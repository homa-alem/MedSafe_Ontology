''' 
Finding Technical Phrases (n-grams) from Text

Copyright (C) 2015 University of Illinois Board of Trustees, DEPEND Research Group, Homa Alemzadeh and Raymond Hoagland

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
import time
import re
import math
import operator

bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measures = nltk.collocations.TrigramAssocMeasures()
pos = POSTagger('./stanford-postagger-2013-06-20/models/wsj-0-18-bidirectional-nodistsim.tagger', './stanford-postagger-2013-06-20/stanford-postagger.jar')

unipatterns = [['NN']]
bipatterns = [['JJ', 'NN'], ['NN','NN']]
tripatterns = [['JJ', 'JJ', 'NN'], ['JJ', 'NN', 'NN'], ['NN', 'JJ', 'NN'], ['NN', 'NN', 'NN'], ['NN', 'IN', 'NN']]
fourpatterns = [['JJ', 'JJ', 'JJ','NN'], ['JJ', 'JJ', 'NN','NN'], ['JJ', 'NN', 'NN','NN'], ['NN', 'NN', 'NN','NN'],
                ['NN','JJ', 'NN','NN'], ['NN', 'NN','JJ', 'NN']]

CSV_In = './Data/Sample_Data_1.csv'
f1 = open(CSV_In, 'rU')
f2 = open('./Data/Unigrams.txt','wb')
f3 = open('./Data/Bigrams.txt','wb')
f4 = open('./Data/Trigrams.txt','wb')
f5 = open('./Data/Fourgrams.txt','wb')
f6 = open('./Data/Test.txt','wb')
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
    tokens = nltk.wordpunct_tokenize(unicode(text, errors='ignore'))
    return 0.5+tokens.count(word)
    
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
    
    # Sort the n-grams based on their RIDF values
    sorted_RIDF = sorted(RIDF.items(), key=operator.itemgetter(1))
    # Filter those with negative RIDF values
    for key, value in sorted_RIDF:
        if (value > 0):
    		filtered_list.append(key)	
    return filtered_list

# Get all the text in the data
Text = ''
docs = [];
for line in csv_rd:
    for i in range(0,2):
    	col = line[i].rstrip('\n\r')
    	if not (col == ''):
    		Text = Text + ' ' + col;
    		docs.append(col);
Text = Text.lower()

# Punctuation filtering
regex = re.compile('[%s]' % re.escape('!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~-'))
Text = regex.sub(' ',Text)
tokens = nltk.wordpunct_tokenize(unicode(Text, errors='ignore'))

# Stop word and number filtering
stops = set(stopwords.words('english'))
tokens= [str(t) for t in tokens if str(t) not in stops and not str(t).isdigit() and len(str(t))>1]
tags = pos.tag(tokens)[0];
Tag_set = {'Word':'Tag'}

# Unigrams
res0 = []
for tag in tags:
    if (cleanseNN([str(tag[1])]) in unipatterns):
        if not str(tag[0]) in res0:
           Tag_set[str(tag[0])] = str(tag[1])
           res0.append(str(tag[0]))
           #f2.write(res0[-1]+'\n')
filtered_res0 = entropy_filter(res0, docs, Text);
for f in filtered_res0:
	f2.write(f+'\n')
#print filtered_res0


# Bigrams 
finder = BigramCollocationFinder.from_words(tokens)
scored = finder.score_ngrams(bigram_measures.raw_freq)
res = sorted(bigram for bigram, score in scored)
#res = [(b1, b2) for (b1, b2) in res if b1 not in stops and b2 not in stops and not b1.isdigit() and not b2.isdigit()]

# POS Pattern Filtering
res1 = [];
for tok in res:
    #tag = pos.tag(tok)
    if Tag_set.has_key(tok[0]) and Tag_set.has_key(tok[1]):
		tag = [Tag_set[tok[0]],Tag_set[tok[1]]]
		#if (cleanseNN([str(tag[0][1]),str(tag[1][1])]) in bipatterns):
		if (cleanseNN([tag[0],tag[1]]) in bipatterns):    
			#res1.append(str(tag[0][0])+' '+str(tag[1][0]))
			res1.append(tok[0]+' '+tok[1])
			#f3.write(res1[-1]+'\n')
        #print res1[-1]
filtered_res1 = entropy_filter(res1, docs, Text);
for f in filtered_res1:
	f3.write(f+'\n')
# return the 10 n-grams with the highest PMI
#best = finder.nbest(bigram_measures.pmi, 10)      

# Trigrams
finder = TrigramCollocationFinder.from_words(tokens)
scored = finder.score_ngrams(trigram_measures.raw_freq)
res = set(nltk.trigrams(tokens))#sorted(trigram for trigram, score in scored)
# POS Pattern Filtering
res2 = [];
for tok in res:
    #tag = pos.tag(tok)
    if Tag_set.has_key(tok[0]) and Tag_set.has_key(tok[1]) and Tag_set.has_key(tok[2]):
		tag = [Tag_set[tok[0]],Tag_set[tok[1]], Tag_set[tok[2]]]
		#if (cleanseNN([str(tag[0][1]),str(tag[1][1]),str(tag[2][1])]) in tripatterns):
		if (cleanseNN([tag[0],tag[1],tag[2]]) in tripatterns):    
			#res2.append(str(tag[0][0])+' '+str(tag[1][0])+' '+str(tag[2][0]))
			res2.append(tok[0]+' '+tok[1]+' '+tok[2])
			#f4.write(res2[-1]+'\n')
filtered_res2 = entropy_filter(res2, docs, Text);
for f in filtered_res2:
	f4.write(f+'\n')
res = res1 + res2

# Fourgrams
res3 = []
res = set(ngrams(tokens, 4))
for tok in res:
    #tag = pos.tag(tok)
    if Tag_set.has_key(tok[0]) and Tag_set.has_key(tok[1]) and Tag_set.has_key(tok[2]) and Tag_set.has_key(tok[3]):
		tag = [Tag_set[tok[0]],Tag_set[tok[1]], Tag_set[tok[2]], Tag_set[tok[3]]]
		#if (cleanseNN([str(tag[0][1]),str(tag[1][1]),str(tag[2][1])]) in tripatterns):
		if (cleanseNN([tag[0],tag[1],tag[2],tag[3]]) in fourpatterns):    
			#res2.append(str(tag[0][0])+' '+str(tag[1][0])+' '+str(tag[2][0]))
			res3.append(tok[0]+' '+tok[1]+' '+tok[2]+' '+tok[3])
			#f5.write(res3[-1]+'\n')
filtered_res3 = entropy_filter(res3, docs, Text);
for f in filtered_res3:
	f5.write(f+'\n')
	
f1.close();
f2.close();
f3.close();
f4.close();
f5.close();
f6.close();