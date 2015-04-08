__author__ = 'benjaminjohnson'

import os
import csv
import itertools
import matplotlib.pyplot as plt

infile1 = csv.reader(open('/Users/benjaminjohnson/Desktop/MacAct.csv', 'rU'), dialect='excel')
infile2 = csv.reader(open('/Users/benjaminjohnson/Desktop/CPreconfirm.csv', 'rU'), dialect='excel')
# infile3 = csv.reader(open('/Users/benjaminjohnson/Desktop/HundredNanomolarHspX.csv', 'rU'), dialect='excel')

MTlist = []
RVfiles = []
Class1 = 0
Class2 = 0
LessThanTen = 0
Zero = 0
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
        if j[4] == i[0] and j[2] == i[2]:
            # if float(i[11]) == 0.0:
            #     Zero += 1
            #     LessThanTen += 1
            #     if j[6] == 'Class I':
            #         Class1 += 1
            #     elif j[6] == 'Class II':
            #         Class2 += 1
            # elif float(i[11]) <= 10.0:
            #     LessThanTen += 1
            #     if j[6] == 'Class I':
            #         Class1 += 1
            #     elif j[6] == 'Class II':
            #         Class2 += 1
            if float(i[11]) <= 10.0 and float(i[10]) >= 95.0:
                LessThanTen += 1
                if j[6] == 'Class I':
                    Class1 += 1
                elif j[6] == 'Class II':
                    Class2 += 1

print "The number of compounds with less than ten percent cytotox is %d" % LessThanTen
print "The number of compounds with zero percent cytotox is %d" % Zero
print "The number of Class I compounds with less than ten percent cytotox is %d" % Class1
print "The number of Class II compounds with less than ten percent cytotox is %d" % Class2



