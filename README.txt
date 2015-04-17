======================================
Summary and licensing information
======================================
This code is for extraction of technical phrases and their relations from a domain corpus (e.g. medical device incident reports, or netwrok tickets) to populate the classes and relationships in a pre-defined domain-specific ontology model.

It is partly adapted based on the techniques proposed for extracting domain-specific n-grams and relations between noun categories , respectively, in the following papers:
- R. Potharaju, N. Jain, and C. Nita-Rotaru, “Juggling the Jigsaw: Towards Automated Problem Inference from Network
  Trouble Tickets,” in NSDI, 2013.
- T. Mohamed, E.R. Hruschka, T.M. Mitchell: Discovering Relations between Noun Categories, EMNLP, pp. 1447-1455, 2011.

Copyright (C) 2015 University of Illinois Board of Trustees, DEPEND Research Group, Homa Alemzadeh

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

======================================
How to run?
======================================
- python tech_ngrams.py
- python relation_extraction.py -r 5 -k 5 -c1 Instruments -c2 Operators

The input data files are in the: ./Data folder
The stanford pos tagger library is called from: ./stanford-postagger-2013-06-20
