###Summary

This module allows a user to annotate all CAT XML files in a given directory with frames and frame elements from FrameNet. The user can search for the frames and frame elements in FrameNet and the Predicate Matrix.

Usage: 		python annotation.py \<inputdir\> 

Example: 	python annotation.py ./Data/Example 

###Requirements
The input files have to be in labeled CAT<sup>1</sup> (acronym for [CELCT/Content Annotation Tool](https://dh.fbk.eu/resources/cat-content-annotation-tool)) XML format and already have been annotated with HAS\_PARTICIPANT relations according to the [NewsReader](http://www.newsreader-project.eu/) annotation scheme<sup>2</sup>.

The script uses the following resources, which are included in this module:
- [Predicate Matrix](http://adimen.si.ehu.es/web/PredicateMatrix)<sup>3</sup> (English-Dutch version, including English and Dutch lemmas)
- The Frame files of the XML version of [FrameNet](https://framenet.icsi.berkeley.edu)<sup>4</sup> (version 1.5)
- A separate file with the lexical units listed for each Frame (extracted from FrameNet version 1.5)

###Description
For each file in the input directory, the user is asked whether (s)he wants to annotate this file and for which annotation round. There are two rounds:

1. **All relations:** annotate all HAS_PARTICIPANT relations (if annotations for a relation already exist, the user is asked whether (s)he wants to change the existing annotation)
2. **Empty relations:** annotate only the HAS_PARTICIPANT relations where there is no frame and/or role specified yet 

After the user has chosen the annotation round, the annotation of the document starts. The following steps are carried out for each HAS\_PARTICIPANT relation:

######1. Enter a frame or lemma
The user is presented with the sentence, predicate and argument. If the user already knows which frame applies, (s)he can enter the frame directly by using capitals and underscores (e.g. *Attack*, *Make\_possible\_to\_do*). If the user does not know which frame applies, (s)he can enter one or multiple Dutch or English lemma(s) expressing or relating to the predicate by using lowercase only (e.g. *praten*). Multiple lemmas can be separated by commas without spaces (e.g. *praten,talk*). The user is then presented with the frames, definitions and roles that are associated with the lemma(s) in the Predicate Matrix & FrameNet. 

Some guidelines:
- You can search for both nouns and verbs, but it is more likely to get results for verbs. So if possible, try to convert nominal predicates into verbal predicates (*analysis* --- *analyse*).
- If the predicate is too specific/vague, try to think of another word that expresses the same or a more general concept (e.g. *take steps* --- *do*).
- If the predicate is a complex expression (multi-word expression, idioms), try to think of another word that expresses the same concept (e.g. *for sale* --- *sell*, *to be/come under fire* --- *criticize*).
- English phrasal verbs can be entered by separating the words by an underscore (e.g. *go\_on*).


######2. Annotation of frame
The frames associated with the lemma(s) (or the entered frame) and their definitions are, one by one, presented to the user (if there are more than 10 frames found, the user is asked to make a smaller selection of frames first). The user has to decide for each frame if it is a frame that fits or not. If multiple frames are chosen, the user is asked to choose the best frame. If no frames are chosen, 'None' is filled in for the frame and the frame element; it is up to the user to decide in the final check (see below) whether there is indeed no good frame available or whether (s)he wants to try again with other lemmas. 

**NB:** Be critical!! In case of doubt, rather keep the 'None' values instead of annotating an ill-fitting frame.


######3. Annotation of frame element
Once the user has selected a frame, its frame elements are listed. The user is asked to select the correct frame element.

######3. Final check
The user is presented with the sentence, predicate and argument as well as the chosen frame and frame element. At this point, (s)he can choose to either (a) Retry the annotation of this relation, (b) Save the annotation and continue with the next relation, or (c) Save the annotation and quit annotating the file.

###Contact

- Chantal van Son (VU University Amsterdam)
- c.m.van.son@student.vu.nl / c.m.van.son@gmail.com

###References

<sup>1</sup> Moretti, G. and Sprugnoli, R. (2014). *CAT User Manual for the NewsReader EU Project. NWR-2014-5*. Fondazione Bruno Kessler.

<sup>2</sup> Tonelli, S., Sprugnoli, R. Speranza, M. and Minard, A.L. (2014). *NewsReader Guidelines for Annotation at Document Level. NWR-2014-2-2. Version FINAL (Aug 2014)*. Fondazione Bruno Kessler.

<sup>2</sup> Lopez de Lacalle, M., Laparra, E., & Rigau, G. (2014). Predicate Matrix: extending SemLink throughWordNet mappings. In *Proceedings of the 9th edition of the Language Resources and Evaluation Conference* (pp. 903-909). Reykjavik, Iceland.

<sup>3</sup> Baker, C. F., Fillmore, C. J., & Lowe, J. B. (1998, August). The Berkeley FrameNet Project. In *Proceedings of the 17th international conference on Computational linguistics-Volume 1* (pp. 86-90). Association for Computational Linguistics.



