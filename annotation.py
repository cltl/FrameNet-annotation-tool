"""
Usage: python annotation.py <inputdir> 

This module takes all the CAT XML files in a given directoy as input
and allows the user to annotate the HAS_PARTICIPANT relations in these
files with frames and frame elements from FrameNet.

"""


################################################################################################################
# Optionally define directories of the Predicate Matrix, the FrameNet frame files and the Frames-LUs file here #
################################################################################################################

pm = "./Resources/PredicateMatrix/PredicateMatrix_nl_withESO.v0.2.role.3.txt"
fn_dir = "./Resources/Frames"
frames_LUs = "./Resources/Frames-LUs.txt"

##################
# Import modules #
##################

from lxml import etree
import os
import re
import sys
import csv
from shutil import copyfile
from datetime import datetime

#############################################################################################
# Functions for getting information from input files (CAT XML, Predicate Matrix and Frames) #
#############################################################################################

def get_text_predicate(pred_id, list_events, list_tokens):
    '''
    Returns the full text of a predicate given its id 
    '''
    predicate = ""
    for event in list_events:
        if (event.get("id") or event.get("m_id")) == pred_id:
            event_tokens = event.findall("token_anchor")
            for event_token in event_tokens:
                for token in list_tokens:
                    if (token.get("id") or token.get("t_id")) == (event_token.get("id") or event_token.get("t_id")):
                        word = token.text + " "
                        predicate = predicate + word
    return predicate

def get_text_argument(arg_id, list_entities, list_tokens):
    '''
    Returns the full text of a argument given its id 
    '''
    argument = ""
    for entity in list_entities:
        if (entity.get("id") or entity.get("m_id")) == arg_id:
            entity_tokens = entity.findall("token_anchor")
            for entity_token in entity_tokens:
                for token in list_tokens:
                    if (token.get("id") or token.get("t_id")) == (entity_token.get("id") or entity_token.get("t_id")):
                        word = token.text + " "
                        argument = argument + word
    return argument

def get_sent_id(pred_id, list_events, list_tokens):
    '''
    Returns the id of the sentence of a predicate given the predicate id
    '''
    for event in list_events:
        if (event.get("id") or event.get("m_id")) == pred_id:
            first_word = event.findall("token_anchor")[0]
    for token in list_tokens:
        if (token.get("id") or token.get("t_id")) == (first_word.get("id") or first_word.get("t_id")):
            sent_id = token.get("sentence")
            break
    return sent_id
        
        
def get_full_sentence(sent_id, list_tokens):
    '''
    Returns the full text of a sentence given its id 
    '''
    sentence = ""
    for token in list_tokens:
        if token.get("sentence") == sent_id:
            word = token.text + " "
            sentence = sentence + word
    return sentence


def get_framenet_data(lemma):
    '''
    Returns a list of frames associated with a given lemma in the Predicate Matrix and in FrameNet
    '''
    frames = []
    # Use the Predicate Matrix to search for frames
    pm_infile = open(pm, "r")
    lu_lemma = "lu-lemma:" + lemma # Dutch lemma
    vn_lemma = "vn-lemma:" + lemma # English lemma (VerbNet)
    fn_entry = "fn-entry:" + lemma # English lemma (FrameNet)
    pb_sense = "pb-sense:" + lemma # English lemma (PropBank)
    for line in pm_infile.readlines():
        columns = line.split()
        if (lu_lemma in columns) or (vn_lemma in columns) or (fn_entry in columns) or (pb_sense in columns):
            for column in columns[2:-1]:
                if column.startswith("fn:"):
                    frame = column.lstrip("fn:")
                    if frame not in frames:
                        frames.append(frame)
    # Use the Frame-LUs file to search for frames
    LUs_infile = open(frames_LUs, "r")
    for line in LUs_infile.readlines():
        columns = line.split()
        if lemma in columns[1:]:
            frame = columns[0]
            if frame not in frames:
                frames.append(frame)
    LUs_infile.close()
    pm_infile.close()
    return frames

def get_frame_elements(list_frames):
    '''
    Takes a list of frames, reads the FrameNet Data and returns a dictionary with for each frame:
    - the definition of the frame (first argument)
    - the frame elements (all other arguments)
    '''
    dir_frames = {}
    for frame in list_frames:
        dir_frames[frame] = []
        for filename in os.listdir(fn_dir):
            if filename.replace(".xml", "") == frame:
                infile = open(os.path.join(fn_dir, filename), 'r')
                raw = infile.read().encode("utf8")
                root = etree.XML(raw)
                definition = (root.find("{http://framenet.icsi.berkeley.edu}definition")).text # Requires name space
                definition = re.sub("<[^>]*>", "", definition) # Removes markup language
                dir_frames[frame].append(definition)
                fes = root.findall("{http://framenet.icsi.berkeley.edu}FE") # Requires name space
                for fe in fes:
                    name_fe = fe.get("name")
                    def_fe = (fe.find("{http://framenet.icsi.berkeley.edu}definition")).text # Requires name space
                    def_fe = re.sub("<[^>]*>", "", def_fe)
                    dir_frames[frame].append(name_fe)
                infile.close()
        if len(dir_frames[frame]) == 0:
            dir_frames[frame] = ["No definition available", "None"]
    return dir_frames

def get_definition_fe(frame, fe):
    '''
    Returns the definition of a frame element (FE) given the name of the frame and the FE itself
    '''
    for filename in os.listdir(fn_dir):
        if filename.replace(".xml", "") == frame:
            infile = open(os.path.join(fn_dir, filename), 'r')
            raw = infile.read().encode("utf8")
            root = etree.XML(raw)
            for fe_element in root.findall("{http://framenet.icsi.berkeley.edu}FE"):
                if fe_element.get("name") == fe:
                    definition = (fe_element.find("{http://framenet.icsi.berkeley.edu}definition")).text # Requires name space
                    definition = definition.split("<fex")[0] # Removes any examples from the definition
                    definition = definition.split("<ex")[0] # Removes any examples from the definition
                    definition = re.sub("<[^>]*>", "", definition) # Removes markup language
                    definition = definition.rstrip("\n") # Removes lines at the end
    return definition

##########################
# Functions for printing #
##########################

def print_sentence(sentence, predicate, argument):
    '''
    Prints the sentence, predicate and argument
    '''
    print("SENTENCE: " + sentence)
    print("PREDICATE: " + predicate)
    print("ARGUMENT: " + argument + "\n")

def print_explanation_search():
    print("There are three options: \n"
          "(1) Enter a frame using capitals and underscores (e.g. Attack or Make_possible_to_do).\n"
          "(2) Enter one or multiple lemmas by using lowercase and commas (without spaces) to separate multiple lemmas "
          "(e.g. praten,talk).\n"
          "(3) Enter Metaphor if the predicate is a productive metaphor.\n"
          "(4) Enter WrongRelation if there is something wrong with the relation.\n\n")

def print_annotation(frame, role):
    '''
    Prints the annotated frame and role
    '''
    print("\n----------------------------- ANNOTATION -----------------------------\n")
    if frame == "None":
        print("NO FRAME IS SELECTED. SAVE THE 'NONE' VALUES AND CONTINUE, OR TRY AGAIN.\n")
    print("FRAME:", frame)
    if role != "None" and role != "WrongRelation" and role != "Metaphor":
        def_role = get_definition_fe(frame, role)
        print("ROLE:", role, "--", def_role )
    else:
        print("ROLE:", role)

def print_emptylines():
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

######################################################################################################
# Functions for user input:                                                                          # 
# These functions present the user with the information (e.g. the sentence, the frames found for a   #
# lemma, etc.) and asks him/her to enter the lemma, the correct frame and the correct frame element. #                            
######################################################################################################

def search_frames():
    '''
    Step 1: Enter a frame or lemma(s).
    Asks the user to enter a frame or lemma(s) and returns:
    1. a list of frames associated with the lemma(s)
    2. a dictionary with the definition and frame elements (FEs) for each frame (i.e. {frame1: [definition, FE1, FE2, etc.], frame2: [definition, FE1, FE2, etc.]} )
    '''
    lemmas_or_frame = input("PLEASE ENTER THE LEMMA(S) OR THE FRAME: ")

    # If there is something wrong with the original annotation of the relation, return WrongRelation
    if lemmas_or_frame == "WrongRelation":
        all_frames = "WrongRelation"
        dict_frames = {}
        return all_frames, dict_frames

    # If the predicate is a productive metaphor, return Metaphor
    if lemmas_or_frame == "Metaphor":
        all_frames = "Metaphor"
        dict_frames = {}
        return all_frames, dict_frames
         
    # If no frame/lemma(s) given, return empty frames + dictionary
    if lemmas_or_frame == "":
        all_frames = []
        dict_frames = {}
        return all_frames, dict_frames
    
    #If frame is given (starts with capital), create list + dictionary of given frame
    if not lemmas_or_frame.islower():                   
        framefilename = lemmas_or_frame + ".xml"
        if framefilename not in os.listdir(fn_dir):   # If no frames found, return empty list + dictionary of frames
            all_frames = []
            dict_frames = {}
            return all_frames, dict_frames
        else: 
            all_frames = [lemmas_or_frame]

    # If lemma(s) is/are given, search for frames and return dictionary
    else:
        lemmas =  lemmas_or_frame.split(",")            
        all_frames = []
        for lemma in lemmas:
            frames_lemma = get_framenet_data(lemma)
            for frame in frames_lemma:
                all_frames.append(frame)
                
    dict_frames = get_frame_elements(all_frames)
    return all_frames, dict_frames

def search_frames_again():
    '''
    Step 1: Enter a frame or lemma(s).
    If in the first try no frames were found , this function asks the user again to enter a frame or lemma(s) and returns:
    1. a list of frames associated with the lemma(s)
    2. a dictionary with the definition and frame elements (FEs) for each frame (i.e. {frame1: [definition, FE1, FE2, etc.], frame2: [definition, FE1, FE2, etc.]} )
    '''
    while True:
        lemmas_or_frame = input("NO DATA FOUND. PLEASE TRY AGAIN (OR ENTER 'q' TO QUIT THIS ANNOTATION): ")
        if lemmas_or_frame == "q":
            print("YOU HAVE CHOSEN TO QUIT THIS ANNOTATION. PLEASE CONTINUE WITH THE NEXT.")
            list_frames = []
            dict_frames = {}
            return list_frames, dict_frames
        else:
            #If frame is given (starts with capital), create list + dictionary of given frame
            if not lemmas_or_frame.islower():                   
                framefilename = lemmas_or_frame + ".xml"
                if framefilename not in os.listdir(fn_dir):   # If no frames found, return empty list + dictionary of frames
                    continue
                else: 
                    all_frames = [lemmas_or_frame]

            # If lemma(s) is/are given, search for frames and return dictionary
            else:
                lemmas =  lemmas_or_frame.split(",")            
                all_frames = []
                for lemma in lemmas:
                    frames_lemma = get_framenet_data(lemma)
                    for frame in frames_lemma:
                        all_frames.append(frame)
                
            dict_frames = get_frame_elements(all_frames)
            if len(dict_frames) == 0:
                continue
            else:
                return all_frames, dict_frames  

def too_many_frames(dict_frames, list_frames):
    '''
    Presents the user with the names of all the found frames and asks him/her to make a smaller selection of frames first 
    '''
    
    new_frames = {}
    set_frames = set(list_frames)
    print("\nTHERE ARE", len(set_frames), "FRAMES AVAILABLE. MAKE A SMALLER SELECTION OF FRAMES FIRST.")
    for number, frame in enumerate(set_frames):
        print(number, frame)
    while True:
        chosen_frames = input("\nWHICH FRAMES DO YOU WANT TO INVESTIGATE FURTHER? ")
        chosen_frames = chosen_frames.split(",")
        for number, frame in enumerate(set_frames):
            if str(number) in chosen_frames:
                new_frames[frame] = dict_frames[frame]
        if len(new_frames) == 0:
            print("\nSORRY, YOUR INPUT WAS NOT CORRECT. PLEASE TYPE THE NUMBERS OF THE FRAMES SEPARATED BY COMMAS.")
            continue
        else:
            return new_frames

def select_good_frames(dict_frames, sentence, predicate, argument):
    '''
    Presents the user with the frames, one by one, and let him/her decide whether it is a good frame or not.
    Returns a dictionary of frames that were marked as 'good' frames.
    '''
    chosen_frames = {}
    n = 0
    for frame in dict_frames:
        n += 1
        def_frame = dict_frames[frame][0]
        fes = dict_frames[frame][1:-1]
        print_emptylines()
        print("---------------------- ANNOTATION OF FRAME(S) ----------------------\n")
        print_sentence(sentence, predicate, argument)
        print("\n----------------------------- NEW FRAME ----------------------------\n")
        print("FRAME", str(n), "OF", str(len(dict_frames)) + ":", frame, "\n")
        print("DEFINITION:", def_frame, "\n")
            
        yes_or_no = input("IS THIS A GOOD FRAME? (enter 'y', or press Enter to discard): ")
        print("\n")
        if yes_or_no == "y":
            chosen_frames[frame] = dict_frames[frame]
    return chosen_frames

def multiple_frames_chosen(chosen_frames):
    '''
    Presents the user with the multiple frames that (s)he has chosen and asks to choose the best-fitting frame
    '''
    print("-------------------------------------------------------------\n")
    print("YOU HAVE CHOSEN MULTIPLE FRAMES: ")
    list_chosen_frames = list(chosen_frames.keys())
    for number, frame in enumerate(list_chosen_frames):
        print(number, frame)
    while True:
        number_best_frame = input("\nPLEASE ENTER THE NUMBER OF THE BEST FRAME: ")
        try:
            best_frame = list_chosen_frames[int(number_best_frame)]
            roles = chosen_frames[best_frame][1:]
            return best_frame, roles
        except:
            print("SORRY, YOUR INPUT WAS NOT CORRECT.")
            continue
        else:
            break

def enter_frame_element(best_frame, roles):
    '''
    Presents the user with the frame elements (FEs) of the frame and asks to select the correct FE
    '''
    chosen_roles = []
    print("----------------------------------------------------------------")
    print("\nYOU HAVE CHOSEN: " , best_frame , "\n\nTHE POSSIBLE ROLES FOR THIS FRAME ARE:")
    for number, role in enumerate(roles):
        print(number, role)
    print("\n(enter multiple roles if you want to compare some definitions first)")
    while True:
        chosen_numbers = input("PLEASE ENTER THE NUMBER OF THE ROLE OF THE ARGUMENT: ")
        chosen_numbers = chosen_numbers.split(",")
        try:
            for chosen_number in chosen_numbers:
                chosen_role = roles[int(chosen_number)]
                chosen_roles.append(chosen_role)
            return chosen_roles
        except:
            print("SORRY, YOUR INPUT WAS NOT CORRECT.")
            continue
        else:
            break


def multiple_fes_chosen(frame,fes):
    '''
    Presents the user with the definitions of the multiple roles that (s)he has chosen and asks to choose the correct one
    '''
    print("-------------------------------------------------------------\n")
    print("YOU HAVE CHOSEN MULTIPLE ROLES. THESE ARE THE DEFINITIONS: \n")
    for number, fe in enumerate(fes):
        definition = get_definition_fe(frame, fe)
        print(number, fe, "\n", definition, "\n")
    while True:
        number_fe = input("\nPLEASE ENTER THE NUMBER OF THE CORRECT ROLE: ")
        try:
            for number, fe in enumerate(fes):
                print(number, fe, number_fe)
                if str(number) == number_fe:
                    return fe
        except:
            print("SORRY, YOUR INPUT WAS NOT CORRECT.")
            continue
        else:
            break


def get_confidence_scores(frame):
    '''
    Asks the user to indicate how confident he/she is about the annotation.
    '''
    if not frame in ["None", "Metaphor", "WrongRelation"]:
        print("\nHOW CONFIDENT ARE YOU ABOUT THE ANNOTATION OF THIS FRAME?\n"
              "3 - This frame fits the context very well.\n"
              "2 - This frame seemed the best fit, but other frames could also apply.\n"
              "1 - This frame does not fit completely, but there was no better frame available.\n")
        confidence_frame = input("ENTER YOUR FRAME CONFIDENCE SCORE: ")
        print("\nHOW CONFIDENT ARE YOU ABOUT THE ANNOTATION OF THIS ROLE? ENTER YOUR CONFIDENCE SCORE.\n"
              "3 - This role fits the context very well.\n"
              "2 - This role seemed the best fit, but other roles could also apply.\n"
              "1 - This role does not fit completely, but there was no better role available.\n")
        confidence_role = input("ENTER YOUR ROLE CONFIDENCE SCORE: ")
    else:
        confidence_frame = "0"
        confidence_role = "0"
    return confidence_frame, confidence_role


###################################################################################
# Functions for overall annotation process:                                       #
# The 'annotation' function includes the several steps of the annotation process: #
# 1. Find information and check requirements:                                     #
#       - Extract the relations from the CAT XML files                            #
#       - Get sentence, predicate and argument                                    #
#       - Check if relation is correct (predicate and argument present,           #
#         respectively referring to event/entity, etc.)                           #
#       - Check if relation is already annotated (skip or ask user first)         #
# 2. Start the actual annotation (call 'user_input' function)                     #
# 3. Final check: let user check his own annotations and choose to retry,         #
#    continue with next annotation or quit annotating this file                   #
# 3. Write the annotations to new file (call 'write_outfile' function)            #
###################################################################################


def annotation(filename, annotation_round):
    '''
    Takes a CAT XML file as input and presents a user with the sentence, predicate and argument of each HAS_PARTICIPANT relation,
    asks him/her to anotate the frame and frame element for this relation and writes the annotations to a new outputfile.
    '''

    # Create output directory and check if the file has already been annotated (if so, the user is warned)
    outfilename, logfile, continue_overwrite = create_dir_and_outfile(filename, annotation_round)
    if continue_overwrite != "y":
        return
    
    # Open CAT XML file and get relevant information
    infile = open(filename, "r")
    raw = infile.read().encode("utf8")
    root = etree.XML(raw)
    list_tokens = root.findall("token")
    list_hprel = root.find("Relations").findall("HAS_PARTICIPANT")
    list_entities = root.find("Markables").findall("ENTITY_MENTION")
    list_events = root.find("Markables").findall("EVENT_MENTION")

    hprel_number = 0
    for hprel in list_hprel:
        hprel_number += 1

        ########### CHECK IF RELATION IS CORRECT ###########
        # If something is wrong with the annotation of the relation, give id of the relation to user and continue with next relation
        try:
            if "m_id" not in hprel.find("source").attrib:                           # GET PREDICATE (accounted for different attribute names for ids)
                pred_id = hprel.find("source").get("id")
            else:
                pred_id = hprel.find("source").get("m_id")
            predicate = get_text_predicate(pred_id, list_events, list_tokens)
            if "m_id" not in hprel.find("source").attrib:                           # GET ARGUMENT
                arg_id = hprel.find("target").get("id")
            else:
                arg_id = hprel.find("target").get("m_id")
            if "r_id" not in hprel.attrib:
                r_id = hprel.get("id")
            else:
                r_id = hprel.get("r_id")
            argument = get_text_argument(arg_id, list_entities, list_tokens)
            sent_id = get_sent_id(pred_id, list_events, list_tokens)                # GET SENTENCE
            sentence = get_full_sentence(sent_id, list_tokens)
        except:
            print_emptylines()
            print("Error: There seems to be something wrong with the original annotation of this relation. Please check the HAS_PARTICIPANT relation with r_id:", hprel.get("r_id"))
            hprel.set("frame", "WrongRelation")
            hprel.set("frame_element", "WrongRelation")
            continue

        hprel_id = "_".join([os.path.basename(filename), sent_id, r_id])

        ########### CHECK IF ANNOTATION ALREADY EXISTS ###########
        # If the relation is already annotated: check with user first (Round 1) or skip to next relation (Round 2)
        if hprel.get("frame") == "None" or hprel.get("frame") == "" or hprel.get("frame") == "WrongRelation" or "frame" not in hprel.attrib:
            to_annotate = "y"
        else:
            if annotation_round == "1":
                print_emptylines()
                print("----------------------- RELATION", hprel_number, "OF", len(list_hprel), "-----------------------\n")
                print_sentence(sentence,predicate,argument)
                print_annotation(hprel.get("frame"), hprel.get("frame_element"))
                print("\nTHIS RELATION HAS ALREADY BEEN ANNOTATED.")
                to_annotate = input("\nDO YOU WANT TO CORRECT THESE ANNOTATIONS? (enter 'y' or press Enter to continue) ")
            if annotation_round == "2":
                to_annotate = "n"
        if to_annotate != "y":
            continue

        ########### IF REQUIREMENTS ARE MET: START ANNOTATION ###########
        else:
            print_emptylines()
            print("-------------------------- EXPLANATION --------------------------\n")
            print_explanation_search()
            #print "If you already know which frame applies, you can enter the frame directly by using capitals and underscores (e.g. Attack or Make_possible_to_do). If you don't know which frame applies, you can search for frames by entering one or multiple Dutch or English lemma(s) expressing or relating to the predicate, using lowercase only (e.g. praten). Multiple lemmas should be separated by commas without spaces (e.g. praten,talk). Is there something wrong with this relation? Enter 'WrongRelation'.\n"
            print("----------------------- RELATION", hprel_number, "OF", len(list_hprel), "-----------------------\n")
            print_sentence(sentence, predicate, argument)
            if annotation_round == "2":
                if hprel.get("frame") != "":
                    print("----------------------------------------------------------------")
                    print("THIS WAS ANNOTATED AS: ", hprel.get("frame"))
            frame, role = user_input(sentence, predicate, argument, logfile, hprel_id)

            ########### CONFIDENCE SCORE ##########
            print_emptylines()
            print("---------------------------- CONFIDENCE SCORE -----------------------------\n")
            print_sentence(sentence, predicate, argument)
            print_annotation(frame, role)

            ########### FINAL CHECK ##########
            while True:
                print_emptylines()
                print("---------------------------- FINAL CHECK -----------------------------\n")
                print_sentence(sentence, predicate, argument)
                print_annotation(frame, role)
                confidence_frame, confidence_role = get_confidence_scores(frame)
                check = input("\nRETRY THIS ANNOTATION (r), SAVE AND CONTINUE WITH THE NEXT (c), OR SAVE AND QUIT ANNOTATING THIS FILE (q)? ")

                # Retry annotation of current relation
                if check == "r":
                    frame, role = user_input(sentence, predicate, argument, logfile, hprel_id)

                # Save to output file and continue with next relation
                if check == "c":
                    hprel.set("frame", frame)
                    hprel.set("frame_element", role)
                    hprel.set("confidence_frame", confidence_frame)
                    hprel.set("confidence_role", confidence_role)
                    write_outfile(outfilename, root)
                    break

                # Save to output file and quit annotating this file
                if check == "q":
                    hprel.set("frame", frame)
                    hprel.set("frame_element", role)
                    write_outfile(outfilename, root)
                    return

    ########### END OF ANNOTATION ########### 
    infile.close()
    print("\n---------------------- ANNOTATION OF FILE COMPLETE ----------------------\n")

def user_input(sentence, predicate, argument, logfile, hprel_id):
    '''
    Starts the actual annotation of a predicate-argument relation
    '''
            
    ########### STEP 1(a): ###########
    # enter the frame, or enter lemma(s) and search for matching frames
    print("----------------------------------------------------------------\n")
    list_frames, dict_frames = search_frames()

    ########### STEP 1(b): ###########
    # if the user thinks there is something wrong with the original annotation of the relation, 'WrongRelation' is returned for frame and role
    if list_frames == "WrongRelation":
        frame = "WrongRelation"
        role = "WrongRelation"
        return frame, role

    ########### STEP 1(c): ###########
    # if the user labelled the predicate as a productive metaphor, 'Metaphor' is returned for frame and role
    if list_frames == "Metaphor":
        frame = "Metaphor"
        role = "Metaphor"
        return frame, role
        
    ########### STEP 1(d): ###########
    # if no frames available, try again or quit with 'q' ('None' is returned for frame and role)
    if len(dict_frames) == 0:
        list_frames, dict_frames = search_frames_again()
        if len(dict_frames) == 0:
            frame = "None"
            role = "None"
            return frame, role
                          
    ########### STEP 2(a): ###########
    # if too many frames are available (>10), make a first selection of frames   
    if len(dict_frames) > 10:
        dict_frames = too_many_frames(dict_frames, list_frames)
                            
    ########### STEP 2(b): ###########
    # if frames available, decide which frame(s) is/are good frames
    if len(dict_frames) > 0:
        chosen_frames = select_good_frames(dict_frames, sentence, predicate, argument) # returns dictionary
        with open(logfile, "a", newline="") as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=",")
            csvwriter.writerow([hprel_id] + list(chosen_frames.keys()))

        ########### STEP 3(a): ###########
        # if no frames are chosen, 'None' is filled in for frame and role (user can later choose to try again)
        if len(chosen_frames) < 1:
            frame = "None"
            role = "None"
            return frame, role
                        
        ########### STEP 3(b): ###########
        # if multiple frames are chosen, choose best frame               
        else:            
            if len(chosen_frames) > 1:
                print_emptylines()
                print("---------------------- SELECTION OF BEST FRAME ----------------------\n")
                print_sentence(sentence, predicate, argument)
                best_frame, roles = multiple_frames_chosen(chosen_frames)
                            
            if len(chosen_frames) == 1:
                for best_frame in chosen_frames:
                    roles = chosen_frames[best_frame][1:]      

            ########### STEP 4: ###########
            # enter the frame element (if multiple frame elements are entered, show definitions and choose correct frames)
            print_emptylines()
            print("---------------------- ANNOTATION OF ROLE ----------------------\n")
            print_sentence(sentence, predicate, argument)
            chosen_roles = enter_frame_element(best_frame, roles)

            if len(chosen_roles) == 1:
                return best_frame, chosen_roles[0]            
            
            if len(chosen_roles) > 1:
                print_emptylines()
                print("---------------------- ANNOTATION OF ROLE ----------------------\n")
                print_sentence(sentence, predicate, argument)
                best_role = multiple_fes_chosen(best_frame, chosen_roles)
                return best_frame, best_role
            

def write_outfile(outfilename, root):
    '''
    Writes the resulting XML to the output-file
    '''
    outfile = open(outfilename, "wb")
    xmlstr = etree.tostring(root, pretty_print=True)
    outfile.write(xmlstr)            
    outfile.close()


def create_dir_and_outfile(filename, annotation_round):
    '''
    Creates output directory and file; if output file already exists (and non-annotated file is taken as input),
    the user is asked whether (s)he wants to overwrite the previous annotations
    '''
    inputdir = os.path.split(filename)[0]
    old_filename = os.path.split(filename)[1].split("-fn")[0]
    if "-framenet" not in inputdir:
        outputdir = inputdir + "-framenet"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        old_filename = os.path.split(filename)[1]
        new_filename = old_filename.replace(".txt.xml", "-fn.txt.xml")
        full_newfilename = os.path.join(outputdir, new_filename)
        logfile = os.path.join(outputdir, "log.csv")
    else:
        outputdir = inputdir
        full_newfilename = filename
        logfile = os.path.join(outputdir, "log.csv")
    if "-fn" not in filename:
        if os.path.exists(full_newfilename):
            print("\nWARNING: This file has already been annotated. If you continue, previous annotations will be "
                  "overwritten (but a backup will be created). Please take the annotated file as input if you want to "
                  "continue where you left off last time.")
            continue_overwrite = input("\nDo you want to continue now? (y/n) ")
        else:
            continue_overwrite = "y"

    else:
        continue_overwrite = "y"

    # create backup
    if continue_overwrite == "y" and annotation_round == "1" and "-framenet" in inputdir:
        create_backup(outputdir, filename, full_newfilename)

    return full_newfilename, logfile, continue_overwrite

def create_backup(outputdir, filename, full_newfilename):
    """
    Creates a folder called "backups" and copies the original annotated file as backup
    """
    outputdir_backups = os.path.join(outputdir, "backups")
    if not os.path.exists(outputdir_backups):
        os.makedirs(outputdir_backups)
    backupfile = os.path.basename(filename).split(".txt.xml")[0] + "_" + \
                 datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M') + "-fn.txt.xml"
    copyfile(full_newfilename, os.path.join(outputdir_backups, backupfile))

#################
# Main function #
#################

def main(argv=None):
    if argv is None:
        argv = sys.argv
        if len(argv) < 2:
            print('Error. Usage: python annotation.py <inputdir>')
        if os.path.isfile(argv[1]):
            print('Error. Input should be directory, not file.')
        else:
            for filename in os.listdir(sys.argv[1]):
                if filename.endswith(".xml"):
                    print("\n", filename)
                    annotation_round = input("Enter 1 to annotate all relations in this file, enter 2 to only annotate "
                                             "the empty relations in this file, or press Enter to skip this file: ")
                    if annotation_round == "1" or annotation_round == "2":
                        full_filename = os.path.join(sys.argv[1], filename)
                        annotation(full_filename, annotation_round)
                    else:
                        continue

if __name__ == '__main__':
    main()
