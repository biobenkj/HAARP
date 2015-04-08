__author__ = 'benjaminjohnson'

import os
import csv
import itertools
import matplotlib.pyplot as plt

infile1 = csv.reader(open('/Users/benkjohnson/Desktop/Concatenated_Function_List.csv', 'rU'), dialect='excel')
infile2 = csv.reader(open('/Users/benkjohnson/Desktop/DEph017_Rv_update.csv', 'rU'), dialect='excel')
# infile3 = csv.reader(open('/Users/benjaminjohnson/Desktop/HundredNanomolarHspX.csv', 'rU'), dialect='excel')

MTlist = []
RVfiles = []

for i in infile1:
    MTlist.append(i[0:])

for j in infile2:
    RVfiles.append(j[0:])

# for k in infile3:
#     Container.append(k[0:])

print len(MTlist)
print len(RVfiles)

for j in RVfiles:
    for i in MTlist:
        if j[0] == i[0]:
            print "Writing things..."
            j.append(i[1])
            j.append(i[2])
            j.append(i[5])

print "Writing the csv out..."
outf = open('/Users/benkjohnson/Desktop/DEpH017_withFuncs.csv', 'wb')
outcsv = csv.writer(outf)
for i in RVfiles:
    outcsv.writerow(i)
outf.close()
print "Closed."
