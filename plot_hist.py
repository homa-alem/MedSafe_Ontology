import numpy as np
import pylab as P

In_file1 = './Data/n_grams_filtered.txt';
f1 = open(In_file1, 'rU')

data_set = []
f1.readline()
for line in f1:
	data_set.append(float(line.split(', ')[1].strip())*100)
print data_set
bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,275,300]
n, bins, patches = P.hist(data_set, bins, normed=1, histtype='bar', rwidth=0.8)
print n
print bins
print patches
P.show()