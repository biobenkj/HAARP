__author__ = 'benjaminjohnson'


import csv


infile1 = csv.reader(open('/Users/benjaminjohnson/Desktop/CPreconfirmData/AprAmasterList_updated.csv', 'rU'), dialect='excel')
infile2 = csv.reader(open('/Users/benjaminjohnson/Desktop/CPreconfirmData/HspXmasterList.csv', 'rU'), dialect='excel')
infile3 = csv.reader(open('/Users/benjaminjohnson/Desktop/CPreconfirmData/C2andC3aprAcpReconfirm.csv', 'rU'), dialect='excel')
infile4 = csv.reader(open('/Users/benjaminjohnson/Desktop/CPreconfirmData/C2hspXcpReconfirm.csv', 'rU'), dialect='excel')

MTlist = []
RVfiles = []
Container = []
together = []
combinedaprAdata = []
combinedhspXdata = []
for i in infile1:
    MTlist.append(i[0:])

for j in infile2:
    RVfiles.append(j[0:])

for k in infile3:
    Container.append(k[0:])

for l in infile4:
    together.append(l[0:])

print "Comparing it all, dammit!"

counter = 0
for i in Container:
    nc = counter
    for j in MTlist:
        if j[2] == i[2] and j[3] == i[3]:
            # j.insert(8, i[0])
            combinedaprAdata.append(j)

for k in together:
    for l in RVfiles:
        if l[2] == k[2] and l[3] == k[3]:
            combinedhspXdata.append(l)

shared = 0
apra = len(combinedaprAdata)
hspx = len(combinedhspXdata)

sharedhits = []
apraspecific = []
hspxspecific = []
for hit in combinedaprAdata:
    for drug in combinedhspXdata:
        if hit[2] == drug[2] and hit[3] == drug[3]:
            shared += 1
            sharedhits.append(drug)

for s in combinedaprAdata:
    for a in sharedhits:
        if s[2] == a[2] and s[3] == a[3]:
            break
        elif sharedhits[-1] == a:
            apraspecific.append(s)
print len(apraspecific)

for s in combinedhspXdata:
    for a in sharedhits:
        if s[2] == a[2] and s[3] == a[3]:
            break
        elif sharedhits[-1] == a:
            hspxspecific.append(s)
print len(hspxspecific)

apra = apra - shared
hspx = hspx - shared

print "Shared = %s" % shared
print "AprA = %s" % apra
print "HspX = %s" % hspx

outfile = open('/Users/benjaminjohnson/Desktop/SharedHits.csv', 'wb')
outcsv = csv.writer(outfile)
outcsv.writerow(['Stock_ID', 'Well', 'CP well location', 'CP plate number', '%FI HspX', '%GI HspX', '%FI AprA', '%GI AprA', 'CPreconfirm %FI', 'CPreconfirm %GI', '%FI ~2 uM EC50', '%GI ~2 uM EC50', 'Activity in Macs', 'Cytotoxicity', 'M. smeg %GI', 'Library', 'Catalog Number', 'Compound Name'])
for hit in sharedhits:
    outcsv.writerow(hit)
outfile.close()

outfile = open('/Users/benjaminjohnson/Desktop/AprAspecificHits.csv', 'wb')
outcsv = csv.writer(outfile)
outcsv.writerow(['Stock_ID', 'Well', 'CP well location', 'CP plate number', '%FI HspX', '%GI HspX', '%FI AprA', '%GI AprA', 'CPreconfirm %FI', 'CPreconfirm %GI', '%FI ~2 uM EC50', '%GI ~2 uM EC50', 'Activity in Macs', 'Cytotoxicity', 'M. smeg %GI', 'Library', 'Catalog Number', 'Compound Name'])
for hit in apraspecific:
    outcsv.writerow(hit)
outfile.close()

outfile = open('/Users/benjaminjohnson/Desktop/HspXspecificHits.csv', 'wb')
outcsv = csv.writer(outfile)
outcsv.writerow(['Stock_ID', 'Well', 'CP well location', 'CP plate number', '%FI HspX', '%GI HspX', '%FI AprA', '%GI AprA', 'CPreconfirm %FI', 'CPreconfirm %GI', '%FI ~2 uM EC50', '%GI ~2 uM EC50', 'Activity in Macs', 'Cytotoxicity', 'M. smeg %GI', 'Library', 'Catalog Number', 'Compound Name'])
for hit in hspxspecific:
    outcsv.writerow(hit)
outfile.close()