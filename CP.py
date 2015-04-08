__author__ = 'benjaminjohnson'

import os
import subprocess
import datetime
import csv
import itertools
from pylab import *
import numpy as np

plate_ID = []
GFP = []  #empty list that will eventually contain the list of lists of data
OD = []
TWENTYFIVEGFP = []
TWENTYFIVEOD = []
THIRTYFIVEGFP = []
THIRTYFIVEOD = []
FIFTYGFP = []
FIFTYOD = []
SEVENTYFIVEGFP = []
SEVENTYFIVEOD = []
HUNDREDGFP = []
HUNDREDOD = []
NORMALGFPDATA = []

NORMALODDATA = []

GFPZFACTOR = []
CLASSIHIT = []
CLASSIIHIT = []
CLASSIIIHIT = []


def find_path():
    """Asks the computer for the path to the the user's location.
    From there is created a path to the desktop
    """
    desk_path = subprocess.Popen("echo $HOME", shell=True, stdout=subprocess.PIPE).stdout.readline().strip("\n")+"/Desktop"
    #Next we need to check that the path actually exits on the computer
    #if it doesn't it will print out a statement to the user and ask them to manually enter the path, or quit the program
    if not os.path.lexists(desk_path):
        print "Unable to find the Desktop."
        while not os.path.lexists(desk_path):
            desk_path = str(raw_input("Please enter the file path for the folder location or enter quit to exit the program:"))
            if desk_path.upper() == "Q":
                quit()
            if not os.path.lexists(desk_path):
                print("Invalid file path. The path you have selected does not exist or was not written correctly. \nAn example of path on Mac OS X: /Users/yourusername/Desktop")
    return desk_path


def create_folder():
    """It creates a default folder 'HTMAD_Data' on the desktop if it
    doesn't already exist. And then prompts the user to create a
    subfolder in HTMAD_Data to store all of the data from the run.
    """
    print "Creating a folder with which all the generated data will be placed."
    print "Default subfolder location will be in 'HTS_Data' which is located on the Desktop"
    defined_path = find_path() + "/HTS_Data"
    now = datetime.datetime.now()
    #all data folder will go into HTMAD_Data, if it doesn't already exist from previous runs it wil be created
    if not os.path.isdir(defined_path):
        os.mkdir(defined_path)
        print "Created folder 'HTS_Data' on the Desktop"
    new_fold = now.strftime("%Y-%m-%d")
    defined_full_path = defined_path + "/" + new_fold  #path to the subfolder inside HTMAD_Data
    #if the specified folder is a valid directory name then it will create the folder and exit the function
    if not os.path.isdir(defined_full_path):
         os.mkdir(defined_full_path)
    else:
        taken = new_fold
        num = 1
        new_fold += "_" + str(num)
        defined_full_path = defined_path + "/" + new_fold
        while os.path.isdir(defined_full_path):
            num += 1
            new_fold = taken + "_" + str(num)
            defined_full_path = defined_path + "/" + new_fold
        print "'" + taken + "' was already a directory in HTS_Data, '" + new_fold + "' was used instead for this run."
        os.mkdir(defined_full_path)

    print "Created subfolder '" + new_fold + "' in the path: " + defined_full_path
    return defined_full_path


def find_input_folder():
    """This function, with prompts from the user, finds the location of the
    data to run the peak picking algorithm. It will look on the desktop
    and will go into a subfolder if necessary. The function returns the
    path to the folder containing the data. All of the user input will be
    bypassed if the user used the -i option in the beginning
    """
    path = find_path()
    input = str(raw_input("Please enter the name of the folder on the Desktop containing the cherry pick data:"))
    data_path = path + "/" + input
    while not os.path.isdir(data_path):
        new_input = str(raw_input("Sorry the software could not be find that folder on the desktop, try typing the folder name again or Q to quit:"))
        if new_input.upper() == "Q":
            quit()
        data_path = path + "/" + new_input
    return data_path


def read_input(infile):
    """Reads in files from the user specified location. These files need to be
    .txt files and in two columns, an x and y, separated by a single space. The
    data will then be separated into two lists, on for x value and one of y values.
    The list of x or y values contain many lists, one for each spectra, that
    contain the x or y values, respectively, for the spectra. It then returns the
    list of y lists.
    """

    print "Reading in files"

    for file in os.listdir(infile):  #iterating through the files contained inside of a parent folder
        gfpruns = []
        odruns = []
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv":  #checking if the file is a text file (ie ends in .txt)
            filename = infile + "/" + file
            data = csv.reader(open(filename, 'rU'), dialect='excel')
            gfp = False
            gfpcontainer = []
            odcontainer = []
            for rows in data:
                if len(rows) >= 7:
                    if rows[7] == 'Meas A':
                        plate_ID.append(rows[2])
                        gfp = True
                    if rows[0] in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P'] and gfp == True:
                        if rows[0] == 'A':
                            gfpcontainer.append(map(int, rows[1:25]))
                        elif rows[0] == 'P':
                            gfpcontainer.append(map(int, rows[1:25]))
                            gfp = False
                            gfpruns.append(gfpcontainer)
                            gfpcontainer = []
                        else:
                            gfpcontainer.append(map(int, rows[1:25]))
                    elif rows[0] in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']:
                        if rows[0] == 'P':
                            odcontainer.append(map(float, rows[1:25]))
                            odruns.append(odcontainer)
                            odcontainer = []
                        elif rows[1] == '- ':
                            break
                        else:
                            odcontainer.append(map(float, rows[1:25]))
                else:
                    continue
        else:
            continue
        GFP.append(gfpruns)
        OD.append(odruns)
    return GFP, OD, plate_ID


def normalizebyz(x, y):
    runavgneggfp = []
    runavgposgfp = []
    runavgnegod = []
    runavgposod = []
    for i, j in itertools.izip(x, y):
        runneggfpcontainer = []
        runposgfpcontainer = []
        runnegodcontainer = []
        runposodcontainer = []

        for m, n in itertools.izip(i, j):

            neggfp = []
            posgfp = []

            negod = []
            posod = []
            for q, r in itertools.izip(m, n):
                negg,nego = q[-2],r[-2]
                posg,poso = q[-1],r[-1]
                neggfp.append(negg)
                posgfp.append(posg)
                negod.append(nego)
                posod.append(poso)
            ang = sum(neggfp)/len(neggfp)
            apg = sum(posgfp)/len(posgfp)
            ano = sum(negod)/len(negod)
            apo = sum(posod)/len(posod)

            stdneg = ((np.std(neggfp))*3)
            stdpos = ((np.std(posgfp))*3)

            z = 1.0-((stdpos+stdneg)/abs(apg-ang))

            if z >= 0.5:
                runneggfpcontainer.append(ang)
                runposgfpcontainer.append(apg)
                runnegodcontainer.append(ano)
                runposodcontainer.append(apo)
                GFPZFACTOR.append(z)
        runavgneggfp.append(runneggfpcontainer)
        runavgposgfp.append(runposgfpcontainer)
        runavgnegod.append(runnegodcontainer)
        runavgposod.append(runposodcontainer)

    print "...Read in %d files...\n...Read in %d plates..." % (len(runavgneggfp), len(plate_ID))
    for i in range(len(x)):




        normalgfp = []

        normgfpcontainer = []

        meanneggfp = np.average(runavgneggfp[i])
        meanposgfp = np.average(runavgposgfp[i])
        for x_i in x[i]:
            for x_ii in x_i:
                for x_iii in x_ii:
                    normgfp = (float(meanneggfp-x_iii))/(float(meanneggfp-meanposgfp))*100
                    normgfpcontainer.append(normgfp)
                del normgfpcontainer[-1]
                del normgfpcontainer[-1]
                normalgfp.append(normgfpcontainer)
                normgfpcontainer = []
            NORMALGFPDATA.append(normalgfp)
            normalgfp = []

    for i in range(len(y)):
        meannegod = np.average(runavgnegod[i])
        meanposod = np.average(runavgposod[i])
        normodcontainer = []
        normalod = []
        for x in y[i]:
            for xi in x:
                for xii in xi:
                    normod = ((meannegod-xii)/(meannegod-meanposod))*100
                    normodcontainer.append(normod)
                del normodcontainer[-1]
                del normodcontainer[-1]
                normalod.append(normodcontainer)
                normodcontainer = []

            NORMALODDATA.append(normalod)
            normalod = []
    return


def bindata(x,y):
    for i,j in itertools.izip(x,y):
        for m,n in itertools.izip(i,j):
            for a,b in itertools.izip(m,n):
                if a <= 25:
                    if a >= -50 and b >= -50:
                        TWENTYFIVEGFP.append(a)
                        TWENTYFIVEOD.append(b)
                elif a <= 50:
                    if b >= -50:
                        FIFTYGFP.append(a)
                        FIFTYOD.append(b)
                        if a >= 35:
                            THIRTYFIVEGFP.append(a)
                            THIRTYFIVEOD.append(b)
                elif a <= 75:
                    if b >= -50:
                        SEVENTYFIVEGFP.append(a)
                        SEVENTYFIVEOD.append(b)
                elif a > 75:
                    if b >= -50:
                        HUNDREDGFP.append(a)
                        HUNDREDOD.append(b)

    return


def findcompound():
    path = find_path()
    input = str(raw_input("Please enter the name of the folder on the Desktop containing the plate IDs:"))
    plate_path = path + "/" + input
    while not os.path.isdir(plate_path):
        new_input = str(raw_input("Sorry the software could not be find that folder on the desktop, try typing the folder name again or Q to quit:"))
        if new_input.upper() == "Q":
            quit()
        plate_path = path + "/" + new_input
    input = str(raw_input("Please enter the name of the folder on the Desktop containing the compound libraries:"))
    comp_path = path + "/" + input
    while not os.path.isdir(comp_path):
        new_input = str(raw_input("Sorry the software could not be find that folder on the desktop, try typing the folder name again or Q to quit:"))
        if new_input.upper() == "Q":
            quit()
        comp_path = path + "/" + new_input
    abovefiftygfp = SEVENTYFIVEGFP + HUNDREDGFP
    abovethirtyfivegfp = THIRTYFIVEGFP + SEVENTYFIVEGFP + HUNDREDGFP
    belowfiftygfp = TWENTYFIVEGFP + FIFTYGFP
    odclassIcut = []
    odclassIIIcut = []
    print "...Finding compound IDs..."
    alldata = TWENTYFIVEOD + FIFTYOD + SEVENTYFIVEOD + HUNDREDOD
    for od in alldata:
        if od <= 35.0:
            odclassIcut.append(od)
        elif od >= 50.0:
            odclassIIIcut.append(od)
    countplate = 0
    countrow = 0
    rowdict = {0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G', 7:'H', 8:'I', 9:'J', 10:'K', 11:'L', 12:'M', 13:'N', 14:'O', 15:'P'}

    for plateg, plateo in itertools.izip(NORMALGFPDATA, NORMALODDATA):
        for rowg, rowo in itertools.izip(plateg,plateo):
            for datg in range(len(rowg)):
                if rowg[datg] in abovefiftygfp and rowo[datg] in odclassIIIcut:
                    if datg < 9:
                        CLASSIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]])
                    else:
                        CLASSIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+str(datg+1),plate_ID[countplate]])
                elif rowg[datg] in belowfiftygfp and rowo[datg] in odclassIIIcut:
                    if (rowo[datg]/rowg[datg]) >= 1.5 or (rowo[datg]/rowg[datg]) < 0:
                        if datg < 9:
                            CLASSIIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]])
                        else:
                            CLASSIIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+str(datg+1),plate_ID[countplate]])
                elif rowg[datg] in abovethirtyfivegfp:
                    if rowg[datg] >= 35.0 and (rowg[datg]/rowo[datg]) >= 1.5 or (rowg[datg]/rowo[datg]) < 0:
                        if datg < 9:
                            CLASSIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]])
                        else:
                            CLASSIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+str(datg+1),plate_ID[countplate]])
                    # elif (rowg[datg]/rowo[datg]) >= 1.5 or (rowg[datg]/rowo[datg]) < 0:
                    #     if datg < 9:
                    #         CLASSIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]])
                    #     else:
                    #         CLASSIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+str(datg+1),plate_ID[countplate]])

            countrow += 1
        countrow = 0
        countplate += 1

    print "...Still working..."
    print len(CLASSIHIT)
    print len(CLASSIIHIT)

    for file in os.listdir(plate_path): #iterating through the files contained inside of a parent folder
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
            filename = plate_path + "/" + file
            data = csv.reader(open(filename, 'rU'), dialect='excel')
            for rows in data:
                for hits in CLASSIHIT:
                    plate_id = hits[3]
                    well_id = hits[2]
                    if well_id == rows[2] and plate_id == rows[3]:
                        hits.append(rows[0])
                        hits.append(rows[1])
                for antibio in CLASSIIHIT:
                        pid = antibio[3]
                        wid = antibio[2]
                        if wid == rows[2] and pid == rows[3]:
                            antibio.append(rows[0])
                            antibio.append(rows[1])
                for h in CLASSIIIHIT:
                    pd = h[3]
                    wd = h[2]
                    if wd == rows[2] and pd == rows[3]:
                        h.append(rows[0])
                        h.append(rows[1])
    print len(CLASSIHIT)
    print len(CLASSIIHIT)

    classIplateid = []
    classIplateloc = []
    for idhits in CLASSIHIT:
        if len(idhits) >= 5:
            classIplateid.append(idhits[4])
            classIplateloc.append(idhits[5])
    classIIplateid = []
    classIIplateloc = []
    for idhitstwo in CLASSIIHIT:
        if len(idhitstwo) >= 5:
            classIIplateid.append(idhitstwo[4])
            classIIplateloc.append(idhitstwo[5])
    classIIIplateid = []
    classIIIplateloc = []
    for idhitsthree in CLASSIIIHIT:
        if len(idhitsthree) >= 5:
            classIIIplateid.append(idhitsthree[4])
            classIIIplateloc.append(idhitsthree[5])

    print len(classIplateid) + len(classIIplateid)

    for file in os.listdir(comp_path):
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
            filename = comp_path + "/" + file
            data1 = csv.reader(open(filename, 'rU'), dialect='excel')
            for info in data1:
                for a in range(len(classIplateid)):
                    if classIplateid[a] == info[0] and classIplateloc[a] == info[1]:
                        CLASSIHIT[a].append(info[2])
                for b in range(len(classIIplateid)):
                    if classIIplateid[b] == info[0] and classIIplateloc[b] == info[1]:
                        CLASSIIHIT[b].append(info[2])
                for c in range(len(classIIIplateid)):
                    if classIIIplateid[c] == info[0] and classIIIplateloc[c] == info[1]:
                        CLASSIIIHIT[c].append(info[2])

    cp = find_path() + '/Platemaps'
    for file in os.listdir(cp):
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
            filename = cp + "/" + file
            data1 = csv.reader(open(filename, 'rU'), dialect='excel')
            for info in data1:
                for a in range(len(classIplateid)):
                    if classIplateid[a] == info[0] and classIplateloc[a] == info[1]:
                        CLASSIHIT[a].append(info[2])
                        CLASSIHIT[a].append(info[6])
                        CLASSIHIT[a].append(info[7])
                for b in range(len(classIIplateid)):
                    if classIIplateid[b] == info[0] and classIIplateloc[b] == info[1]:
                        CLASSIIHIT[b].append(info[2])
                        CLASSIIHIT[b].append(info[6])
                        CLASSIIHIT[b].append(info[7])
                for c in range(len(classIIIplateid)):
                    if classIIIplateid[c] == info[0] and classIIIplateloc[c] == info[1]:
                        CLASSIIIHIT[c].append(info[2])
                        CLASSIIIHIT[c].append(info[6])
                        CLASSIIIHIT[c].append(info[7])

    c1hits = []
    for hit in CLASSIHIT:
        if len(hit) > 7:
            c1hits.append(hit)

    c2hits = []
    for hit in CLASSIIHIT:
        if len(hit) > 7:
            c2hits.append(hit)

    c3hits = []
    for hit in CLASSIIIHIT:
        if len(hit) > 7:
            c3hits.append(hit)

    return c1hits, c2hits, c3hits


def findcompound_allhits():
    path = find_path()
    input = str(raw_input("Please enter the name of the folder on the Desktop containing the plate IDs:"))
    plate_path = path + "/" + input
    while not os.path.isdir(plate_path):
        new_input = str(raw_input("Sorry the software could not be find that folder on the desktop, try typing the folder name again or Q to quit:"))
        if new_input.upper() == "Q":
            quit()
        plate_path = path + "/" + new_input
    input = str(raw_input("Please enter the name of the folder on the Desktop containing the compound libraries:"))
    comp_path = path + "/" + input
    while not os.path.isdir(comp_path):
        new_input = str(raw_input("Sorry the software could not be find that folder on the desktop, try typing the folder name again or Q to quit:"))
        if new_input.upper() == "Q":
            quit()
        comp_path = path + "/" + new_input
    allhits = []
    print "...Finding compound IDs..."
    alldata = TWENTYFIVEOD + FIFTYOD + SEVENTYFIVEOD + HUNDREDOD
    allgfp = TWENTYFIVEGFP + FIFTYGFP + SEVENTYFIVEGFP + HUNDREDGFP
    countplate = 0
    countrow = 0
    rowdict = {0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G', 7:'H', 8:'I', 9:'J', 10:'K', 11:'L', 12:'M', 13:'N', 14:'O', 15:'P'}

    for plateg, plateo in itertools.izip(NORMALGFPDATA, NORMALODDATA):
        for rowg, rowo in itertools.izip(plateg,plateo):
            for datg in range(len(rowg)):
                if rowg[datg] in allgfp and rowo[datg] in alldata:
                    if datg < 9:
                        allhits.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]])
                    else:
                        allhits.append([rowg[datg],rowo[datg],rowdict[countrow]+str(datg+1),plate_ID[countplate]])
                    # elif (rowg[datg]/rowo[datg]) >= 1.5 or (rowg[datg]/rowo[datg]) < 0:
                    #     if datg < 9:
                    #         CLASSIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]])
                    #     else:
                    #         CLASSIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+str(datg+1),plate_ID[countplate]])

            countrow += 1
        countrow = 0
        countplate += 1

    print "...Still working..."
    print len(CLASSIHIT)
    print len(CLASSIIHIT)

    for file in os.listdir(plate_path): #iterating through the files contained inside of a parent folder
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
            filename = plate_path + "/" + file
            data = csv.reader(open(filename, 'rU'), dialect='excel')
            for rows in data:
                for hits in allhits:
                    plate_id = hits[3]
                    well_id = hits[2]
                    if well_id == rows[2] and plate_id == rows[3]:
                        hits.append(rows[0])
                        hits.append(rows[1])

    classIplateid = []
    classIplateloc = []
    for idhits in allhits:
        if len(idhits) >= 5:
            classIplateid.append(idhits[4])
            classIplateloc.append(idhits[5])


    for file in os.listdir(comp_path):
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
            filename = comp_path + "/" + file
            data1 = csv.reader(open(filename, 'rU'), dialect='excel')
            for info in data1:
                for a in range(len(classIplateid)):
                    if classIplateid[a] == info[0] and classIplateloc[a] == info[1]:
                        allhits[a].append(info[2])

    cp = find_path() + '/Platemaps'
    for file in os.listdir(cp):
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
            filename = cp + "/" + file
            data1 = csv.reader(open(filename, 'rU'), dialect='excel')
            for info in data1:
                for a in range(len(classIplateid)):
                    if classIplateid[a] == info[0] and classIplateloc[a] == info[1]:
                        allhits[a].append(info[2])
                        allhits[a].append(info[6])
                        allhits[a].append(info[7])

    c1hits = []
    for hit in allhits:
        if len(hit) > 7:
            c1hits.append(hit)

    return c1hits


def makecsvfile(path, c1, c2, c3):
    print "...Making .csv files for each class of hits..."
    outf = open(path + '/' + 'Class I hits.csv', 'wb')
    outcsv = csv.writer(outf)
    outcsv.writerow(['Class I hits are binned at > 35% GFP inhibition and at least a 1.5-fold difference between GFP and OD'])
    outcsv.writerow(["Fluorescence inhibition (% of positive control)", "Growth inhibition (% of positive control)", "CP Well location", "Plate number", "Library", "Library well location", "Class type call from original screen", "Vendor", "Compound catalog number", "Compound name"])
    for i in c1:
        outcsv.writerow(i)
    outf1 = open(path + '/' + 'Class II hits.csv', 'wb')
    outcsv = csv.writer(outf1)
    outcsv.writerow(['Class II hits are binned at > 50% GFP inhibition and > 50% growth inhibition'])
    outcsv.writerow(["Fluorescence inhibition (% of positive control)", "Growth inhibition (% of positive control)", "CP Well location", "Plate number", "Library", "Library well location", "Class type call from original screen", "Vendor", "Compound catalog number", "Compound name"])
    for j in c2:
        outcsv.writerow(j)
    outf1 = open(path + '/' + 'Class III hits.csv', 'wb')
    outcsv = csv.writer(outf1)
    outcsv.writerow(['Class III hits are binned at > 50% growth inhibition and at least a 3-fold difference between GFP and OD'])
    outcsv.writerow(["Fluorescence inhibition (% of positive control)", "Growth inhibition (% of positive control)", "CP Well location", "Plate number", "Library", "Library well location", "Class type call from original screen", "Vendor", "Compound catalog number", "Compound name"])
    for k in c3:
        outcsv.writerow(k)
#    allod = TWENTYFIVEOD + FIFTYOD + SEVENTYFIVEOD + HUNDREDOD
#    allgfp = TWENTYFIVEGFP + FIFTYGFP + SEVENTYFIVEGFP + HUNDREDGFP
#    outf2 = open(path + '/' + 'All Data.csv', 'wb')
#    outcsv = csv.writer(outf2)
#    outcsv.writerow(["OD", "GFP"])
#    for i,j in itertools.izip(allod, allgfp):
#        outcsv.writerow(i)
#        outcsv.writerow(j)
    return


def makecsvfile_allhits(path, c1):
    print "...Making .csv files for each class of hits..."
    outf = open(path + '/' + 'Class I hits.csv', 'wb')
    outcsv = csv.writer(outf)
    outcsv.writerow(["Fluorescence inhibition (% of positive control)", "Growth inhibition (% of positive control)", "CP Well location", "Plate number", "Library", "Library well location", "Class type call from original screen", "Vendor", "Compound catalog number", "Compound name"])
    for i in c1:
        outcsv.writerow(i)

#    allod = TWENTYFIVEOD + FIFTYOD + SEVENTYFIVEOD + HUNDREDOD
#    allgfp = TWENTYFIVEGFP + FIFTYGFP + SEVENTYFIVEGFP + HUNDREDGFP
#    outf2 = open(path + '/' + 'All Data.csv', 'wb')
#    outcsv = csv.writer(outf2)
#    outcsv.writerow(["OD", "GFP"])
#    for i,j in itertools.izip(allod, allgfp):
#        outcsv.writerow(i)
#        outcsv.writerow(j)
    return


def plotallclassesdata(CLASSIHIT, CLASSIIHIT, CLASSIIIHIT, folder):
    print "...Plotting data..."
    x = False
    y = False
    z = False
    plt.plot(TWENTYFIVEOD,TWENTYFIVEGFP, 'o', color='0.95')
    plt.plot(FIFTYOD,FIFTYGFP, 'o', color='0.95')
    plt.plot(SEVENTYFIVEOD,SEVENTYFIVEGFP, 'o', color='0.95')
    plt.plot(HUNDREDOD,HUNDREDGFP, 'o', color='0.95')
    dmso = ['A', 'B', 'O', 'P']
    for i in CLASSIHIT:
        x = plt.plot(i[1], i[0], 'o', color='g')
    for j in CLASSIIHIT:
        y = plt.plot(j[1], j[0], 'o', color='r')
    for k in CLASSIIIHIT:
        z = plt.plot(k[1], k[0], 'o', color='c')
#    px1 = float(CLASSIHIT[0][1])
#    py1 = float(CLASSIHIT[0][0])
#    px2 = float(CLASSIIHIT[0][1])
#    py2 = float(CLASSIIHIT[0][0])
#    px3 = float(CLASSIIIHIT[0][1])
#    py3 = float(CLASSIIIHIT[0][0])
    plt.xlim(-50,120)
    plt.ylim(-50,120)
    plt.xlabel("Growth inhibition [GI] (% of positive control)")
    plt.ylabel("Fluorescence inhibition [FI] (% of positive control)")
    plt.title("Plot of Class I, II hits\n from the aprA'::GFP HTS")
    if z != False:
        plt.legend([x,y,z],['Class I Hits', 'Class II Hits', 'Class III Hits'], loc=4, numpoints=1)
    else:
        plt.legend([x,y],['Class I Hits', 'Class II Hits'], loc=4, numpoints=1)
    plt.axvline(0,-50,120,linestyle = '--')
    plt.axhline(0,-50,120,linestyle = '--')
    plt.axhline(25,-50,120,linestyle = '--')
    plt.axhline(-25,-50,120,linestyle = '--')
    plt.axhline(50,-50.120, linestyle = '--')
    plt.axhline(75,-50,120,linestyle = '--')
    plt.axhline(100,-50,120,linestyle = '--')
    plt.axvline(25,-50,120,linestyle = '--')
    plt.axvline(50,-50,120,linestyle = '--')
    plt.axvline(75,-50,120,linestyle = '--')
    plt.axvline(100,-50,120,linestyle = '--')
    plt.axvline(-25,-50,120,linestyle = '--')
    outfile = open(folder + "/" + 'Scatter plot of all classes of hits.png', "w")
    plt.savefig(folder + "/" + 'Scatter plot of of all classes of hits.png', dpi=300)
    outfile.close()