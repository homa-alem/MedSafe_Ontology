''' 
Finding Technical Phrases (n-grams) from Text

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

'''
import nltk
from nltk.collocations import *
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk import bigrams
from nltk import trigrams
from nltk.util import ngrams
from nltk.tag.stanford import POSTagger
import csv
from time import time
import re
import math
import operator

bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()
pos = POSTagger('./stanford-postagger-2013-06-20/models/english-left3words-distsim.tagger', './stanford-postagger-2013-06-20/stanford-postagger.jar')

# N-gram patterns for technical terms
patterns = [['NN'],['JJ'], ['JJ', 'NN'], ['NN','NN'], ['JJ', 'JJ', 'NN'], ['JJ', 'NN', 'NN'], ['NN', 'JJ', 'NN'], ['NN', 'NN', 'NN'],['NN', 'IN', 'NN'],
			['JJ', 'JJ', 'JJ','NN'], ['JJ', 'JJ', 'NN','NN'], ['JJ', 'NN', 'NN','NN'], ['NN', 'NN', 'NN','NN'],['NN','JJ', 'NN','NN'], ['NN', 'NN','JJ', 'NN']]

# Input and Output files
CSV_In = './Data/davinci.csv'
Out_file = './Data/n_grams.txt';
f1 = open(CSV_In, 'rU')
f2 = open(Out_file,'wb')
csv_rd = csv.reader(f1, dialect='excel', delimiter=',')


# Clean part of speech tags
def cleanseNN(list):
	for i in range(0, len(list)):
		for k in range(0, len(list[i])):
			if("NN" in list[i][k]):
				list[i][k] = "NN"
	return list

# Calculate term frequency
def term_f(word, text):
	return 0.5+text.count(word)
	
def doc_f(word, docs):
	df = sum(1 for d in docs if word in d)
	return df
	
# Filter n-grams with low Mutual Information (statistically insignificant)
def entropy_filter(phrase_list, docs, text):
	RIDF = {'WORD': 0};
	filtered_list = [];
	for phrase in phrase_list:
		#print phrase
		IDF = math.log(len(docs)/(0.5+doc_f(phrase, docs)))
		eIDF = math.log(1-math.exp((-term_f(phrase,text))/len(docs)))	
		RIDF[phrase] = IDF+eIDF
	RIDF.pop("WORD", None)
	print "\nCalculated RIDFs"
	
	# Sort the n-grams based on their RIDF values
	sorted_RIDF = sorted(RIDF.items(), key=operator.itemgetter(1))
	print "\nSorted n-grams"
	# Filter those with negative RIDF values
	for key, value in sorted_RIDF:
		if (value > 0):
			filtered_list.append(key)	
	print "\nFiltered n-grams"
	return filtered_list

# Main code starts here
t0 = time()

cnt = 0
docs = [];
All_Text = '';
sentences = [];
words = [];
results = {'ngram':0};
stops = set(stopwords.words('english'))

# Skip headers 
csv_rd.next();
# Get all the text
for line in csv_rd:
	cnt = cnt + 1
	Text = ''
	for i in range(1,2):
		Text = Text + line[i].rstrip('\n\r')
	if not (Text == ''):
		docs.append(Text);
		All_Text = All_Text + Text;
print "\nRead all data.."

# Get the sentences
Text = All_Text
sentences =  All_Text.split('.')[0:-1];

# Normalization and Punctuation filtering
Text = Text.lower()
regex = re.compile('[%s]' % re.escape('!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~-'))
Text = regex.sub(' ',Text)

# Get the words
raw_tokens = word_tokenize(unicode(Text, errors='ignore'))

# Filter English Stop words and numbers 
#tokens= [str(t) for t in raw_tokens if str(t) not in stops and not str(t).isdigit() and len(str(t))>1]
tokens= [str(t) for t in raw_tokens if not str(t).isdigit() and len(str(t))>1]
words = words+tokens

print "\nTagging started.."
# Part of Speech Tagging 
tags = [];
starti = 0
endi = 0
for l in range(0, 10):
	endi =  min((starti + (len(tokens)/10) ), len(tokens))
	print "Tagging #" + str(l) + ": from " + str(starti)+ " to "+str(endi-1)
	tags = tags + pos.tag(tokens[starti:endi])[0];
	starti = endi;
	
print "\n"+str(len(tags))+" words tagged.."

# Save all the Noun and Adjective unigrams in a hash table
Tag_set = {'Word':'Tag'}
for tag in tags:
	if (cleanseNN([str(tag[1])]) in patterns[0:2]):
		Tag_set[str(tag[0])] = str(tag[1])		

# Look for longest n-gram appearing in the text with the patterns of technical terms			
n_gram = [];
tags = [];
n_gram_str = '';
for tok in raw_tokens:
	phrase = str(tok);
	if (len(n_gram) < 5) and (Tag_set.has_key(phrase)):
		n_gram.append(phrase);
		tags.append(Tag_set[phrase]);
	else:
		# Only if we found something
		if (len(n_gram) > 1):
			# If the pattern of tags is of interest, save it
			if (cleanseNN(tags) in patterns):
				for n in n_gram:
					n_gram_str = n_gram_str + ' ' + n; 
				if (results.has_key(n_gram_str)):
					results[n_gram_str] = results[n_gram_str]+1;
				else:
					results[n_gram_str] = 1;
					print n_gram_str;
			# Restart searching for next n-gram
			n_gram = []; 
			tags = [];
			n_gram_str = '';

print "\n"+str(len(results.keys()))+" n-grams found.."	

# Filtering n-grams	
filtered_result = entropy_filter(results.keys(), docs, Text);
for f in filtered_result:
	#print f
	f2.write(f+'\n')
	
f1.close();
f2.close();
<<<<<<< HEAD

t1 = time()
# Main code ends here

print "\n\nProcessed a total of:"
print str(len(docs))+" Reports"		
print str(len(sentences))+" Sentences"
print str(len(words))+" Words"
print "In "+str(t1-t0)+' seconds..\n'
=======
f3.close();
f4.close();
f5.close();
f6.close();
>>>>>>> 384b031693822b2d7440e889c47c6d0d42480167
