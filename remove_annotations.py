'''
This script takes a directory as input and asks the user for each file in the directory whether he/she wants to remove all FrameNet annotations from the HAS_PARTICIPANT relations in this file. 

Usage: python annotation.py <inputdir>
'''

from lxml import etree
import os
import sys

    
argv = sys.argv
if len(sys.argv) < 2:
    print 'Error. Usage: python annotation.py <inputdir>'
else:
    for filename in os.listdir(sys.argv[1]):
        print "\n", filename
        to_annotate = raw_input("Do you want to remove the annotations of this file? (enter 'y' or press Enter to continue) ")
        if to_annotate != "y":
            continue
        else:
            print "\n"   
            # Open CAT XML file and get relevant information
            full_filename = os.path.join(sys.argv[1], filename)
            infile = open(full_filename, "r")
            raw = infile.read()
            root = etree.XML(raw)                   
            relations = root.find("Relations")
            list_hprel = relations.findall("HAS_PARTICIPANT")
            for hprel in list_hprel:
                hprel.set("frame", "")
                hprel.set("frame_element", "")
            outfile = open(full_filename, "w")
            xmlstr = etree.tostring(root)
            outfile.write(xmlstr)
            
            outfile.close()  
            infile.close()





