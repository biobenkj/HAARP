__author__ = 'benjaminjohnson'
import os
import subprocess
import datetime
import csv
import itertools
import matplotlib.pyplot as plt
from pylab import *
import numpy as np

#Initialize a series of global lists to be manipulated and accessed by all functions
plate_ID = []
GFP = []
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
    """It creates a default folder 'HTS_Data' on the desktop if it
    doesn't already exist. And then creates a subfolder in HTS_Data with the date
    to store all of the data from the run.
    """
    print "Creating a folder with which all the generated data will be placed."
    print "Default subfolder location will be in 'HTS_Data' which is located on the Desktop"
    defined_path = find_path() + "/HTS_Data"
    now = datetime.datetime.now()
    #all data folder will go into HTS_Data, if it doesn't already exist from previous runs it wil be created
    if not os.path.isdir(defined_path):
        os.mkdir(defined_path)
        print "Created folder 'HTS_Data' on the Desktop"
    new_fold = now.strftime("%Y-%m-%d")
    defined_full_path = defined_path + "/" + new_fold  #path to the subfolder inside HTS_Data
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
    data to run the analysis on the data. It will look on the desktop
    and will go into a subfolder if necessary. The function returns the
    path to the folder containing the data. All of the user input will be
    bypassed if the user used the -i option in the beginning
    """
    path = find_path()
    input = str(raw_input("Please enter the name of the folder on the Desktop containing the HTS data:"))
    data_path = path + "/" + input
    while not os.path.isdir(data_path):
        new_input = str(raw_input("Sorry the software could not be find that folder on the desktop, try typing the folder name again or Q to quit:"))
        if new_input.upper() == "Q":
            quit()
        data_path = path + "/" + new_input
#    create_folder()
    return data_path


def read_input(infile):
    """Reads in files from the user specified location. These files need to be
    .csv files and exported in the Perkin Elmer plate reader format. This function
    will read in both the fluorescence and OD readings within each run and collate
    them in a list of lists.
    """

    print "Reading in files"

    for file in os.listdir(infile):  #iterating through the files contained inside of a parent folder
        gfpruns = []
        odruns = []
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .csv
        if extension == ".csv":  #checking if the file is a text file (ie ends in .csv)
            filename = infile + "/" + file
            data = csv.reader(open(filename, 'rU'), dialect='excel')
            gfp = False
            gfpcontainer = []
            odcontainer = []
            for rows in data:
                if len(rows) >= 7:
                    if rows[7] == 'Meas A': #make sure that all the preliminary text is skipped up to the actual data
                        plate_ID.append(rows[2]) #store the plate barcode
                        gfp = True
                    if rows[0] in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P'] and gfp == True:
                        if rows[0] == 'A':
                            gfpcontainer.append(map(int,rows[1:25])) #values need to be integers for further analysis
                        elif rows[0] == 'P':
                            gfpcontainer.append(map(int,rows[1:25]))
                            gfp = False
                            gfpruns.append(gfpcontainer)
                            gfpcontainer = []
                        else:
                            gfpcontainer.append(map(int,rows[1:25]))
                    elif rows[0] in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']:
                        if rows[0] == 'P':
                            odcontainer.append(map(float,rows[1:25])) #ensure that ODs are floats and not rounded to integers
                            odruns.append(odcontainer)
                            odcontainer = []
                        elif rows[1] == '- ':
                            break
                        else:
                            odcontainer.append(map(float,rows[1:25]))
                else:
                    continue
        else:
            continue
        GFP.append(gfpruns)
        OD.append(odruns)

    return GFP, OD, plate_ID


def normalizebyz(x, y):
    """This algorithm makes use of normalizing plates within a run
    by using only the plates that have a Z' factor greater than 0.5.
    This is to account for any bleed over from the positive controls
    """
    runavgneggfp = [] #initialize empty lists which will eventually contain the average values of GFP and OD for a run
    runavgposgfp = []
    runavgnegod = []
    runavgposod = []
    for i, j in itertools.izip(x, y):
        runneggfpcontainer = [] #initialize some temporary containers for proper formatting of data to maintain runs seperate from one another
        runposgfpcontainer = []
        runnegodcontainer = []
        runposodcontainer = []
        for m, n in itertools.izip(i, j):
            neggfp = []
            posgfp = []
            negod = []
            posod = []
            for q, r in itertools.izip(m, n):
                negg,nego = q[-2],r[-2] #reverse index to grab the DMSO negative control values
                posg,poso = q[-1],r[-1] #reverse index to grab the positive control values
                neggfp.append(negg)
                posgfp.append(posg)
                negod.append(nego)
                posod.append(poso)
            ang = sum(neggfp)/len(neggfp) #calculate the averages
            apg = sum(posgfp)/len(posgfp)
            ano = sum(negod)/len(negod)
            apo = sum(posod)/len(posod)
            stdneg = ((np.std(neggfp))*3) #calculate 3 times the standard deviation for Z' calculation
            stdpos = ((np.std(posgfp))*3)
            # stdneg = ((np.std(negod))*3) #calculate 3 times the standard deviation for Z' calculation
            # stdpos = ((np.std(posod))*3)

            z = 1.0-((stdpos+stdneg)/abs(apg-ang))  #calculate the Z' prime value
            print z
            if z >= 0.5: #if Z' is greater than 0.5, save the average negative and positive control values from that plate
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

    for i in range(len(x)): #start the normalization steps using the average DMSO and positive control values from within a run that have a Z' greater than 0.5
        normalgfp = []
        normgfpcontainer = []
        meanneggfp = np.average(runavgneggfp[i]) #average the means from within a run
        meanposgfp = np.average(runavgposgfp[i])
        for x_i in x[i]:
            for x_ii in x_i:
                for x_iii in x_ii:
                    normgfp = (float(meanneggfp-x_iii))/(float(meanneggfp-meanposgfp))*100 #calculate the normalized percent inhibition
                    normgfpcontainer.append(normgfp)
                del normgfpcontainer[-1] #remove the negative and positive control values from the plates as we won't need them any more
                del normgfpcontainer[-1]
                normalgfp.append(normgfpcontainer)
                normgfpcontainer = []
            NORMALGFPDATA.append(normalgfp)
            normalgfp = []

    for i in range(len(y)):
        meannegod = np.average(runavgnegod[i]) #do the same as above but for the OD values
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
    """This function bins the data based on percent inhibition"""
    for i,j in itertools.izip(x,y):
        for m,n in itertools.izip(i,j):
            for a,b in itertools.izip(m,n):
                if a <= 25: #bin values with less than or equal to 25% fluorescence inhibition
                    # if a >= -50 and b >= -50: #values less than -50% fluorescence inhibition are likely autofluorescent
                    TWENTYFIVEGFP.append(a)
                    TWENTYFIVEOD.append(b)
                elif a <= 50: #bin values with less than or equal to 50% fluorescence inhibition
                    # if b >= -50:
                    FIFTYGFP.append(a)
                    FIFTYOD.append(b)
                    if a >= 35: #add values that are greater than 35% fluorescence inhibition for Class I binning later
                        THIRTYFIVEGFP.append(a)
                        THIRTYFIVEOD.append(b)
                elif a <= 75: #bin values with less than or equal to 75% fluorescence inhibition
                    # if b >= -50:
                    SEVENTYFIVEGFP.append(a)
                    SEVENTYFIVEOD.append(b)
                elif a > 75: #bin values greater than 75% fluorescence inhibition
                    # if b >= -50:
                    HUNDREDGFP.append(a)
                    HUNDREDOD.append(b)
    return


def findcompound():
    """This is a complex set of algorithms to retrieve the compound IDs, names,
    original library, and plate location. Folders containing the relevant libraries
    for the screen were made from the Harvard database. The user is prompted for the
    names of these folders that need to be on the desktop"""
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
    allgfp = TWENTYFIVEGFP + FIFTYGFP + SEVENTYFIVEGFP + HUNDREDGFP
    odclassIcut = []
    #odclassIIcut = []
    odclassIIIcut = []
    print "...Finding compound IDs..."
    alldata = TWENTYFIVEOD + FIFTYOD + SEVENTYFIVEOD + HUNDREDOD
    for od in alldata:
        if od <= 35.0: #grab all compounds with growth inhibition less than 35% for Class I compounds
            odclassIcut.append(od)
        elif od >= 50.0: #grab all compounds with growth inhibition greater than 50% for Class II and III compounds
            odclassIIIcut.append(od)
    countplate = 0
    countrow = 0
    rowdict = {0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G', 7:'H', 8:'I', 9:'J', 10:'K', 11:'L', 12:'M', 13:'N', 14:'O', 15:'P'}
#    print len(odclassIIIcut)
    for plateg, plateo in itertools.izip(NORMALGFPDATA, NORMALODDATA): #iterate by plate in a run
#        print len(i)
        for rowg, rowo in itertools.izip(plateg,plateo): #iterate by row within a plate
            for datg in range(len(rowg)):
                if rowg[datg] in allgfp and rowo[datg] in alldata: #find if the individual value in the well is in either of the Class II fluorescence or growth inhibition bins
                    if datg < 9: #for wells 1-9
                        CLASSIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]]) #append fluorescence inhibition, growth inhibition, well location, and plate ID
                    else:
                        CLASSIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+str(datg+1),plate_ID[countplate]])
                # elif rowg[datg] in belowfiftygfp and rowo[datg] in odclassIIIcut: #find if the individual value in the well is in either of the Class III fluorescence or growth inhibition bins
                #     if (rowo[datg]/rowg[datg]) >= 1.5 or (rowo[datg]/rowg[datg]) < 0:
                #         if datg < 9:
                #             CLASSIIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]])
                #         else:
                #             CLASSIIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+str(datg+1),plate_ID[countplate]])
                # elif rowg[datg] in abovethirtyfivegfp: #find if the individual value in the well is in either of the Class I fluorescence or growth inhibition bins
                #     if rowg[datg] >= 35.0 and (rowg[datg]/rowo[datg]) >= 1.5 or (rowg[datg]/rowo[datg]) < 0:
                #         if datg < 9:
                #             CLASSIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]])
                #         else:
                #             CLASSIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+str(datg+1),plate_ID[countplate]])
                #     elif (rowg[datg]/rowo[datg]) >= 1.5 or (rowg[datg]/rowo[datg]) < 0:
                #         if datg < 9:
                #             CLASSIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]])
                #         else:
                #             CLASSIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+str(datg+1),plate_ID[countplate]])

            countrow += 1
        countrow = 0
        countplate += 1

    print "...Still working..."
    for file in os.listdir(plate_path): #iterating through the files contained inside of a parent folder
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
            filename = plate_path + "/" + file
            data = csv.reader(open(filename, 'rU'), dialect='excel')
            for rows in data:
                for hits in CLASSIIHIT:
                    plate_id = hits[3]
                    well_id = hits[2]
                    if well_id == rows[2] and plate_id == rows[3]:
                        hits.append(rows[0])
                        hits.append(rows[1])

    classIplateid = []
    classIplateloc = []
    newhits = []
    for short in CLASSIIHIT:
        if len(short) > 4:
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
                    if classIplateid[a] == info[1] and classIplateloc[a] == info[0]:
                        newhits[a].append(info[2])

    cp = find_path() + '/Platemaps'
    for file in os.listdir(cp):
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
            filename = cp + "/" + file
            data1 = csv.reader(open(filename, 'rU'), dialect='excel')
            for info in data1:
                for a in range(len(newhits)):
                    if newhits[a][5] == info[1] and classIplateloc[a] == info[0]:
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