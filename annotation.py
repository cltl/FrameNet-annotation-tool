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

#############################################################################################
# Functions for getting information from input files (CAT XML, Predicate Matrix and Frames) #
#############################################################################################

def get_text_predicate(pred_id, list_events, list_tokens):
    '''
    Returns the full text of a predicate given its id 
    '''
    predicate = ""
    for event in list_events:
        if event.get("m_id") == pred_id:
            event_tokens = event.findall("token_anchor")
            for event_token in event_tokens:
                for token in list_tokens:
                    if token.get("t_id") == event_token.get("t_id"):
                        word = token.text + " "
                        predicate = predicate + word
    return predicate

def get_text_argument(arg_id, list_entities, list_tokens):
    '''
    Returns the full text of a argument given its id 
    '''
    argument = ""
    for entity in list_entities:
        if entity.get("m_id") == arg_id:
            entity_tokens = entity.findall("token_anchor")
            for entity_token in entity_tokens:
                for token in list_tokens:
                    if token.get("t_id") == entity_token.get("t_id"):
                        word = token.text + " "
                        argument = argument + word
    return argument

def get_sent_id(pred_id, list_events, list_tokens):
    '''
    Returns the id of the sentence of a predicate given the predicate id
    '''
    for event in list_events:
        if event.get("m_id") == pred_id:
            first_word = event.findall("token_anchor")[0]
    for token in list_tokens:
        if token.get("t_id") == first_word.get("t_id"):
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
                raw = infile.read()
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
            raw = infile.read()
            root = etree.XML(raw)
            for fe_element in root.findall("{http://framenet.icsi.berkeley.edu}FE"):
                if fe_element.get("name") == fe:
                    definition = (fe_element.find("{http://framenet.icsi.berkeley.edu}definition")).text # Requires name space
                    definition = definition.split("<fex")[0] # Removes any examples from the definition
                    definition = definition.split("<ex")[0] # Removes any examples from the definition
                    definition = re.sub("<[^>]*>", "", definition) # Removes markup language
    return definition

##########################
# Functions for printing #
##########################

def print_sentence(sentence, predicate, argument):
    '''
    Prints the sentence, predicate and argument
    '''
    print "SENTENCE: " + sentence 
    print "PREDICATE: " + predicate 
    print "ARGUMENT: " + argument + "\n"

def print_explanation_search():
    print "There are three options:"
    print "(1) Enter a frame using capitals and underscores (e.g. Attack or Make_possible_to_do)."
    print "(2) Enter one or multiple lemmas by using lowercase and commas (without spaces) to separate multiple lemmas (e.g. praten,talk)."
    print "(3) Enter WrongRelation if there is something wrong with the relation.\n\n"

def print_annotation(frame, role):
    '''
    Prints the annotated frame and role
    '''
    print "\n----------------------------- ANNOTATION -----------------------------\n"
    if frame == "None":
        print "NO FRAME IS SELECTED. SAVE THE 'NONE' VALUES AND CONTINUE, OR TRY AGAIN.\n"
    print "FRAME:", frame
    if role != "None" and role != "WrongRelation":
        def_role = get_definition_fe(frame, role)
        print "ROLE:", role, "--", def_role 
    else:
        print "ROLE:", role

def print_emptylines():
    print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"

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
    lemmas_or_frame = raw_input("PLEASE ENTER THE LEMMA(S) OR THE FRAME: ")

    # If there is something wrong with the original annotation of the relation, return WrongRelation
    if lemmas_or_frame == "WrongRelation":
        all_frames = "WrongRelation"
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
        lemmas_or_frame = raw_input("NO DATA FOUND. PLEASE TRY AGAIN (OR ENTER 'q' TO QUIT THIS ANNOTATION): ")
        if lemmas_or_frame == "q":
            print "YOU HAVE CHOSEN TO QUIT THIS ANNOTATION. PLEASE CONTINUE WITH THE NEXT."
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
    print "\nTHERE ARE", len(list_frames), "FRAMES AVAILABLE. MAKE A SMALLER SELECTION OF FRAMES FIRST."
    for number, frame in enumerate(list_frames):
        print number, frame
    while True:
        chosen_frames = raw_input("\nWHICH FRAMES DO YOU WANT TO INVESTIGATE FURTHER? ")
        chosen_frames = chosen_frames.split(",")
        for number, frame in enumerate(list_frames):
            if str(number) in chosen_frames:
                new_frames[frame] = dict_frames[frame]
        if len(new_frames) == 0:
            print "\nSORRY, YOUR INPUT WAS NOT CORRECT. PLEASE TYPE THE NUMBERS OF THE FRAMES SEPARATED BY COMMAS."
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
        print "---------------------- ANNOTATION OF FRAME(S) ----------------------\n"
        print_sentence(sentence, predicate, argument)
        print "\n----------------------------- NEW FRAME ----------------------------\n"
        print "FRAME", str(n), "OF", str(len(dict_frames)) + ":", frame, "\n"
        print "DEFINITION:", def_frame, "\n"
            
        yes_or_no = raw_input("IS THIS A GOOD FRAME? (enter 'y', or press Enter to discard): ")
        print "\n"
        if yes_or_no == "y":
            chosen_frames[frame] = dict_frames[frame]
    return chosen_frames

def multiple_frames_chosen(chosen_frames):
    '''
    Presents the user with the multiple frames that (s)he has chosen and asks to choose the best-fitting frame
    '''
    print "-------------------------------------------------------------\n"
    print "YOU HAVE CHOSEN MULTIPLE FRAMES: "
    list_chosen_frames = list(chosen_frames.keys())
    for number, frame in enumerate(list_chosen_frames):
        print number, frame
    while True:
        number_best_frame = raw_input("\nPLEASE ENTER THE NUMBER OF THE BEST FRAME: ")
        try:
            best_frame = list_chosen_frames[int(number_best_frame)]
            roles = chosen_frames[best_frame][1:]
            return best_frame, roles
        except:
            print "SORRY, YOUR INPUT WAS NOT CORRECT."
            continue
        else:
            break

def enter_frame_element(best_frame, roles):
    '''
    Presents the user with the frame elements (FEs) of the frame and asks to select the correct FE
    '''
    print "----------------------------------------------------------------"
    print "\nYOU HAVE CHOSEN: " , best_frame , "\n\nTHE POSSIBLE ROLES FOR THIS FRAME ARE:"
    for number, role in enumerate(roles):
        print number, role
    while True:
        chosen_number = raw_input("\nPLEASE ENTER THE NUMBER OF THE ROLE OF THE ARGUMENT: ")
        try:
            chosen_role = roles[int(chosen_number)]
            return chosen_role
        except:
            print "SORRY, YOUR INPUT WAS NOT CORRECT."
            continue
        else:
            break

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

    # Open CAT XML file and get relevant information
    infile = open(filename, "r")
    raw = infile.read()
    root = etree.XML(raw)
    list_tokens = root.findall("token")
    list_hprel = (root.find("Relations")).findall("HAS_PARTICIPANT")
    list_entities = (root.find("Markables")).findall("ENTITY_MENTION")
    list_events = (root.find("Markables")).findall("EVENT_MENTION")

    hprel_number = 0
    for hprel in list_hprel:
        hprel_number += 1
        
        ########### CHECK IF RELATION IS CORRECT ###########
        # If something is wrong with the annotation of the relation, give id of the relation to user and continue with next relation
        try:
            pred_id = hprel.find("source").get("m_id")                              # GET PREDICATE
            predicate = get_text_predicate(pred_id, list_events, list_tokens)
            arg_id = hprel.find("target").get("m_id")                               # GET ARGUMENT
            argument = get_text_argument(arg_id, list_entities, list_tokens)
            sent_id = get_sent_id(pred_id, list_events, list_tokens)                # GET SENTENCE
            sentence = get_full_sentence(sent_id, list_tokens)
        except:            
            print_emptylines()
            print "Error: There seems to be something wrong with the original annotation of this relation. Please check the HAS_PARTICIPANT relation with r_id:", hprel.get("r_id")
            hprel.set("frame", "WrongRelation")
            hprel.set("frame_element", "WrongRelation")
            continue 

        ########### CHECK IF ANNOTATION ALREADY EXISTS ###########
        # If the relation is already annotated: check with user first (Round 1) or skip to next relation (Round 2)
        if hprel.get("frame") == "None" or hprel.get("frame") == "" or hprel.get("frame_element") == "None" or hprel.get("frame_element") == "":
            to_annotate = "y"
        else:
            if annotation_round == "1":
                print_emptylines()
                print "----------------------- RELATION", hprel_number, "OF", len(list_hprel), "-----------------------\n"   
                print "THIS RELATION HAS ALREADY BEEN ANNOTATED:"
                print_sentence(sentence,predicate,argument)
                print_annotation(hprel.get("frame"), hprel.get("frame_element"))
                to_annotate = raw_input("\nDO YOU WANT TO ANNOTATE THIS RELATION? (enter 'y' or press Enter to continue) ")
            if annotation_round == "2":
                to_annotate = "n"
        if to_annotate != "y":
            continue

        ########### IF REQUIREMENTS ARE MET: START ANNOTATION ###########  
        else:
            print_emptylines()
            print "-------------------------- EXPLANATION --------------------------\n"
            print_explanation_search()
            #print "If you already know which frame applies, you can enter the frame directly by using capitals and underscores (e.g. Attack or Make_possible_to_do). If you don't know which frame applies, you can search for frames by entering one or multiple Dutch or English lemma(s) expressing or relating to the predicate, using lowercase only (e.g. praten). Multiple lemmas should be separated by commas without spaces (e.g. praten,talk). Is there something wrong with this relation? Enter 'WrongRelation'.\n"
            print "----------------------- RELATION", hprel_number, "OF", len(list_hprel), "-----------------------\n" 
            print_sentence(sentence, predicate, argument) 
            frame, role = user_input(sentence, predicate, argument)

            ########### FINAL CHECK ########### 
            while True:                      
                print_emptylines()
                print "---------------------------- FINAL CHECK -----------------------------\n"
                print_sentence(sentence, predicate, argument)
                print_annotation(frame, role)
                check = raw_input("\nRETRY THIS ANNOTATION (r), SAVE AND CONTINUE WITH THE NEXT (c), OR SAVE AND QUIT ANNOTATING THIS FILE (q)? ")
                if check == "r":
                    frame, role = user_input(sentence, predicate, argument)
                if check == "c":
                    hprel.set("frame", frame)
                    hprel.set("frame_element", role)
                    break
                if check == "q":
                    hprel.set("frame", frame)
                    hprel.set("frame_element", role)
                    write_outfile(filename, root, annotation_round)
                    return             

    ########### END OF ANNOTATION: WRITE RESULT TO OUTPUTFILE ########### 
    write_outfile(filename, root, annotation_round)
    infile.close()
    print "\n---------------------- ANNOTATION OF FILE COMPLETE ----------------------\n"

def user_input(sentence, predicate, argument):
    '''
    Starts the actual annotation of a predicate-argument relation
    '''
            
    ########### STEP 1(a): ###########
    # enter the frame, or enter lemma(s) and search for matching frames
    print "----------------------------------------------------------------\n"
    list_frames, dict_frames = search_frames()

    ########### STEP 1(b): ###########
    # if the user thinks there is something wrong with the original annotation of the relation, 'WrongRelation' is returned for frame and role
    if list_frames == "WrongRelation":
        frame = "WrongRelation"
        role = "WrongRelation"
        return frame, role
        
    ########### STEP 1(c): ###########
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
        chosen_frames = select_good_frames(dict_frames, sentence, predicate, argument)

        ########### STEP 3(a): ###########
        # if no frames are chosen, 'None' is filled in for frame and role (user can later choose to try again)
        if len(chosen_frames) < 1:
            best_frame = "None"
            chosen_role = "None"
                        
        ########### STEP 3(b): ###########
        # if multiple frames are chosen, choose best frame (roles are selected for this frame)                
        else:            
            if len(chosen_frames) > 1:
                print_emptylines()
                print "---------------------- SELECTION OF BEST FRAME ----------------------\n"
                print_sentence(sentence, predicate, argument)
                best_frame, roles = multiple_frames_chosen(chosen_frames)
                            
            if len(chosen_frames) == 1:
                for best_frame in chosen_frames:
                    roles = chosen_frames[best_frame][1:]      

            ########### STEP 4: ###########
            # enter the frame element
            print_emptylines()
            print "---------------------- ANNOTATION OF ROLE ----------------------\n"
            print_sentence(sentence, predicate, argument)
            chosen_role = enter_frame_element(best_frame, roles)

        return best_frame, chosen_role

def write_outfile(filename, root, annotation_round):
    '''
    Writes the resulting XML to a new outputfile in a separate directory
    '''
    inputdir = os.path.split(filename)[0]
    old_filename = os.path.split(filename)[1]
    outputdir = inputdir + "-framenet"
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    if annotation_round == "1":
        new_filename = old_filename.replace(".txt.xml", "-fn1.txt.xml")
        full_newfilename = os.path.join(outputdir, new_filename)
    if annotation_round == "2":
        new_filename = old_filename.replace(".txt.xml", "-fn2.txt.xml")
        full_newfilename = os.path.join(outputdir, new_filename)
    outfile = open(full_newfilename, "w")
    xmlstr = etree.tostring(root)
    outfile.write(xmlstr)            
    outfile.close() 

#################
# Main function #
#################

def main(argv=None):
    if argv is None:
        argv = sys.argv
        if len(argv) < 2:
            print 'Error. Usage: python annotation.py <inputdir>'
        if os.path.isfile(argv[1]):
            print 'Error. Input should be directory, not file.'
        else:
            for filename in os.listdir(sys.argv[1]):
                print "\n", filename
                annotation_round = raw_input("Enter 1 to annotate all relations in this file, enter 2 to only annotate the empty relations in this file, or press Enter to skip this file: ")
                if annotation_round == "1" or annotation_round == "2":
                    full_filename = os.path.join(sys.argv[1], filename)
                    annotation(full_filename, annotation_round)               
                else:
                    continue

if __name__ == '__main__':
    main()
