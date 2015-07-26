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

# 1: da Vinci data, 0: IBM data
da_Vinci = 0;

bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()
pos = POSTagger('./stanford-postagger-2013-06-20/models/english-left3words-distsim.tagger', 
                './stanford-postagger-2013-06-20/stanford-postagger.jar')

# N-gram patterns for technical terms
patterns = [['NN'],['JJ'], ['JJ', 'NN'], ['NN','NN'], ['JJ', 'JJ', 'NN'], ['JJ', 'NN', 'NN'], 
            ['NN', 'JJ', 'NN'], ['NN', 'NN', 'NN'],['NN', 'IN', 'NN'],
			['JJ', 'JJ', 'JJ','NN'], ['JJ', 'JJ', 'NN','NN'], ['JJ', 'NN', 'NN','NN'], 
			['NN', 'NN', 'NN','NN'],['NN','JJ', 'NN','NN'], ['NN', 'NN','JJ', 'NN']]

training_set = []
# Input and Output files
if da_Vinci:
	CSV_In = './Data/davinci.csv'
	# Training data (seeds)
	CSV_In2 = './Data/Instruments.csv'
	f1 = open(CSV_In, 'rU')
	f1t = open(CSV_In2, 'rU')	
	csv_rd = csv.reader(f1, dialect='excel', delimiter=',')
	csv_rdt = csv.reader(f1t, dialect='excel', delimiter=',')
	# Skip headers 
	csv_rdt.next();
	# Get all the training phrases
	for line in csv_rdt:
		training_set.append(line[0])
	# Skip headers 
	csv_rd.next();
	csv_rd.next();
else:
	p7_models = ["9117_mmb","9117_mmc","9117_mmd"]
	p7_model = p7_models[0]
	#input_file = open('./Data/POWER7_'+p7_model+'_data.txt');
	input_file = open('./Data/POWER7_data_0.txt');
	
Out_file = './Data/n_grams.txt';
Out_file2 = './Data/n_grams_filtered.txt';
f2 = open(Out_file,'wb')
f3 = open(Out_file2,'wb')


# da_Vinci data or IBM data?
if da_Vinci:
    start_col = 1;
    end_col = 2;
else:
    start_col = 0;
    end_col = 1;

# Clean part of speech tags
def cleanseNN(list):
	for i in range(0, len(list)):
		for k in range(0, len(list[i])):
			if("NN" in list[i][k]):
				list[i][k] = "NN"
	return list
	
	
# Filter n-grams with low Mutual Information (statistically insignificant)
def entropy_filter(phrase_list, docs, text):
    # Dictionary of n-grams with their RIDFs and TFs
	RIDF = {'WORD': [0,0,0]};
	filtered_list = {'WORD':-1};
	for phrase in phrase_list:
		#print phrase
		df = sum(1 for d in docs if phrase in d);
		IDF = math.log(len(docs)/(0.5+df))
		# Calculate term frequency
		tf = 0.5+text.count(phrase)
		eIDF = math.log(1-math.exp((-tf)/len(docs)))	
		RIDF[phrase] = [IDF+eIDF,tf-0.5,df]
	RIDF.pop("WORD", None)
	print "\nCalculated RIDFs"
	
	# Sort the n-grams based on their RIDF values
	sorted_RIDF = sorted(RIDF.items(), key=operator.itemgetter(1))
	#print sorted_RIDF
	print "\nSorted n-grams"
	# Filter those with negative RIDF values and save the rest with their DFs in results
	for key, values in sorted_RIDF:
		#if (values[0] > 0):
			filtered_list[key] = values[0]	
	filtered_list.pop("WORD", None)
	#print filtered_list
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


# Get all the text
if da_Vinci:
	for line in csv_rd:
		cnt = cnt + 1
		Text = ''
		for i in range(start_col,end_col+1):
			Text = Text + ' ' + line[i].rstrip('\n\r')
		if not (Text == ''):
			docs.append(Text);
			All_Text = All_Text + Text;
		#if (cnt == 10):
		#	break;
else:
	for line in input_file:
		cnt = cnt + 1
		Text = line.rstrip('\n\r')
		if not (Text == ''):
			docs.append(Text);
			All_Text = All_Text + Text;
		#if (cnt == 10):
		#	break;

print "\nRead all data.."
print str(len(docs))+" Reports"	
#print All_Text;

# Get the sentences
Text = All_Text

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

# Part of Speech Tagging 
tags = [];
starti = 0
endi = 0
no_chunks = len(tokens)/50000;
print 'Process '+str(len(tokens))+' tokens in '+str(no_chunks)+ ' chunks..' 
for l in range(0, no_chunks):
	endi =  min((starti + (len(tokens)/no_chunks) ), len(tokens))
	print "Tagging #" + str(l) + ": from " + str(starti)+ " to "+str(endi-1)
	tags = tags + pos.tag(tokens[starti:endi])[0];
	starti = endi;
	
print "\n"+str(len(tags))+" words tagged.."

# Save all the Noun and Adjective unigrams in a hash table
Tag_set = {'Word':'Tag'}
for tag in tags:
	if (cleanseNN([str(tag[1])]) in patterns[0:2]):
		Tag_set[str(tag[0])] = str(tag[1])		
	#print cleanseNN([str(tag[1])])
#print tags
#print '\n'
#print Tag_set


# Look for longest n-gram appearing in each sentence with the patterns of technical terms			
# Normalization and Punctuation filtering=> keep sentence separators
Text = All_Text.lower()
sentences = re.split('[;,.:]', Text)
#print sentences
n_gram = []
tags = []
n_gram_str = ''
for s in sentences:
	#regex = re.compile('[%s]' % re.escape('!"#$%&\'()*+/:<=>?@[\\]^_`{|}~-'))
	#Text = regex.sub(' ',s)
    # Get the words
	raw_tokens = word_tokenize(unicode(s, errors='ignore'))
	#print raw_tokens
	# Filter numbers 
	words= [str(t) for t in raw_tokens if not str(t).isdigit() and len(str(t))>1]
	
	#print '--->' + Text + '\n'
	s_result = []
	for w in words:
		if (Tag_set.has_key(w)):
			n_gram.append(w)
			tags.append(Tag_set[w])
			#print "n-gram = "+n_gram[-1]
		# If this is the last word in the list or a non-NJ word, we finalize the n-gram
		if not(Tag_set.has_key(w)) or (words.index(w) == len(words)-1):
			# Only if we found something
			if (len(n_gram) > 1):
				#print "long n-gram = "+n_gram[0]
				# If the pattern of tags is of interest, save it
				if (cleanseNN(tags) in patterns):
					for n in n_gram:
					    if (n_gram_str == ''):
					    	n_gram_str = n
					    else:
							n_gram_str = n_gram_str + ' ' + n 
					if not(n_gram_str in s_result):
					    s_result.append(n_gram_str)
						#print n_gram_str
					#print '===' + n_gram_str + '\n'
			for n in s_result:
				if (results.has_key(n)):
					results[n] = results[n]+1
				else:						
					results[n] = 1
			# Restart searching for next n-gram
			n_gram = []
			tags = []
			n_gram_str = ''
print "\n"+str(len(results.keys()))+" n-grams found.."	
print results.keys()

f2.write('Technical Phrase, Sentence Frequency\n')
for key in results.keys():
	f2.write(key+', '+str(results[key])+'\n')

# Filtering n-grams	
filtered_result = entropy_filter(results.keys(), docs, Text)
print filtered_result
# Sort filtered n-grams based on their scores
sorted_filtered = sorted(filtered_result.items(), key=operator.itemgetter(1), reverse=True)
n_cnt = 0;
data_set = []
f3.write('Technical Phrase, Document Frequency\n')
for key, value in sorted_filtered:
	#print f
	if da_Vinci:
		for t in training_set[0:50]:
			if (t in key):
				f3.write(key+', '+str(value)+'\n')
				data_set.append(value)
				n_cnt = n_cnt + 1;
				break;
	else:
		f3.write(key+', '+str(value)+'\n')
		data_set.append(value)
		n_cnt = n_cnt + 1;		

if da_Vinci:
	f1.close()
	f1t.close()
else:
	input_file.close()
f2.close();
f3.close();
t1 = time()

print "\n\nProcessed a total of:"
print str(len(docs))+" Reports"		
print str(len(sentences))+" Sentences"
print str(len(tokens))+" Words"
print str(n_cnt)+" Technical Phrases"
print "In "+str(t1-t0)+' seconds..\n'
