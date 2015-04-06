''' 
Finding Relation between Noun Categories

Copyright (C) 2015 University of Illinois Board of Trustees, DEPEND Research Group, Raymond Hoagland and Homa Alemzadeh

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

# TWO CATEGORIES IMPLIED

# import statements
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
from sklearn import datasets
from sklearn import metrics
import pandas as pd
import argparse
import logging
import sys

# define parser and add thresholds
parser = argparse.ArgumentParser(description='K-Means Clusterer v1.0.0')
parser.add_argument('-r', metavar='--rarity', dest='rarity', nargs='?', action='store', required=False, const=-1, default=-1,
                   help='rarity threshold for pre-processing', type=int)
parser.add_argument('-c', metavar='--co-occurrence', dest='co', nargs='?', action='store', required=False, const=-1, default=-1,
                   help='co-occurrence threshold for pre-processing', type=int)
# add args for num of clusters and verbose
parser.add_argument('-k', metavar='--clusters', dest='clusters', nargs='?', action='store', required=False, const=-1, default=3,
                   help='number of clusters for k-means', type=int)
parser.add_argument('-v', metavar='--verbose', dest='verbose', action='store_const', required=False, const=True, default=False,
                   help='print various messages during execution')
# add args for categories
parser.add_argument('-c1', metavar='--category1', dest='cat1', action='store', nargs = '?', required=False, const=True, default='Instruments',
                   help='category1 for clustering')
parser.add_argument('-c2', metavar='--category2', dest='cat2', action='store', nargs = '?', required=False, const=True, default='Operators',
                   help='category2 for clustering')
parser.add_argument('-s', metavar='--sentences', dest='cat3', action='store', nargs = '?', required=False, const=True, default='Event',
                   help='sentences')
# add args for input/output files
parser.add_argument('-i1', metavar='--input1', dest='inp1', action='store', nargs='?', required=False, const=None, default=None,
                    help='input1 filepath')
parser.add_argument('-i2', metavar='--input2', dest='inp2', action='store', nargs='?', required=False, const=None, default=None,
                    help='input2 filepath')
parser.add_argument('-i3', metavar='--input3', dest='inp3', action='store', nargs='?', required=False, const=None, default=None,
                    help='input3 filepath')
parser.add_argument('-o', metavar='--output', dest='out', action='store', nargs='?', required=False, const=True, default=True,
                    help='dump to output file')

# get the args from the user
args = parser.parse_args()

# use default files unless otherwise specified
instrumentsIn = './Instruments.csv' if args.inp1==None else args.inp1
operatorsIn = './Operators.csv' if args.inp2==None else args.inp2
sentencesIn = './davinci.csv' if args.inp3==None else args.inp3

try:
    df = pd.read_csv(instrumentsIn)
except:
    print 'Bad file input1'
    sys.exit(0)
try:
    if(args.cat1 == 'Instruments'):
        # read input files (assume cols called instruments, operators, event)
        Instruments_dic = list(df['Instruments'][:len(df['Instruments'])])
    else:
        Instruments_dic = list(df[args.cat1][:len(df[args.cat1])])
        print Instruments_dic
except:
    print 'Bad input category 1'
    sys.exit(0)

try:
    df = pd.read_csv(operatorsIn)
except:
    print 'Bad file input2'
    sys.exit(0)
try:
    if(args.cat2 == 'Operators'):
        Operators_dic = list(df['Operators'][:len(df['Operators'])])
    else:
        Operators_dic = list(df[args.cat2][:len(df[args.cat2])])
except:
    print 'Bad input category 2'
    sys.exit(0)

try:
    df = pd.read_csv(sentencesIn)
except:
    print 'Bad file input_sentences'
    sys.exit(0)
try:
    if(args.cat3 == 'Event'):
        sample_sentences = list(df['Event'][:len(df['Event'])])
    else:
        sample_sentences = list(df[args.cat3][:len(df[args.cat3])])
    tmp_sent = []
    for i in sample_sentences:
        i = str(i)
        for k in i.split('.'):
            tmp_sent.append(k)
    sample_sentences = tmp_sent
    print len(sample_sentences)
except:
    print 'Bad input sentences'
    sys.exit(0)


# predefined categories
Category_nums = {0: 'Instruments', 1: 'Operators'}
Categories = {'Instruments': Instruments_dic, 'Operators': Operators_dic}

def preProcess(sentences, rarityThresh=-1, coThresh=-1, lexPatterns = []):
    if(rarityThresh == -1 and coThresh == -1):
        print 'gg'
        return sentences
        
    # category indices
    idx1 = -1
    idx2 = -1

    # used for rarity threshold
    contextHash = {}

    # used for cooccurence threshold
    occHash = {}

    # pruning list
    unselected = []

    # selected subset
    subSet = []

    # lowercase versions for all values in the categories
    CategoriesLower = [frozenset([f.lower() for f in Categories[k]]) for k in Categories.keys()]

    # check each sentence
    for i in xrange(len(sentences)):

        # pull words and reset indices
        words = sentences[i].lower().split()
        idx1 = -1
        idx2 = -1
        category_1 = -1
        category_2 = -1
        cat_idx = 0

        # check each category
        for category in CategoriesLower:
            # loop through words of the sentence
            for k in xrange(len(words)): 
                # mark if found
                if (words[k] in category):
                    if(idx1 == -1):
                        idx1 = k
                        category_1 = cat_idx
                        #break
                        continue
                    else:
                        idx2 = k
                        category_2 = cat_idx
                        break

            #identified now so pass out
            if(idx1 != -1 and idx2 != -1):
                break
            cat_idx += 1

        # if found a pair, add to the output sentences
        if(idx1 != -1 and idx2 != -1):

            # pull out context
            context = ' '.join(words[idx1+1 : idx2])

            # if already seen, increment number of times seen and what lines it has been seen at
            if(context in contextHash):
                val = contextHash[context]
                val[0] += 1
                val[1].append(i)
               
            # new entry
            else:
                contextHash[context] = [1, [i]]

            # if already seen, update number of times for these cats and what lines
            if(context in occHash):

                # get current hash value
                val = occHash[context]
                caught = -1

                # loop through segments
                for g in xrange(len(val)):

                    # extract hash info
                    cat1 = val[g][0]
                    cat2 = val[g][1]
                    value = val[g][2]
                    lines = val[g][3]

                    # check if this category combo has been seen
                    if((cat1 == category_1 and cat2 == category_2) or (cat1 == category_1 and cat2 == category_2)):

                        # update info
                        value += 1
                        val[g][2] = value
                        lines.append(i)
                        val[g][3] = lines
                        caught = 1
                        break

                # update value
                if(caught == 1):
                    occHash[context] = val

                # new entry for this context
                else:
                    occHash[context].append([category_1, category_2, 1, [i]])

            # new entry
            else:
                occHash[context] = [[category_1, category_2, 1, [i]]]

        else:
            if(args.verbose):
                print 'Printing sentence: '
                print sentences[i]
            unselected.append(i)

    # 1st Pruning Step
    if(rarityThresh != -1):
        for key in contextHash.keys():
            val = contextHash[key]
            # does not meet min so kill all of its sentencces
            if(val[0] < rarityThresh):
                for v in val[1]:
                    if(not v in unselected):
                        unselected.append(v)

    # 2nd Pruning Step
    if(coThresh != -1):
        for key in occHash.keys():
            val = occHash[key]
            for f in val:
                if(f[2] < coThresh):
                    for v in f[3]:
                        if(not v in unselected):
                            unselected.append(v)

    print 'idling'
    unselected = sorted(unselected)
    unsel_val = 0
    sentence_val =0
    while(1):
        if(sentence_val == len(sentences)):
            break
        if(sentence_val < unselected[unsel_val]):
            subSet.append(sentences[sentence_val])
        elif(sentence_val == unselected[unsel_val]):
            unsel_val += 1
        sentence_val += 1
 
    #subSet = [sentences[i] for i in xrange(len(sentences)) if not i in unselected]
    
    return subSet

def performClustering(matrix, order, K=3):
    outfile = open('./clusterDump.txt', 'wb')

    km = KMeans(K)
    try:
        km.fit_predict(matrix)
    except:
        k = K-1
        while(1):
            try:
                km = KMeans(k)
                km.fit_predict(matrix)
                break
            except:
                k -= 1

    if(args.verbose):
        print 'Printing cluster centers and labels: '
        print km.cluster_centers_
        print km.labels_

    if(args.out):
        for i in xrange(len(km.labels_)):
            outfile.write(str(km.labels_[i])+' '+' '.join(order[i]) + '\n')

    outfile.close()
    return (km.cluster_centers_, km.labels_)

def decideNewRelation(centers, labels, hash, order):
    print len(centers)
    for center in centers:
        bestLoc = [-1, -1]
        for i in xrange(len(center)):
            if(center[i] > bestLoc[1]):
                bestLoc[0] = i
                bestLoc[1] = center[i]
        print "Printing new relation: "
        print order[bestLoc[0]]

def constructMatrix(C1, C2, sentences, indices=True, threshold=-1):
    cat1 = None
    cat2 = None

    # need to look for the right string within category_nums and then pull instances
    if(indices):
        cat1 = [f.lower() for f in Categories[Category_nums[C1]]]
        cat2 = [f.lower() for f in Categories[Category_nums[C2]]]

    #given the name, just pull instances
    else:
        cat1 = [f.lower() for f in Categories[C1]]
        cat2 = [f.lower() for f in Categories[C2]]

    matrix = []
    contextHash = {}
    order = []

    # look through sentences provided
    for k in xrange(len(sentences)):
        startIdx = -1
        endIdx = -1
        startWord = ''
        endWord = ''
        sent = sentences[k].lower().split()

        # look through words and identify words from categories
        for i in xrange(len(sent)):
            if(sent[i] in cat1):
                startIdx = i
                startWord = sent[i]

            elif (sent[i] in cat2 and startIdx != -1):
                endIdx = i
                endWord = sent[i]

            # early break, identified keywords
            if(startIdx != -1 and endIdx != -1):
                break

        # make sure found keywords
        if(startIdx != -1 and endIdx != -1):

            # pull out the context
            context = ' '.join(sent[startIdx+1 : endIdx])

            # add it to the hash table
            if(context in contextHash.keys()):
                prev = contextHash[context]
                setFlag = 0

                for i in xrange(len(prev)):
                    sets = prev[i]

                    if(sets[0] == startWord and sets[1] == endWord):
                        sets[2] += 1
                        prev[i] = sets
                        contextHash[context] = prev
                        setFlag = 1
                        break

                if(setFlag == 0):
                    prev.append([startWord, endWord, 1])
                    contextHash[context] = prev
            else:
                contextHash[context] = [[startWord, endWord, 1]]

        else:
            if(args.verbose):
                pass
                #print 'error found...'

    # initial concept matrix calculations
    for i in xrange(len(contextHash.keys())):
        matrix.append([])
        v = contextHash.keys()
        N = len(v)
        rowCount = 0
        if(indices):
            order.append(v[i], Category_nums[C1], Category_nums[C2])
        else:
            order.append([v[i], C1, C2])

        # row calculations
        for k in xrange(len(contextHash.keys())):

            # pull hash data for indices
            iHash = contextHash[v[i]]
            kHash = contextHash[v[k]]
            currCount = 0

            # loop through hash data and calculate initial counts
            for j in xrange(len(iHash)):
                startWord = iHash[j][0]
                endWord = iHash[j][1]
                count1 = iHash[j][2]

                for o in xrange(len(kHash)):
                    startWord2 = kHash[o][0]
                    endWord2 = kHash[o][1]
                    count2 = kHash[o][2]

                    # found a match where both contexts have occured so increment
                    if(startWord == startWord2 and endWord == endWord2):
                        currCount += min(count1, count2)
                        rowCount += min(count1, count2)

            # add to matrix
            matrix[i].append(currCount)

        # normalize matrix
        mCount = 0
        for l in xrange(len(matrix[i])):
            matrix[i][l] = matrix[i][l] / float(rowCount)

            # increment count for row
            if(matrix[i][l] > 0):
                mCount += 1

        # perform weighting
        if(mCount > 0):
            for l in xrange(len(matrix[i])):
                matrix[i][l] = matrix[i][l] * N/mCount

    if(args.verbose):
        print "Displaying matrix: ", matrix
        matrixDump = open('./matrixDump.txt', 'wb')
        for i in xrange(len(matrix)):
            zz = ''
            for k in xrange(len(matrix[i])):
                zz += str(matrix[i][k]) + ' '
            matrixDump.write(zz[0:len(zz)-1])
        matrixDump.close()
    return (contextHash, matrix, order)

print 'Starting preprocessing..'
subset = preProcess(sample_sentences, rarityThresh=args.rarity, coThresh=args.co)
print 'Constructing the matrix'
matrixHash = constructMatrix(args.cat1, args.cat2, subset, indices=False)
print 'Performing clustering'
centersLabels = performClustering(matrixHash[1], matrixHash[2], K=args.clusters)
print 'Deciding new relations'
decideNewRelation(centersLabels[0], centersLabels[1], matrixHash[0], matrixHash[2])
