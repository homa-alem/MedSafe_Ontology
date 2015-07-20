import numpy as np
import pylab as P

In_file1 = './Data/n_grams_filtered.txt';
f1 = open(In_file1, 'rU')

f1.readline()
for line in f1:
	line.split(',')
bins = [100,125,150,160,170,180,190,200,210,220,230,240,250,275,300]
n, bins, patches = P.hist(data_set, bins, normed=1, histtype='bar', rwidth=0.8)
P.figure()
P.show()