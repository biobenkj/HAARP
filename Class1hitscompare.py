__author__ = 'benjaminjohnson'


import csv

infile1 = csv.reader(open('/Users/benjaminjohnson/Desktop/CPreconfirmData/C1hits.csv', 'rU'), dialect='excel')
infile2 = csv.reader(open('/Users/benjaminjohnson/Desktop/CPreconfirmData/amlcp.csv', 'rU'), dialect='excel')

MTlist = []
RVfiles = []
Container = []
together = []
combineddata = []
for i in infile1:
    MTlist.append(i[0:])

for j in infile2:
    RVfiles.append(j[0:])

print len(MTlist)
print len(RVfiles)

counter = 0
for i in MTlist:
    nc = counter
    for j in RVfiles:
        if j[0] == i[5] and j[1] == i[2]:
            # j.insert(8, i[0])
            combineddata.append(j)
            # counter += 1
    # if counter == nc:
    #     together.append(['',i,'',''])
# for i in combineddata:
#     for j in Container:
#         if i[1] == j[0]:
#             i.insert(4, j[1])
#             i.insert(7, j[4])
# for i in Container:
#     nc = counter
#     for j in RVfiles:
#         if j[6] == i[2] and j[7] == i[3]:
#             # together.append(j)
#             j.insert(0, i[0])
#             j.insert(1, i[1])
#             together.append(j)
#
# print len(together)
#
# for space in RVfiles:
#     if len(space) < 18:
#         # space.insert(8, '-')
#         space.insert(14, '-')

outfile = open('/Users/benjaminjohnson/Desktop/outfile.csv', 'wb')
outcsv = csv.writer(outfile)
outcsv.writerow(['Stock_ID', 'Well', 'CP well location', 'CP plate number', '%FI HspX', '%GI HspX', '%FI AprA', '%GI AprA', 'CPreconfirm %FI', 'CPreconfirm %GI', '%FI ~2 uM EC50', '%GI ~2 uM EC50', 'Activity in Macs', 'Cytotoxicity', 'M. smeg %GI', 'Library', 'Catalog Number', 'Compound Name'])
pxlist = []
pylist = []
hitlistx = []
hitlisty = []
for i in combineddata:
    outcsv.writerow(i)
#    pxlist.append(float(i[0]))
#    pylist.append(float(i[1]))
#    if i[0] > 25.0 and i[1] < 25.0:
#        hitlistx.append(float(i[0]))
#        hitlisty.append(float(i[1]))
#
#
#plt.xlim(-5,100)
#plt.ylim(-5,100)
#plt.xlabel("Activity in macrophages percent inhibition")
#plt.ylabel("Cytotoxicity in macrophages percent inhibition")
#plt.title("Scatter plot of all data from the hspX-specific cherry picks")
## plt.legend([t1, t2, t3, t4],['<25% FI', '25-50% FI', '50-75% FI', '>75% FI'], loc=4, numpoints=1)
#plt.axvline(0,-50,120,linestyle = '--')
#plt.axhline(0,-50,120,linestyle = '--')
#plt.axhline(25,-50,120,linestyle = '--')
#plt.axhline(-25,-50,120,linestyle = '--')
#plt.axhline(50,-50.120, linestyle = '--')
#plt.axhline(75,-50,120,linestyle = '--')
#plt.axhline(100,-50,120,linestyle = '--')
#plt.axvline(25,-50,120,linestyle = '--')
#plt.axvline(50,-50,120,linestyle = '--')
#plt.axvline(75,-50,120,linestyle = '--')
#plt.axvline(100,-50,120,linestyle = '--')
#plt.axvline(-25,-50,120,linestyle = '--')
##    plt.axvline(-50,-50.120, linestyle = '--')
##    plt.axvline(-75,-120,120,linestyle = '--')
#plt.plot(pxlist, pylist, 'o', color='0.95')
#plt.plot(hitlistx, hitlisty, 'r')
#of = open("/Users/benjaminjohnson/Desktop" + "/" + 'Scatter plot of all data.png', "w")
#plt.savefig("/Users/benjaminjohnson/Desktop" + "/" + 'Scatter plot of all data.png', dpi=300)
#of.close()
#plt.clf()
