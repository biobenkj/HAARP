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


def findcompound_allhits():
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

    return allhits


def knockdown(allhits):
    deskpath = find_path()
    confirmdata = deskpath + '/APRA_Data'
    class1hits = []
    class2hits = []
    class3hits = []
    c1 = False
    c2 = False
    c3 = False
    for file in os.listdir(confirmdata):
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv":  #checking if the file is a text file (ie ends in .txt)
            filename = confirmdata + "/" + file
            if file == 'Class I hits.csv':
                c1 = True
            elif file == 'Class II hits.csv':
                c2 = True
                c1 = False
            elif file == 'Class III hits.csv':
                c3 = True
                c1 = False
                c2 = False
            data = csv.reader(open(filename, 'rU'), dialect='excel')
            for line in data:
                if line[0].startswith('Class') or line[0].startswith('Fluorescence'):
                    continue
                elif c1:
                    class1hits.append(line)
                elif c2:
                    class2hits.append(line)
                elif c3:
                    class3hits.append(line)
    counter = 0
    class1comparedata = []
    for hit in class1hits:
        for knkdown in allhits:
            if knkdown[2] == hit[2] and knkdown[3] == hit[3]:
                class1comparedata.append([hit[0], knkdown[0], hit[1], knkdown[1], hit[2], hit[3], hit[4], hit[5], hit[6], hit[7], hit[8], hit[9]])
    class2comparedata = []
    for hit in class2hits:
        for knkdown in allhits:
            if knkdown[2] == hit[2] and knkdown[3] == hit[3]:
                class2comparedata.append([hit[0], knkdown[0], hit[1], knkdown[1], hit[2], hit[3], hit[4], hit[5], hit[6], hit[7], hit[8], hit[9]])
                if knkdown[0] > 0 and knkdown[1] > 0:
                    counter += 1
    class3comparedata = []
    for hit in class3hits:
        for knkdown in allhits:
            if knkdown[2] == hit[2] and knkdown[3] == hit[3]:
                class3comparedata.append([hit[0], knkdown[0], hit[1], knkdown[1], hit[2], hit[3], hit[4], hit[5], hit[6], hit[7], hit[8], hit[9]])
    print counter
    return class1comparedata, class2comparedata, class3comparedata


def makecsvfile_allhits(path, c1, c2, c3):
    print "...Making .csv files for each class of hits..."
    outf = open(path + '/' + 'Class I hits.csv', 'wb')
    outcsv = csv.writer(outf)
    outcsv.writerow(["FI reconfirm", "FI knockdown", "GI reconfirm", "GI knockdown" "CP Well location", "Plate number", "Library", "Library well location", "Class type call from original screen", "Vendor", "Compound catalog number", "Compound name"])
    for i in c1:
        outcsv.writerow(i)
    outf = open(path + '/' + 'Class II hits.csv', 'wb')
    outcsv = csv.writer(outf)
    outcsv.writerow(["FI reconfirm", "FI knockdown", "GI reconfirm", "GI knockdown" "CP Well location", "Plate number", "Library", "Library well location", "Class type call from original screen", "Vendor", "Compound catalog number", "Compound name"])
    for i in c2:
        outcsv.writerow(i)
    outf = open(path + '/' + 'Class III hits.csv', 'wb')
    outcsv = csv.writer(outf)
    outcsv.writerow(["FI reconfirm", "FI knockdown", "GI reconfirm", "GI knockdown" "CP Well location", "Plate number", "Library", "Library well location", "Class type call from original screen", "Vendor", "Compound catalog number", "Compound name"])
    for i in c3:
        outcsv.writerow(i)

    return