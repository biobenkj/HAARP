__author__ = 'benjaminjohnson'

import os
import csv
import itertools
import matplotlib.pyplot as plt

infile1 = csv.reader(open('/Users/benjaminjohnson/Desktop/R01_Data_Analysis/1150_List_1.csv', 'rU'), dialect='excel')
infile2 = csv.reader(open('/Users/benjaminjohnson/Desktop/R01_Data_Analysis/1150_List_2.csv', 'rU'), dialect='excel')
infile3 = csv.reader(open('/Users/benjaminjohnson/Desktop/R01_Data_Analysis/Excluded_wells.csv', 'rU'), dialect='excel')
infile4 = csv.reader(open('/Users/benjaminjohnson/Desktop/R01_Data_Analysis/1149_data_list.csv', 'rU'), dialect='excel')
infile5 = csv.reader(open('/Users/benjaminjohnson/Desktop/R01_Data_Analysis/AprAspecificCytoxandActInMacs.csv', 'rU'), dialect='excel')
infile6 = csv.reader(open('/Users/benjaminjohnson/Desktop/R01_Data_Analysis/CommonCytoxandActInMacs.csv', 'rU'), dialect='excel')
infile7 = csv.reader(open('/Users/benjaminjohnson/Desktop/R01_Data_Analysis/AprAspecificEC50master.csv', 'rU'), dialect='excel')

MTlist = []
RVfiles = []
Container = []
HspXdata = []
AprAspecific = []
Common = []
EC50 = []
grtfiftygrowth = []
for i in infile1:
    MTlist.append(i[0:])

for j in infile2:
    RVfiles.append(j[0:])

for k in infile3:
    Container.append(k[0:])

# for l in infile4:
#     HspXdata.append(l[:0])

for l in infile4:
    if l[3] != 'Y' and l[11] == 'Y' or l[12] == 'Y':
        HspXdata.append(l)

for m in infile5:
    AprAspecific.append(m[0:])

for n in infile6:
    Common.append(n[0:])

for hit in MTlist:
    grtfiftygrowth.append(hit[0:])

# for hit in MTlist:
#     if float(hit[11]) >= 50.0 and hit[3] != 'Y':
#         grtfiftygrowth.append(hit)

for comp in RVfiles:
    grtfiftygrowth.append(comp[0:])
# for comp in RVfiles:
#     if float(comp[11]) >= 50.0 and comp[3] != 'Y':
#         grtfiftygrowth.append(comp)

for o in infile7:
    EC50.append(o[0:])

print len(grtfiftygrowth)


for exclude in Container:
    for drug in grtfiftygrowth:
        if exclude[1] == drug[1] and exclude[0] == drug[0]:
            idx = grtfiftygrowth.index(drug)
            grtfiftygrowth.remove(grtfiftygrowth[idx])

print len(grtfiftygrowth)

comparedata = []

print "Massive comparison time!"

for hspx in HspXdata:
    for compare in grtfiftygrowth:
        if hspx[1] == compare[1] and hspx[0] == compare[0]:
            comparedata.append([hspx[0], hspx[1], hspx[7], hspx[8], compare[10], compare[11]])
# for compare in grtfiftygrowth:
#     for hspx in HspXdata:
#         if compare[1] == hspx[1] and compare[0] == hspx[0]:
#             comparedata.append([compare[0], compare[1], compare[10], compare[11], hspx[7], hspx[8]])

print "Finding compounds now..."

cp = '/Users/benjaminjohnson/Desktop/Platemaps'
for f in os.listdir(cp):
    extension = os.path.splitext(f)[1]   #finds the extension of the file, which for our purposes needs to be .txt
    if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
        filename = cp + "/" + f
        data1 = csv.reader(open(filename, 'rU'), dialect='excel')
        for info in data1:
            for a in range(len(comparedata)):
                if comparedata[a][1] == info[1] and comparedata[a][0] == info[0]:
                    comparedata[a].append(info[2])
                    comparedata[a].append(info[6])
                    comparedata[a].append(info[7])

print 'Now looking at EC50, cytotox, and macrophage data...'

for apracytox in AprAspecific:
    for anti in range(len(comparedata)):
        if apracytox[4] == comparedata[anti][0] and apracytox[5] == comparedata[anti][1]:
            comparedata[anti].insert(6, apracytox[0])
            comparedata[anti].insert(7, apracytox[1])
            comparedata[anti].insert(2, apracytox[2])
            comparedata[anti].insert(3, apracytox[3])

for comcytox in Common:
    for anti in range(len(comparedata)):
        if comcytox[4] == comparedata[anti][0] and comcytox[5] == comparedata[anti][1]:
            comparedata[anti].insert(6, comcytox[0])
            comparedata[anti].insert(7, comcytox[1])
            comparedata[anti].insert(2, comcytox[2])
            comparedata[anti].insert(3, comcytox[3])

for ec50 in EC50:
    for anti in range(len(comparedata)):
        if ec50[4] == comparedata[anti][0] and ec50[5] == comparedata[anti][1]:
            comparedata[anti].insert(8, ec50[0])
            comparedata[anti].insert(9, ec50[1])
            # comparedata[anti].insert(2, ec50[2])
            # comparedata[anti].insert(3, ec50[3])

print "Cleaning up the data table..."

for pretty in range(len(comparedata)):
    if len(comparedata[pretty]) < 13:
        comparedata[pretty].insert(6, '-')
        comparedata[pretty].insert(7, '-')
        comparedata[pretty].insert(8, '-')
        comparedata[pretty].insert(9, '-')
        comparedata[pretty].insert(2, '-')
        comparedata[pretty].insert(3, '-')

print "Writing the data table to outfile.csv..."

outfile = open('/Users/benjaminjohnson/Desktop/outfile.csv', 'wb')
outcsv = csv.writer(outfile)
# outcsv.writerow(["100 Nanomolar FI", "100 Nanomolar GI", "Submicromolar FI", "Submicromolar GI", "Activity in Macs", "Cytotoxicity", "Confirmation FI", "Confirmation GI", "CP Well location", "Plate number", "Library", "Library well location", "Class type call from original screen", "Vendor", "Compound catalog number", "Compound name"])
outcsv.writerow(['Stock_ID', 'Well', 'CP well location', 'CP plate number', '%FI HspX', '%GI HspX', '%FI AprA', '%GI AprA', '%FI ~2 uM EC50', '%GI ~2 uM EC50', 'Activity in Macs', 'Cytotoxicity', 'Library', 'Catalog Number', 'Compound Name'])
pxlist = []
pylist = []
print "Plotting!"
for dat in comparedata:
    pxlist.append(dat[5])
    pylist.append(dat[7])
hitlistx = []
hitlisty = []
for newdat in comparedata:
    if newdat[2] != '-':
        hitlistx.append(newdat[5])
        hitlisty.append(newdat[7])
for i in comparedata:
    outcsv.writerow(i)

plt.xlim(-50,150)
plt.ylim(-50,120)
plt.xlabel("Percent growth inhibition at acidic pH (% positive control)")
plt.ylabel("Percent growth inhibition at neutral pH (% positive control)")

plt.axvline(0,-50,150,linestyle = '--')
plt.axhline(0,-50,150,linestyle = '--')
plt.axhline(25,-50,150,linestyle = '--')
plt.axhline(-25,-50,150,linestyle = '--')
plt.axhline(50,-50.150, linestyle = '--')
plt.axhline(75,-50,150,linestyle = '--')
plt.axhline(100,-50,150,linestyle = '--')
plt.axvline(25,-50,150,linestyle = '--')
plt.axvline(50,-50,150,linestyle = '--')
plt.axvline(75,-50,150,linestyle = '--')
plt.axvline(100,-50,150,linestyle = '--')
plt.axvline(-25,-50,150,linestyle = '--')

plt.plot(pxlist, pylist, 'o', color='0.95')
plt.plot(hitlistx, hitlisty, 'ro')
of = open("/Users/benjaminjohnson/Desktop" + "/" + 'Scatter plot of all data with CP.png', "w")
plt.savefig("/Users/benjaminjohnson/Desktop" + "/" + 'Scatter plot of all data with CP.png', dpi=300)
of.close()
plt.clf()
plt.xlim(-50,150)
plt.ylim(-50,120)
plt.xlabel("Percent growth inhibition at acidic pH (% positive control)")
plt.ylabel("Percent growth inhibition at neutral pH (% positive control)")

plt.axvline(0,-50,150,linestyle = '--')
plt.axhline(0,-50,150,linestyle = '--')
plt.axhline(25,-50,150,linestyle = '--')
plt.axhline(-25,-50,150,linestyle = '--')
plt.axhline(50,-50.150, linestyle = '--')
plt.axhline(75,-50,150,linestyle = '--')
plt.axhline(100,-50,150,linestyle = '--')
plt.axvline(25,-50,150,linestyle = '--')
plt.axvline(50,-50,150,linestyle = '--')
plt.axvline(75,-50,150,linestyle = '--')
plt.axvline(100,-50,150,linestyle = '--')
plt.axvline(-25,-50,150,linestyle = '--')
plt.plot(pxlist, pylist, 'bo')
oftwo = open("/Users/benjaminjohnson/Desktop" + "/" + 'Scatter plot of all data.png', "w")
plt.savefig("/Users/benjaminjohnson/Desktop" + "/" + 'Scatter plot of all data.png', dpi=300)
oftwo.close()
plt.clf()