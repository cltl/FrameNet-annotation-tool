###Description###


This module takes all the CAT XML files in a given directoy as input and allows the user to annotate the HAS_PARTICIPANT relations with frames and frame elements from FrameNet. The CAT XML files already have to be annotated with the HAS_PARTICIPANT roles.

There are two annotation rounds:
1. annotate all HAS_PARTICIPANT relations using the Predicate Matrix & FrameNet
2. annotate only the HAS_PARTICIPANT relations where there is no frame and/or role specified yet (manual entering)

In Round 1 the user is asked to enter the frame directly (if the user already knows which frame applies) or to enter the lemma(s) expressing or relating to the predicate for each HAS_PARTICIPANT relation. The user is then presented with the frames, definitions and roles that are associated with the lemma(s) in the Predicate Matrix & FrameNet. In Round 2 the user is asked to manually (re-)enter the frames and roles for the HAS_PARTICIPANT relation that is missing the frame and/or role.

To run the script you need the following resources, which are included in this module:
- Predicate Matrix (English-Dutch version, including English and Dutch lemmas)
- The Frame files from FrameNet
- A separate file with the lexical units listed for each Frame (extracted from FrameNet)

###Usage from command line###

Usage: 		python annotation.py <inputdir> <round [1 or 2]>
Example: 	python annotation.py ./Example 1 


###Some general guidelines###

- The best way is to first annotate files in Round 1, and then annotate the resulting files (in folder 'X-framenet-1') in Round 2 to annotate the relations for which there was no good frame available in the Predicate Matrix.
- In the first step of the annotation you can either: (a) enter one frame directly if you already know which frame applies; use capitals and underscores, e.g. 'Attack' / 'Make_possible_to_do', OR (b) enter one or more lemmas that express or are strongly related to the predicate; use lowercase only and separate multiple lemmas by commas without spaces, e.g. 'praten' / 'praten,talk'
- Be critical!! Rather keep the 'None' values instead of annotating a Frame in case of doubt. 


###Some guidelines for entering the lemma(s) (Round 1)###

- You can enter both Dutch and English lemmas.
- You can search for both nouns and verbs, but it is more likely to get results for verbs. So if possible, try to convert nominal predicates into verbal predicates (analysis --> analyse).
- If the predicate is too specific/vague, try to think of another word that expresses the same or a more general concept (e.g. take steps --> do).
- If the predicate is a complex expression (multi-word expression, idioms), try to think of another word that expresses the same concept (e.g. for sale --> sell, to be/come under fire --> criticize).
- English phrasal verbs can be entered by separating the words by an underscore (e.g. go_on).

###Contact###

Chantal van Son (VU University Amsterdam)
c.m.van.son@student.vu.nl / c.m.van.son@gmail.com



