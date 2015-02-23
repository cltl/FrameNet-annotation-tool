"""
Usage: python annotation.py <inputdir> 

This module takes all the CAT XML files in a given directoy as input and allows the user to annotate the HAS_PARTICIPANT relations with frames and frame elements from FrameNet.

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


def get_framenet_data(pm, frames_LUs, lemma):
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

def get_frame_elements(fn_dir, list_frames):
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
                definition = (root.find("{http://framenet.icsi.berkeley.edu}definition")).text
                definition = re.sub("<[^>]*>", "", definition) # Removes tags
                dir_frames[frame].append(definition)
                fes = root.findall("{http://framenet.icsi.berkeley.edu}FE")
                for fe in fes:
                    name_fe = fe.get("name")
                    def_fe = (fe.find("{http://framenet.icsi.berkeley.edu}definition")).text
                    def_fe = re.sub("<[^>]*>", "", def_fe)
                    dir_frames[frame].append(name_fe)
                infile.close()
        if len(dir_frames[frame]) == 0:
            dir_frames[frame] = ["No definition available", "None"]
    return dir_frames

def get_definition_fe(fn_dir, frame, fe):
    for filename in os.listdir(fn_dir):
        if filename.replace(".xml", "") == frame:
            infile = open(os.path.join(fn_dir, filename), 'r')
            raw = infile.read()
            root = etree.XML(raw)
            for fe_element in root.findall("{http://framenet.icsi.berkeley.edu}FE"):
                if fe_element.get("name") == fe:
                    definition = (fe_element.find("{http://framenet.icsi.berkeley.edu}definition")).text
                    definition = definition.split("<fex")[0] # Removes any examples from the definition
                    definition = definition.split("<ex")[0] # Removes any examples from the definition
                    definition = re.sub("<[^>]*>", "", definition) # Removes markup language
    return definition

##########################
# Functions for printing #
##########################

def print_sentence(sentence, predicate, argument):
    print "SENTENCE: " + sentence 
    print "PREDICATE: " + predicate 
    print "ARGUMENT: " + argument + "\n"

def print_annotation(frame, role):
    print "\n----------------------------- ANNOTATION -----------------------------\n"
    if frame == "None":
        print "NO FRAME IS SELECTED. SAVE THE 'NONE' VALUES AND CONTINUE, OR TRY AGAIN.\n"
    print "FRAME:", frame
    if role != "None":
        def_role = get_definition_fe(fn_dir, frame, role)
        print "ROLE:", role, "--", def_role 
    else:
        print "ROLE:", role

def print_emptylines():
    print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"

############################
# Functions for user input #
############################

def search_first_attempt():
    lemmas_or_frame = raw_input("PLEASE ENTER THE LEMMA(S) EXPRESSING OR RELATING TO THE PREDICATE TO SEARCH FOR FRAMES, OR ENTER THE FRAME DIRECTLY: ")
           
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
            frames_lemma = get_framenet_data(pm, frames_LUs, lemma)
            for frame in frames_lemma:
                all_frames.append(frame)
                
    dict_frames = get_frame_elements(fn_dir, all_frames)
    return all_frames, dict_frames

def no_data_found():
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
                    frames_lemma = get_framenet_data(pm, frames_LUs, lemma)
                    for frame in frames_lemma:
                        all_frames.append(frame)
                
            dict_frames = get_frame_elements(fn_dir, all_frames)
            if len(dict_frames) == 0:
                continue
            else:
                return all_frames, dict_frames  

def too_many_frames(dict_frames, list_frames):
    new_frames = {}	
    print "\nTHERE ARE", len(dict_frames), "FRAMES AVAILABLE. MAKE A SELECTION OF FRAMES FIRST."
    for number, frame in enumerate(list_frames):
        print number, frame
    while True:
        number_frames = raw_input("\nHOW MUCH FRAMES DO YOU WANT TO SHOW? ")
        try:
            n = 0
            while n < int(number_frames):
                n += 1
                while True:
                    entered_number = raw_input("\nPLEASE ENTER THE NUMBER OF THE FRAME YOU WANT TO SHOW: ")
                    try:
                        for number, frame in enumerate(list_frames):
                            if number == int(entered_number):
                                new_frames[frame] = dict_frames[frame]                        
                    except:
                        print "\nSORRY, YOUR INPUT WAS NOT CORRECT."
                        continue
                    else:
                        break                   
        except:
            print "\nSORRY, YOUR INPUT WAS NOT CORRECT."
            continue
        else:
            break
    return new_frames

def select_good_frames(dict_frames, sentence, predicate, argument):
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

############################
# Functions for annotation #
############################


def annotation(filename, annotation_round):
    '''
    Presents a user with a sentence, predicate and argument and let him/her annotate the frame and frame element for this predicate-argument relation
    '''

    # Open CAT XML file and get relevant information
    infile = open(filename, "r")
    raw = infile.read()
    root = etree.XML(raw)
    list_tokens = root.findall("token")
    list_hprel = (root.find("Relations")).findall("HAS_PARTICIPANT")
    list_entities = (root.find("Markables")).findall("ENTITY_MENTION")
    list_events = (root.find("Markables")).findall("EVENT_MENTION")

    for hprel in list_hprel:
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
            print "Error: There seems to be something wrong with the existing annotation. Please check the HAS_PARTICIPANT relation with r_id:", hprel.get("r_id")
            hprel.set("frame", "WrongAnnotation")
            hprel.set("frame_element", "WrongAnnotation")
            continue 

        ########### CHECK IF ANNOTATION ALREADY EXISTS ###########
        # If the relation is already annotated: check with user first (Round 1) or skip to next relation (Round 2)
        if hprel.get("frame") == "None" or hprel.get("frame") == "" or hprel.get("frame_element") == "None" or hprel.get("frame_element") == "":
            to_annotate = "y"
        else:
            if annotation_round == "1":
                print_emptylines()
                print "----------------------- NEW RELATION  -----------------------\n"   
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
            frame, role = user_input(sentence, predicate, argument)

            ########### FINAL CHECK ########### 
            while True:                      
                print_emptylines()
                print "---------------------------- FINAL CHECK -----------------------------\n"
                print_sentence(sentence, predicate, argument)
                print_annotation(frame, role)
                check = raw_input("\nRETRY THIS ANNOTATION (r), SAVE AND CONTINUE WITH THE NEXT (c), OR SAVE AND QUIT ANNOTATING THIS FILE (q)? ")
                if check == "r":
                    user_input(sentence, predicate, argument)
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
    print_emptylines()
    print "----------------------- NEW RELATION  -----------------------\n" 
    print_sentence(sentence, predicate, argument)   
            
    ########### STEP 1: ###########
    # enter the frame, or enter lemma(s) and search for matching frames
    print "-------------------------------------------------------------\n"
    list_frames, dict_frames = search_first_attempt()

    ########### STEP 2(a): ###########
    # if no frames available, try again or quit with 'q' ('None' is filled in for frame and role)
    if len(dict_frames) == 0:
        #print "-------------------------------------------------------------\n"
        list_frames, dict_frames = no_data_found()
        if len(dict_frames) == 0:
            best_frame = "None"
            chosen_role = "None"
                           
    ########### STEP 2(b): ###########
    # if too many frames are available (>10), make a first selection of frames   
    if len(dict_frames) > 10:
        dict_frames = too_many_frames(dict_frames, list_frames)
                            
    ########### STEP 2(c): ###########
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
                annotation_round = raw_input("Enter 1 (all relations) or 2 (empty relations) if you want to annotate this file, or press Enter to continue) ")
                if annotation_round == "1" or annotation_round == "2":
                    full_filename = os.path.join(sys.argv[1], filename)
                    annotation(full_filename, annotation_round)               
                else:
                    continue

if __name__ == '__main__':
    main()
