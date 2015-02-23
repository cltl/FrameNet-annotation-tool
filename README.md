###Summary###

This module allows a user to annotate all CAT XML files in a given directory with frames and frame elements from FrameNet. The user can search for the frames and frame elements in FrameNet and the Predicate Matrix.

Usage: 		python annotation.py \<inputdir\> \<round [1 or 2]\>

Example: 	python annotation.py ./Data/Example 1 

###Requirements###
The input files have to be in labeled CAT (acronym for CELCT/Content Annotation Tool) XML format (see [CAT Annotation Tool](https://dh.fbk.eu/resources/cat-content-annotation-tool) and already have been annotated with HAS\_PARTICIPANT relations according to the NewsReader annotation scheme (see [NewsReader's project website](http://www.newsreader-project.eu/)).

The script uses the following resources, which are included in this module:
- Predicate Matrix (English-Dutch version, including English and Dutch lemmas)
- The Frame files of the XML version of FrameNet (version 1.5)
- A separate file with the lexical units listed for each Frame (extracted from FrameNet version 1.5)

###Description###
There are two annotation rounds:

1. **All relations:** annotate all HAS_PARTICIPANT relations; if annotations for a relation already exist, the user is asked whether (s)he wants to change the existing annotation
2. **Empty relations:** annotate only the HAS_PARTICIPANT relations where there is no frame and/or role specified yet 

######1. Enter a frame or lemma######
The user is presented with the sentence, predicate and argument. If the user already knows which frame applies, (s)he can enter the frame directly by using capitals and underscores (e.g. **Attack**, **Make\_possible\_to\_do**). If the user does not know which frame applies, (s)he can enter one or multiple Dutch or English lemma(s) expressing or relating to the predicate by using lowercase only (e.g. **praten**). Multiple lemmas can be separated by commas without spaces ***praten,talk**). The user is then presented with the frames, definitions and roles that are associated with the lemma(s) in the Predicate Matrix & FrameNet. 

Some guidelines:
- You can search for both nouns and verbs, but it is more likely to get results for verbs. So if possible, try to convert nominal predicates into verbal predicates (analysis --- analyse).
- If the predicate is too specific/vague, try to think of another word that expresses the same or a more general concept (e.g. take steps --- do).
- If the predicate is a complex expression (multi-word expression, idioms), try to think of another word that expresses the same concept (e.g. for sale --> sell, to be/come under fire --- criticize).
- English phrasal verbs can be entered by separating the words by an underscore (e.g. go\_on).


######2. Annotation of frame######
- Be critical!! Rather keep the 'None' values instead of annotating a Frame in case of doubt. 


######3. Annotation of frame element######
Once the user has selected a frame, the frame elements for this frame are listed. The user is asked to select the correct frame element.

######3. Final check######
The user is presented with the sentence, predicate and argument and the chosen frame and frame element. At this point, (s)he can choose to either (a) Retry the annotation of this relation, (b) Save the annotation and continue with the next relation, or (c) Save the annotation and quit annotating the file.



###Contact###

- Chantal van Son (VU University Amsterdam)
- c.m.van.son@student.vu.nl / c.m.van.son@gmail.com



