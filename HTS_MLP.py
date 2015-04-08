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
                negg,nego = q[1],r[1] #reverse index to grab the DMSO negative control values
                posg,poso = q[0],r[0] #reverse index to grab the positive control values
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

            z = 1.0-((stdpos+stdneg)/abs(apg-ang))  #calculate the Z' prime value

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
                # del normgfpcontainer[0] #remove the negative and positive control values from the plates as we won't need them any more
                # del normgfpcontainer[0]
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
                # del normodcontainer[0]
                # del normodcontainer[0]
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
                    if a >= -50 and b >= -50: #values less than -50% fluorescence inhibition are likely autofluorescent
                        TWENTYFIVEGFP.append(a)
                        TWENTYFIVEOD.append(b)
                elif a <= 50: #bin values with less than or equal to 50% fluorescence inhibition
                    if b >= -50:
                        FIFTYGFP.append(a)
                        FIFTYOD.append(b)
                        if a >= 35: #add values that are greater than 35% fluorescence inhibition for Class I binning later
                            THIRTYFIVEGFP.append(a)
                            THIRTYFIVEOD.append(b)
                elif a <= 75: #bin values with less than or equal to 75% fluorescence inhibition
                    if b >= -50:
                        SEVENTYFIVEGFP.append(a)
                        SEVENTYFIVEOD.append(b)
                elif a > 75: #bin values greater than 75% fluorescence inhibition
                    if b >= -50:
                        HUNDREDGFP.append(a)
                        HUNDREDOD.append(b)
    return

def plotbindata(folder, ave):
    """This function will plot the binned data using matplotlib"""
    print "...Plotting all data..."
    t1 = plt.plot(TWENTYFIVEOD,TWENTYFIVEGFP,'bo') #color compounds with less than 25% fluorescence inhibition blue
    t2 = plt.plot(FIFTYOD,FIFTYGFP,'co') #color compounds with less than 50% fluorescence inhibition cyan
    t3 = plt.plot(SEVENTYFIVEOD,SEVENTYFIVEGFP,'yo') #color compounds with less than 75% fluorescence inhibition yellow
    t4 = plt.plot(HUNDREDOD,HUNDREDGFP,'ro') #color compounds with greater than 75% fluorescence inhibition red
    plt.xlim(-50,120) #set x and y axis limits
    plt.ylim(-50,120)
    plt.xlabel("Growth inhibition [GI] (% of positive control)")
    plt.ylabel("Fluorescence inhibition [FI] (% of positive control)")
    plt.title("Scatter plot of all data from the MLP hspX'::GFP HTS\nZ'-factor is %.2f" % ave)
    # plt.legend([t1, t2, t3, t4],['<25% FI', '25-50% FI', '50-75% FI', '>75% FI'], loc=4, numpoints=1)
    plt.axvline(0,-50,120,linestyle = '--') #add some dashed lines for visual purposes
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
    outfile = open(folder + "/" + 'Scatter plot of all data.png', "w") #open a file using the path to the subfolder in HTS_Data
    plt.savefig(folder + "/" + 'Scatter plot of all data.png', dpi=300) #save the figure with a resolution of 300 dpi
    outfile.close() #close the file
    plt.clf() #THIS IS IMPORTANT FOR FURTHER PLOTTING. This will clear the figure. If you don't do this matplotlib will just make a composite of all plots


def twodplot(folder):
    """This function produces the heatmap to note where most compounds
    are localizing to. This function requires matplotlib.
    """
    x = TWENTYFIVEOD + FIFTYOD + SEVENTYFIVEOD + HUNDREDOD #gather all of the GFP and OD values from the whole data set
    y = TWENTYFIVEGFP + FIFTYGFP + SEVENTYFIVEGFP + HUNDREDGFP
    hist,xedges,yedges = np.histogram2d(x,y,bins=100,range=[[-50,120],[-50,120]]) #generate a 2-D histogram with matplotlib
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1] ]
    imshow(hist.T,extent=extent,interpolation='nearest',origin='lower') #generate the plot
    plt.xlabel("Growth inhibition [GI] (% of positive control)")
    plt.ylabel("Fluorescence inhibition [FI] (% of positive control)")
    plt.axvline(0,-50,120,linestyle = '--', color = 'white') #add some dashed lines for visualization purposes
    plt.axhline(0,-50,120,linestyle = '--', color = 'white')
    plt.axhline(25,-50,120,linestyle = '--', color = 'white')
    plt.axhline(-25,-50,120,linestyle = '--', color = 'white')
    plt.axhline(50,-50.120, linestyle = '--', color = 'white')
    plt.axhline(75,-50,120,linestyle = '--', color = 'white')
    plt.axhline(100,-50,120,linestyle = '--', color = 'white')
    plt.axvline(25,-50,120,linestyle = '--', color = 'white')
    plt.axvline(50,-50,120,linestyle = '--', color = 'white')
    plt.axvline(75,-50,120,linestyle = '--', color = 'white')
    plt.axvline(100,-50,120,linestyle = '--', color = 'white')
    plt.axvline(-25,-50,120,linestyle = '--', color = 'white')
    colorbar()
    outfile = open(folder + '/' + '2-D density plot.png', 'w') #open a file to put the plot in the subfolder of HTS_Data
    plt.savefig(folder + '/' + '2-D density plot.png', dpi=300) #save the figure with a resolution of 300 dpi
    outfile.close() #close the file
    plt.clf() #clear the figure again. IMPORTANT


def calcz():
    """Calculate the average Z' factor for the dataset"""
    avez = sum(GFPZFACTOR)/len(GFPZFACTOR)
    float(avez)
    return avez


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
                if rowg[datg] in abovefiftygfp and rowo[datg] in odclassIIIcut: #find if the individual value in the well is in either of the Class II fluorescence or growth inhibition bins
                    if datg > 1 and datg < 9: #for wells 2-9
                        CLASSIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]]) #append fluorescence inhibition, growth inhibition, well location, and plate ID
                    elif datg > 1 and datg >= 9:
                        CLASSIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+str(datg+1),plate_ID[countplate]])
                elif rowg[datg] in belowfiftygfp and rowo[datg] in odclassIIIcut: #find if the individual value in the well is in either of the Class III fluorescence or growth inhibition bins
                    if (rowo[datg]/rowg[datg]) >= 1.5 or (rowo[datg]/rowg[datg]) < 0:
                        if datg > 1 and datg < 9:
                            CLASSIIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]])
                        elif datg > 1 and datg >= 9:
                            CLASSIIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+str(datg+1),plate_ID[countplate]])
                elif rowg[datg] in abovethirtyfivegfp: #find if the individual value in the well is in either of the Class I fluorescence or growth inhibition bins
                    if rowg[datg] >= 35.0 and (rowg[datg]/rowo[datg]) >= 1.5 or (rowg[datg]/rowo[datg]) < 0:
                    # if rowo[datg] <= 10.0 and (rowg[datg]/rowo[datg]) >= 1.5 or (rowg[datg]/rowo[datg]) < 0:
                        if datg > 1 and datg < 9:
                            CLASSIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]])
                        elif datg > 1 and datg >= 9:
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
#    print len(CLASSIIHIT)
    for file in os.listdir(plate_path): #iterating through the files contained inside of a parent folder
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .csv
        if extension == ".csv": #checking if the file is a text file (ie ends in .csv)
            filename = plate_path + "/" + file
            data = csv.reader(open(filename, 'rU'), dialect='excel') #this is a pretty marvelous feature of this python package... read excel style documents!
            for rows in data:
                for hits in CLASSIHIT:
                    id = hits[3]
                    if id == rows[3].upper(): #if the plate ID matches a corresponding one in the library ID file
                        hits.append(rows[1]) #append the library ID and the library name
                        hits.append(rows[2])
#            for rows in data:
                for antibio in CLASSIIHIT:
                        antibioid = antibio[3]
                        if antibioid == rows[3].upper(): #if the plate ID matches a corresponding one in the library ID file
                            antibio.append(rows[1]) #append the library ID and the library name
                            antibio.append(rows[2])
                for h in CLASSIIIHIT:
                    hid = h[3]
                    if hid == rows[3].upper(): #if the plate ID matches a corresponding one in the library ID file
                        h.append(rows[1]) #append the library ID and the library name
                        h.append(rows[2])
    classIplateid = []
    classIplateloc = []
    for idhits in CLASSIHIT:
        classIplateid.append(idhits[5])
        classIplateloc.append(idhits[2])
    classIIplateid = []
    classIIplateloc = []
    for idhitstwo in CLASSIIHIT:
        classIIplateid.append(idhitstwo[5])
        classIIplateloc.append(idhitstwo[2])
    classIIIplateid = []
    classIIIplateloc = []
    for idhitstwo in CLASSIIIHIT:
        classIIIplateid.append(idhitstwo[5])
        classIIIplateloc.append(idhitstwo[2])

    for file in os.listdir(comp_path):
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .csv
        if extension == ".csv": #checking if the file is a text file (ie ends in .csv)
            filename = comp_path + "/" + file
            data1 = csv.reader(open(filename, 'rU'), dialect='excel')
            for info in data1:
                for a in range(len(classIplateid)): #the following loops find and append the compound ID and name within the libraries
                    if classIplateid[a] == info[0] and classIplateloc[a] == info[1]:
                        CLASSIHIT[a].append(info[5])
                        CLASSIHIT[a].append(info[6])
                        CLASSIHIT[a].append(info[7])
                for b in range(len(classIIplateid)):
                    if classIIplateid[b] == info[0] and classIIplateloc[b] == info[1]:
                        CLASSIIHIT[b].append(info[5])
                        CLASSIIHIT[b].append(info[6])
                        CLASSIIHIT[b].append(info[7])
                for c in range(len(classIIIplateid)):
                    if classIIIplateid[c] == info[0] and classIIIplateloc[c] == info[1]:
                        CLASSIIIHIT[c].append(info[5])
                        CLASSIIIHIT[c].append(info[6])
                        CLASSIIIHIT[c].append(info[7])
    return


def plotCIdata(CLASSIHIT, folder):
    """Plot the Class I data and grey out all other data points"""
    print "...Plotting data..."

    for gfpplate, odplate in itertools.izip(NORMALGFPDATA, NORMALODDATA):
        for gfprow, odrow in itertools.izip(gfpplate, odplate):
            del gfprow[0]
            del gfprow[0]
            del odrow[0]
            del odrow[0]


    #plot but grey out all points
    for greygfp, greyod in itertools.izip(NORMALODDATA, NORMALGFPDATA):
        for greyx, greyy in itertools.izip(greygfp, greyod):
            plt.plot(greyx, greyy, 'o', color='0.95')

    # plt.plot(NORMALODDATA, NORMALGFPDATA, 'o', color='0.95')
    # plt.plot(TWENTYFIVEOD,TWENTYFIVEGFP,'o', color='0.95')
    # plt.plot(FIFTYOD,FIFTYGFP,'o', color='0.95')
    # plt.plot(SEVENTYFIVEOD,SEVENTYFIVEGFP,'o', color='0.95')
    # plt.plot(HUNDREDOD,HUNDREDGFP,'o', color='0.95')
    for i in CLASSIHIT:
        plt.plot(i[1], i[0], 'o', color='g') #re-plot the Class I data and color it green
    plt.xlim(-50,120) #set the x and y axis limits
    plt.ylim(-50,120)
    plt.xlabel("Growth inhibition (% of positive control)")
    plt.ylabel("Fluorescence inhibition (% of positive control)")
    plt.title("Plot of Class I hits from the aprA'::GFP HTS")
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
    outfile = open(folder + "/" + 'Scatter plot of Class I hits.png', "w")
    plt.savefig(folder + "/" + 'Scatter plot of Class I hits.png', dpi=300)
    outfile.close()
    plt.clf()


def plotCIIdata(CLASSIIHIT, folder):
    """Plot the Class II data, greying out all other points"""
    #plot and grey out all data points
    for greygfp, greyod in itertools.izip(NORMALODDATA, NORMALGFPDATA):
        for greyx, greyy in itertools.izip(greygfp, greyod):
            plt.plot(greyx, greyy, 'o', color='0.95')
    # plt.plot(TWENTYFIVEOD,TWENTYFIVEGFP,'o', color='0.95')
    # plt.plot(FIFTYOD,FIFTYGFP,'o', color='0.95')
    # plt.plot(SEVENTYFIVEOD,SEVENTYFIVEGFP,'o', color='0.95')
    # plt.plot(HUNDREDOD,HUNDREDGFP,'o', color='0.95')
    for i in CLASSIIHIT:
        plt.plot(i[1], i[0], 'o', color='r') #re-plot the Class II data points and color them red
    plt.xlim(-50,120)
    plt.ylim(-50,120)
    plt.xlabel("Growth inhibition (% of positive control)")
    plt.ylabel("Fluorescence inhibition (% of positive control)")
    plt.title("Plot of Class II hits from the hspX'::GFP HTS")
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
    outfile = open(folder + "/" + 'Scatter plot of Class II hits.png', "w")
    plt.savefig(folder + "/" + 'Scatter plot of Class II hits.png', dpi=300)
    outfile.close()
    plt.clf()


def plotCIIIdata(CLASSIIIHIT, folder):
    """Plot the Class III data and grey out all other points"""
    print "...Plotting data..."
    #plot all data points and color them grey
    for greygfp, greyod in itertools.izip(NORMALODDATA, NORMALGFPDATA):
        for greyx, greyy in itertools.izip(greygfp, greyod):
            plt.plot(greyx, greyy, 'o', color='0.95')
    # plt.plot(TWENTYFIVEOD,TWENTYFIVEGFP, 'o', color='0.95')
    # plt.plot(FIFTYOD,FIFTYGFP, 'o', color='0.95')
    # plt.plot(SEVENTYFIVEOD,SEVENTYFIVEGFP, 'o', color='0.95')
    # plt.plot(HUNDREDOD,HUNDREDGFP, 'o', color='0.95')
    for i in CLASSIIIHIT:
        plt.plot(i[1], i[0], 'o', color='c') #re-plot the Class III data points and color them cyan
    plt.xlim(-50,120)
    plt.ylim(-50,120)
    plt.xlabel("Growth inhibition (% of positive control)")
    plt.ylabel("Fluorescence inhibition (% of positive control)")
    plt.title("Plot of Class III hits from the hspX'::GFP HTS")
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
    outfile = open(folder + "/" + 'Scatter plot of Class III hits.png', "w")
    plt.savefig(folder + "/" + 'Scatter plot of Class III hits.png', dpi=300)
    outfile.close()
    plt.clf()


def plotallclassesdata(CLASSIHIT, CLASSIIHIT, CLASSIIIHIT, folder):
    """Plot all three classes of data and grey out all other points"""
    print "...Plotting data..."
    x = False
    y = False
    z = False
    #plot all data points and grey them out
    for greygfp, greyod in itertools.izip(NORMALODDATA, NORMALGFPDATA):
        for greyx, greyy in itertools.izip(greygfp, greyod):
            plt.plot(greyx, greyy, 'o', color='0.95')
    # plt.plot(TWENTYFIVEOD,TWENTYFIVEGFP, 'o', color='0.95')
    # plt.plot(FIFTYOD,FIFTYGFP, 'o', color='0.95')
    # plt.plot(SEVENTYFIVEOD,SEVENTYFIVEGFP, 'o', color='0.95')
    # plt.plot(HUNDREDOD,HUNDREDGFP, 'o', color='0.95')
    #re-plot all classes of hits and color them the same way as in the individual plots
    for i in CLASSIHIT:
        x = plt.plot(i[1], i[0], 'o', color='g')
    for j in CLASSIIHIT:
        y = plt.plot(j[1], j[0], 'o', color='r')
    for k in CLASSIIIHIT:
        z = plt.plot(k[1], k[0], 'o', color='c')
    plt.xlim(-50,120)
    plt.ylim(-50,120)
    plt.xlabel("Growth inhibition [GI] (% of positive control)")
    plt.ylabel("Fluorescence inhibition [FI] (% of positive control)")
    plt.title("Plot of Class I, II, and III hits\n from the hspX'::GFP HTS")
    if z != False: #this is a clunky way of plotting figure legends for the two screens as the HspX screen doesn't have Class III compounds
        #eventually this will be an option that will be set either by a config file or by the user when initiating the program
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
    plt.clf()


def makecsvfile(path):
    """Make the .csv file containing all the pertinent hit information
    that has been gathered until now. Takes a path in as an argument
    that comes from the find_path function"""
    print "...Making .csv files for each class of hits..."
    #make three seperate files
    #one for each class of hits
    outf = open(path + '/' + 'Class I hits.csv', 'wb')
    outcsv = csv.writer(outf)
    outcsv.writerow(['Class I hits are binned at > 35% GFP inhibition and at least a two-fold difference between GFP and OD'])
    outcsv.writerow(["Fluorescence inhibition (% of positive control)", "Growth inhibition (% of positive control)", "Well location", "Plate number", "Library", "Library plate ID", "Vendor", "Compound catalog number", "Compound Name"])
    for i in CLASSIHIT:
        outcsv.writerow(i)
    outf1 = open(path + '/' + 'Class II hits.csv', 'wb')
    outcsv = csv.writer(outf1)
    outcsv.writerow(['Class II hits are binned at > 50% GFP inhibition and > 50% growth inhibition'])
    outcsv.writerow(["Fluorescence inhibition (% of positive control)", "Growth inhibition (% of positive control)", "Well location", "Plate number", "Library", "Library plate ID", "Vendor", "Compound catalog number", "Compound Name"])
    for j in CLASSIIHIT:
        outcsv.writerow(j)
    outf1 = open(path + '/' + 'Class III hits.csv', 'wb')
    outcsv = csv.writer(outf1)
    outcsv.writerow(['Class III hits are binned at < 75% GFP inhibition and > 75% growth inhibition'])
    outcsv.writerow(["Fluorescence inhibition (% of positive control)", "Growth inhibition (% of positive control)", "Well location", "Plate number", "Library", "Library plate ID", "Vendor", "Compound catalog number", "Coumpound Name"])
    for k in CLASSIIIHIT:
        outcsv.writerow(k)
    return


#THE FUNCTIONS BELOW THIS LINE ARE SPECIFIC FOR THE HARVARD DATABASE TO UPLOAD INFORMATION
#ALL OF THEM ARE VERY VERY SPECIFIC TO OUR DATA AND ARE THUS NOT USEFUL FOR THE GENERAL USER

def writealldata(outpath):
    alldat = []
    newGFP = []
    newOD = []

    for i,j in itertools.izip(GFP, OD):
        for k,l in itertools.izip(i,j):
                newGFP.append(k)
                newOD.append(l)

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

    countplate = 0
    countrow = 0
    rowdict = {0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G', 7:'H', 8:'I', 9:'J', 10:'K', 11:'L', 12:'M', 13:'N', 14:'O', 15:'P'}
    #    print len(odclassIIIcut)
    for plateg, plateo in itertools.izip(newGFP, newOD):
    #        print len(i)
        for rowg, rowo in itertools.izip(plateg,plateo):
            for datg in range(len(rowg)):
#                if datg <= 1:
##                        alldat.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]])
#                    alldat.append([plate_ID[countplate],rowdict[countrow]+('0'+str(datg+1)), 'E','Y', rowg[datg], rowo[datg], rowg[datg]/rowo[datg]])
                if datg < 9:
                    alldat.append([plate_ID[countplate],rowdict[countrow]+('0'+str(datg+1)), 'X','', rowg[datg], rowo[datg], rowg[datg]/rowo[datg]])
                elif datg == 22:
                    alldat.append([plate_ID[countplate],rowdict[countrow]+str(datg+1), 'N', '', rowg[datg], rowo[datg], rowg[datg]/rowo[datg]])
                elif datg == 23:
                    alldat.append([plate_ID[countplate],rowdict[countrow]+str(datg+1), 'P', '', rowg[datg], rowo[datg], rowg[datg]/rowo[datg]])
                else:
                    alldat.append([plate_ID[countplate],rowdict[countrow]+str(datg+1), 'X', '', rowg[datg], rowo[datg], rowg[datg]/rowo[datg]])
            countrow += 1
        countrow = 0
        countplate += 1
#    negcontrol = ['A23', 'B23', 'C23', 'D23', 'E23', 'F23', 'G23', 'H23', 'I23', 'J23', 'K23', 'L23', 'M23', 'N23', 'O23', 'P23']
#    poscontrol = ['A24', 'B24', 'C24', 'D24', 'E24', 'F24', 'G24', 'H24', 'I24', 'J24', 'K24', 'L24', 'M24', 'N24', 'O24', 'P24']
    ratiodata = []
    for pg, po in itertools.izip(NORMALGFPDATA, NORMALODDATA):
        for rg, ro in itertools.izip(pg, po):
            for dg in range(len(rg)):
                ratiodata.append([rg[dg], ro[dg], rg[dg]/ro[dg], ro[dg]/rg[dg]])
    for r,s in itertools.izip(alldat,ratiodata):
        r.append(s[0])
        r.append(s[1])
        r.append(s[2])
        r.append(s[3])

    for file in os.listdir(plate_path): #iterating through the files contained inside of a parent folder
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
            filename = plate_path + "/" + file
            data = csv.reader(open(filename, 'rU'), dialect='excel')
            for rows in data:
                for hits in alldat:
                    id = hits[0]


                    if id == rows[3].upper():
                        hits.append(hits[0])
                        hits[0] = rows[2]
#                            hits.append(rows[1])

#    classIplateid = []
#    classIplateloc = []
#    for idhits in alldat:
#
#        classIplateid.append(idhits[5])
#        classIplateloc.append(idhits[2])

#    for file in os.listdir(comp_path):
#        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
#        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
#            filename = comp_path + "/" + file
#            data1 = csv.reader(open(filename, 'rU'), dialect='excel')
#            for info in data1:
#                for a in range(len(classIplateid)):
#                    if classIplateid[a] == info[0] and classIplateloc[a] == info[1]:
#                        alldat[a].append(info[6])
#                        alldat[a].append(info[7])
    print "...Making .csv files for all hits..."
    outf = open(outpath + '/' + 'Alldata.csv', 'wb')
    outcsv = csv.writer(outf)
    outcsv.writerow(['Stock_ID', 'Well', 'Type', 'Exclude', 'Fluorescence_A', 'Absorbance_A', 'Ratio_A', '%FI compared to a positive control', '%GI compared to a positive control', 'FI:GI ratio', 'GI:FI ratio', 'Positive: >35% FI and >1.5-fold or <0 fluorescence:growth inhibition', 'Positive: inhibits at least 50% fluorescence and growth', 'Positive: >50% GI, <50% FI, >1.5-fold or <0 growth:fluorescence inhibition', 'Comment'])
    for i in alldat:
        outcsv.writerow(i)
    return

def comparehits(op):

    newharvdat = []
    c1hitdat = []
    c2hitdat = []
    c3hitdat = []
    dat = csv.reader(open(op + '/Alldata.csv', 'rU'), dialect='excel')
    for rows in dat:
        if rows[0].startswith('Stock_ID'):
            continue
        newharvdat.append(rows)
    c1dat = csv.reader(open('/Users/benjaminjohnson/Desktop/HTS_Data/2013-04-10_8/Class I hits.csv', 'rU'), dialect='excel')
    for rows in c1dat:
        if rows[0].startswith('Class') or rows[0].startswith('Fluorescence'):
            continue
        c1hitdat.append([rows[3], rows[5], rows[2]])
    c2dat = csv.reader(open('/Users/benjaminjohnson/Desktop/HTS_Data/2013-04-10_8/Class II hits.csv', 'rU'), dialect='excel')
    for rows in c2dat:
        if rows[0].startswith('Class') or rows[0].startswith('Fluorescence'):
            continue
        c2hitdat.append([rows[3], rows[5], rows[2]])
    c3dat = csv.reader(open('/Users/benjaminjohnson/Desktop/HTS_Data/2013-04-10_8/Class III hits.csv', 'rU'), dialect='excel')
    for rows in c3dat:
        if rows[0].startswith('Class') or rows[0].startswith('Fluorescence'):
            continue
        c3hitdat.append([rows[3], rows[5], rows[2]])
    negcontrol = ['A21', 'B21', 'C21', 'D21', 'E21', 'F21', 'G21', 'H21', 'I21', 'J21', 'K21', 'L21', 'M21', 'N21', 'O21', 'P21','A22', 'B22', 'C22', 'D22', 'E22', 'F22', 'G22', 'H22', 'I22', 'J22', 'K22', 'L22', 'M22', 'N22', 'O22', 'P22']
    for c1 in c1hitdat:
        for row in newharvdat:
            if c1[0] == row[11] and c1[2] == row[1]:
                row[11] = 'Y'
                row.append('')
                row.append('')
                row.append('Inhibits GFP fluorescence more than OD')
#                if c1[3] == 'blank' or c1[2] in negcontrol:
#                    row[3] = 'Y'
#                    row[11] = ''
#                    row[14] = 'Well issue'
    for c2 in c2hitdat:
        for row in newharvdat:
            if c2[0] == row[11] and c2[2] == row[1]:
                row[11] = ''
                row.append('Y')
                row.append('')
                row.append('Inhibits greater than or equal to 50% GFP fluorescence and OD; antibiotic-like')
#                if c2[3] == 'blank' or c2[2] in negcontrol:
#                    row[3] = 'Y'
#                    row[12] = ''
#                    row[14] = 'Well issue'
    for c3 in c3hitdat:
        for row in newharvdat:
            if c3[0] == row[11] and c3[2] == row[1]:
                row[11] = ''
                row.append('')
                row.append('Y')
                row.append('Inhibits OD more than GFP fluorescence')
#                if c3[3] == 'blank' or c3[2] in negcontrol:
#                    row[3] = 'Y'
#                    row[13] = ''
#                    row[14] = 'Well issue'
    for i in newharvdat:
        if i[11] == 'Y' or i[1] == '':
            continue
        else:
            i[11] = ''
    outf = open(op + '/' + 'Alldata.csv', 'wb')
    outcsv = csv.writer(outf)
    outcsv.writerow(['Stock_ID', 'Well', 'Type', 'Exclude', 'Fluorescence_A', 'Absorbance_A', 'Ratio_A', '%FI compared to a positive control', '%GI compared to a positive control', 'FI:GI ratio', 'GI:FI ratio', 'Positive: >35% FI and >1.5-fold or <0 fluorescence:growth inhibition', 'Positive: inhibits at least 50% fluorescence and growth', 'Positive: <50% FI, >50% GI, >1.5-fold or <0 growth:fluorescence inhibition', 'Comment'])
    for i in newharvdat:
        outcsv.writerow(i)

    return


def badwells(fold):
    path = find_path()
    input = str(raw_input("Please enter the name of the folder on the Desktop containing the file with bad wells to be searched:"))
    plate_path = path + "/" + input
    outf = []
    dat = csv.reader(open(plate_path + '/Alldata.csv', 'rU'), dialect='excel')
    for rows in dat:
        if rows[0].startswith('Stock_ID'):
            continue
        elif rows[3] == 'Y' and rows[21] == 'Rifampicin bleed over':
            outf.append([rows[0], rows[1]])

    fileout = open(fold + '/' + 'Excluded_wells.csv', 'wb')
    outcsv = csv.writer(fileout)
    outcsv.writerow(['Stock_ID', 'Well'])
    for i in outf:
        outcsv.writerow(i)
    return


