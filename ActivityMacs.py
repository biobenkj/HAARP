__author__ = 'benjaminjohnson'


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
    print "Default subfolder location will be in 'Macs_Data' which is located on the Desktop"
    defined_path = find_path() + "/Macs_Data"
    now = datetime.datetime.now()
    #all data folder will go into HTMAD_Data, if it doesn't already exist from previous runs it wil be created
    if not os.path.isdir(defined_path):
        os.mkdir(defined_path)
        print "Created folder 'Macs_Data' on the Desktop"
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
        print "'" + taken + "' was already a directory in Macs_Data, '" + new_fold + "' was used instead for this run."
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

        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv":  #checking if the file is a text file (ie ends in .txt)
            filename = infile + "/" + file
            data = csv.reader(open(filename, 'rU'), dialect='excel')

            gfpcontainer = []

            for rows in data:
                if len(rows) >= 7:
                    if rows[3].startswith('Calc'):
                        plate_ID.append(rows[2])
                    if rows[0] in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']:
                        if rows[0] == 'A':
                            gfpcontainer.append(map(int, rows[1:25]))
                        elif rows[0] == 'P':
                            gfpcontainer.append(map(int, rows[1:25]))
                            gfpruns.append(gfpcontainer)
                            gfpcontainer = []
                        else:
                            gfpcontainer.append(map(int, rows[1:25]))

                else:
                    continue
        else:
            continue
        GFP.append(gfpruns)

    return GFP, plate_ID


def normalizebyz(x):
    runavgneggfp = []
    runavgposgfp = []

    for i in x:
        runneggfpcontainer = []
        runposgfpcontainer = []

        for m in i:

            posgfp = []
            counter = 0
            for q in m:
                posg = q[-1]
                if counter == 1:
                    neggfp = q[2:22]
                posgfp.append(posg)
                counter += 1

            ang = sum(neggfp)/len(neggfp)
            apg = sum(posgfp)/len(posgfp)


            stdneg = ((np.std(neggfp))*3)
            stdpos = ((np.std(posgfp))*3)

            z = 1.0-((stdpos+stdneg)/abs(apg-ang))
            print z
            if z >= 0.5:
                runneggfpcontainer.append(ang)
                runposgfpcontainer.append(apg)
                GFPZFACTOR.append(z)
        runavgneggfp.append(runneggfpcontainer)
        runavgposgfp.append(runposgfpcontainer)

    print "...Read in %d files...\n...Read in %d plates..." % (len(runavgneggfp), len(plate_ID))
    print runavgneggfp, runavgposgfp
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

    return


def bindata(x):
    for i in x:
        for m in i:
            for a in m:
                if a <= 25:
                    TWENTYFIVEGFP.append(a)
                elif a <= 50:
                    FIFTYGFP.append(a)
                elif a <= 75:
                    SEVENTYFIVEGFP.append(a)
                elif a > 75:
                    HUNDREDGFP.append(a)

    return


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
    allgfp = TWENTYFIVEGFP + FIFTYGFP + SEVENTYFIVEGFP + HUNDREDGFP
    countplate = 0
    countrow = 0
    rowdict = {0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G', 7:'H', 8:'I', 9:'J', 10:'K', 11:'L', 12:'M', 13:'N', 14:'O', 15:'P'}

    for plateg in GFP:
        for rowg in plateg:
            for datg in range(len(rowg)):
                if rowg[datg] in allgfp:
                    if datg < 9:
                        allhits.append([rowg[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]])
                    else:
                        allhits.append([rowg[datg],rowdict[countrow]+str(datg+1),plate_ID[countplate]])

            countrow += 1
        countrow = 0
        countplate += 1

    for file in os.listdir(plate_path): #iterating through the files contained inside of a parent folder
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
            filename = plate_path + "/" + file
            data = csv.reader(open(filename, 'rU'), dialect='excel')
            for rows in data:
                for hits in allhits:
                    plate_id = hits[2]
                    well_id = hits[1]
                    if well_id == rows[2] and plate_id == rows[3]:
                        hits.append(rows[0])
                        hits.append(rows[1])

    classIplateid = []
    classIplateloc = []
    newhits = []
    for short in allhits:
        if len(short) > 3:
            newhits.append(short)
            classIplateid.append(short[3])
            classIplateloc.append(short[4])
    # for idhits in newhits:
    #     if len(idhits) >= 4:
    #         classIplateid.append(idhits[3])
    #         classIplateloc.append(idhits[4])

    for file in os.listdir(comp_path):
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
            filename = comp_path + "/" + file
            data1 = csv.reader(open(filename, 'rU'), dialect='excel')
            for info in data1:
                for a in range(len(classIplateid)):
                    if classIplateid[a] == info[0] and classIplateloc[a] == info[1]:
                        newhits[a].append(info[2])

    cp = find_path() + '/Platemaps'
    for file in os.listdir(cp):
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
            filename = cp + "/" + file
            data1 = csv.reader(open(filename, 'rU'), dialect='excel')
            for info in data1:
                for a in range(len(classIplateid)):
                    if classIplateid[a] == info[0] and classIplateloc[a] == info[1]:
                        newhits[a].append(info[2])
                        newhits[a].append(info[6])
                        newhits[a].append(info[7])

    # for hit in newhits:
    #     if hit[0] < 0:
    #         hit[0] = float(0.0)

    return newhits


def makecsvfile_allhits(path, c1):
    print "...Making .csv files for each class of hits..."
    outf = open(path + '/' + 'Class I hits.csv', 'wb')
    outcsv = csv.writer(outf)
    outcsv.writerow(["Fluorescence inhibition (% of positive control)", "CP Well location", "Plate number", "Library", "Library well location", "Class type call from original screen", "Vendor", "Compound catalog number", "Compound name"])
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