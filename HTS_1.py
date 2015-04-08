__author__ = 'benjaminjohnson'


import os
import subprocess
import datetime
import csv
import itertools
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as sp
import scipy
import scikits.bootstrap as bootstrap
#import rpy2.robjects as robjects
#from rpy2.robjects.packages import importr

plate_ID = []
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
#ODZFACTOR = []
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
    .txt files and in two columns, an x and y, separated by a single space. The
    data will then be separated into two lists, on for x value and one of y values.
    The list of x or y values contain many lists, one for each spectra, that
    contain the x or y values, respectively, for the spectra. It then returns the
    list of y lists.
    """
    GFP = [] #empty list that will eventually contain the list of lists of data
    OD = []



    print "Reading in files"

    for file in os.listdir(infile): #iterating through the files contained inside of a parent folder
        gfpruns = []
        odruns = []
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
            filename = infile + "/" + file
            data = csv.reader(open(filename, 'rU'), dialect='excel')
            gfp = False
            gfpcontainer = []
            odcontainer = []
            for rows in data:
                if rows[7] == 'Meas A':
                    plate_ID.append(rows[2])
                    gfp = True
                if rows[0] in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P'] and gfp == True:
                    if rows[0] == 'A':
                        gfpcontainer.append(map(int,rows[1:]))
                    elif rows[0] == 'P':
                        gfpcontainer.append(map(int,rows[1:]))
#                        map(GFP.extend, rows[1:])
                        gfp = False
                        gfpruns.append(gfpcontainer)
                        gfpcontainer = []
                    else:
                        gfpcontainer.append(map(int,rows[1:]))
                elif rows[0] in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']:
                    if rows[0] == 'P':
                        odcontainer.append(map(float,rows[1:]))
                        odruns.append(odcontainer)
                        odcontainer = []
                    elif rows[1] == '- ':
                        break
                    else:
                        odcontainer.append(map(float,rows[1:]))
        else:
            continue
        GFP.append(gfpruns)
        OD.append(odruns)
#
#    print len(GFP), len(OD)
    return GFP, OD, plate_ID


def normalize (x,y):
    for i,j in itertools.izip(x,y):
        normalgfp = []
        normalod = []
        avgneggfp = []
        avgposgfp = []
        neggfp = []
        posgfp = []
        avgnegod = []
        avgposod = []
        negod = []
        posod = []
        normgfpcontainer = []
        normodcontainer = []
        for m,n in itertools.izip(i,j):
            negg,nego = m[-2],n[-2]
            posg,poso = m[-1],n[-1]
            neggfp.append(negg)
            posgfp.append(posg)
            negod.append(nego)
            posod.append(poso)
        ang = sum(neggfp)/len(neggfp)
        apg = sum(posgfp)/len(posgfp)

        avgposgfp.append(apg)
        avgneggfp.append(ang)
        ano = sum(negod)/len(negod)
        apo = sum(posod)/len(posod)
        avgposod.append(apo)
        avgnegod.append(ano)
        stdneg = ((np.std(neggfp))*3)
        stdpos = ((np.std(posgfp))*3)
#        stdnegod = float(np.std(negod)*3)
#        stdposod = float(np.std(posod)*3)
        z = 1.0-((stdneg+stdpos)/(ang-apg))
#        z1 = 1.0-((stdnegod + stdposod)/(ano-apo))
        GFPZFACTOR.append(z)
#        ODZFACTOR.append(z1)
        for m,n in itertools.izip(avgneggfp,avgposgfp):
            for x in i:
                for xi in x:
#                    a = m-xi
#                    b = m-n
#                    norm = (float(a)/float(b))
                    normgfp = (float(m-xi))/(float(m-n))*100
                    normgfpcontainer.append(normgfp)
                del normgfpcontainer[-1]
                del normgfpcontainer[-1]
                normalgfp.append(normgfpcontainer)
                normgfpcontainer = []

        for m,n in itertools.izip(avgnegod,avgposod):
            for x in j:
                for xi in x:
#                    a = m-xi
#                    b = m-n
#                    norm = (float(a)/float(b))
                    normod = ((m-xi)/(m-n))*100
                    normodcontainer.append(normod)
                del normodcontainer[-1]
                del normodcontainer[-1]
                normalod.append(normodcontainer)
                normodcontainer = []

        NORMALGFPDATA.append(normalgfp)
        NORMALODDATA.append(normalod)
    return
def normalizebyz (x,y):
    runavgneggfp = []
    runavgposgfp = []
    runavgnegod = []
    runavgposod = []
    for i,j in itertools.izip(x,y):
        runneggfpcontainer = []
        runposgfpcontainer = []
        runnegodcontainer = []
        runposodcontainer = []

#        avgneggfp = []
#        avgposgfp = []
#        neggfp = []
#        posgfp = []
#        avgnegod = []
#        avgposod = []
#        negod = []
#        posod = []

        for m,n in itertools.izip(i,j):
        #        avgneggfp = []
        #        avgposgfp = []
            neggfp = []
            posgfp = []
        #        avgnegod = []
        #        avgposod = []
            negod = []
            posod = []
            for q,r in itertools.izip(m,n):
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
#        avgposod.append(apo)
#        avgnegod.append(ano)
            stdneg = ((np.std(neggfp))*3)
            stdpos = ((np.std(posgfp))*3)
        #        stdnegod = float(np.std(negod)*3)
        #        stdposod = float(np.std(posod)*3)
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

        #        z1 = 1.0-((stdnegod + stdposod)/(ano-apo))

        #        ODZFACTOR.append(z1)
    print "...Read in %d files...\n...Read in %d plates..." % (len(runavgneggfp), len(plate_ID))
    for i in range(len(x)):



#        for m,n in itertools.izip(runavgneggfp,runavgposgfp):
#            if not len(m):
#                continue
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

#        for m,n in itertools.izip(runavgnegod,runavgposod):
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

def bindata (x,y):
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
#    print len(TWENTYFIVEOD), len(FIFTYGFP), len(SEVENTYFIVEGFP), len(HUNDREDGFP)
    return

def writealldata(path):
    print "...Making .csv files for each class of hits..."
    outf = open(path + '/' + 'Alldata.csv', 'wb')
    outcsv = csv.writer(outf)
    outcsv.writerow(['OD', 'GFP'])
    allgfpdata = TWENTYFIVEGFP + FIFTYGFP + SEVENTYFIVEGFP + HUNDREDGFP
    alloddata = TWENTYFIVEOD + FIFTYOD + SEVENTYFIVEOD + HUNDREDGFP
    for i,j in itertools.izip(alloddata,allgfpdata):
        outcsv.writerow([i,j])

def linregress():
    R = robjects.r

    twofivegfp = TWENTYFIVEGFP
    twofiveod = TWENTYFIVEOD
#    for i,j in itertools.izip(twofivegfp,twofiveod):
#        if i < 0:
#            del i,j
    allgfpdata = twofivegfp + FIFTYGFP + SEVENTYFIVEGFP + HUNDREDGFP
    alloddata = twofiveod + FIFTYOD + SEVENTYFIVEOD + HUNDREDOD
#    print np.shape(NORMALGFPDATA)


    fit = np.polyfit(alloddata, allgfpdata, 1)
    model = np.poly1d(fit)
    slope, intercept, r_value, p_value, std_err = sp.linregress(alloddata,allgfpdata)
    matdata = zip(alloddata, allgfpdata)
    print matdata[:10]
    print "...Bootstrapping the confidence intervals. This will take some time..."
#    CIs = bootstrap.ci(data=allgfpdata, statfunction=scipy.mean, alpha = 0.000001)
#    print CIs
    print 1.96*std_err
    CI = 1.96 * std_err
#    lower = CIs[0]
#    upper = CIs [1]
    c_y = [np.min(model(alloddata)),np.max(model(alloddata))]
    c_x = [np.min(alloddata),np.max(alloddata)]
    p_x = np.arange(-50,120,1)
    p_y = fit[0]*p_x+fit[0]
    lCI = p_y - abs(CI)
    uCI = p_y + abs(CI)
    predict = R['confint']
    lm = R['lm']
    r_vec1 = robjects.FloatVector(alloddata)
    r_vec2 = robjects.FloatVector(allgfpdata)
    robjects.globalenv["y"] = r_vec2
    robjects.globalenv["x"] = r_vec1
    rmodel = lm("y ~ x")
#    a = predict(rmodel)[1]
#    lower = predict(rmodel)[2]
#    upper = predict(rmodel)[3]
#    c = predict(rmodel)[4]
    upper = predict(rmodel, interval = "confidence", level = 0.9999)
    print upper
#    print(lower.names)
#    upper = predict(rmodel)['upper']
    return slope, intercept, lCI, uCI, p_x, p_y, c_x, c_y
#    fit = np.polyfit(alloddata, allgfpdata, 1)
#    model = np.poly1d(fit)
#    return model
#def plotbindata(folder, ave, m, b, low, high, p_x, p_y, c_x, c_y):
def plotbindata(folder, ave):
    print "...Plotting all data..."
    plt.plot(TWENTYFIVEOD,TWENTYFIVEGFP,'bo')
    plt.plot(FIFTYOD,FIFTYGFP,'co')
    plt.plot(SEVENTYFIVEOD,SEVENTYFIVEGFP,'yo')
    plt.plot(HUNDREDOD,HUNDREDGFP,'ro')
    x = np.arange(-120,120)
#    plt.plot(x, m*x + b, 'g-')
#    plt.plot(c_x, c_y, 'g-')
#    plt.plot(p_x, low, 'g--')
#    plt.plot(p_x, high, 'g--')
    plt.xlim(-50,120)
    plt.ylim(-50,120)
    plt.xlabel("Growth inhibition (% of positive control)")
    plt.ylabel("Fluorescence inhibition (% of positive control)")
    plt.title("Z'-factor is %.2f" % ave)
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
#    plt.axvline(-50,-50.120, linestyle = '--')
#    plt.axvline(-75,-120,120,linestyle = '--')
    outfile = open(folder + "/" + 'Scatter plot of all data.png', "w")
    plt.savefig(folder + "/" + 'Scatter plot of all data.png', dpi=300)
    outfile.close()
    plt.clf()

def calcz():
    avez = sum(GFPZFACTOR)/len(GFPZFACTOR)
#    aveo = sum(ODZFACTOR)/len(ODZFACTOR)
    float(avez)
#    float(aveo)
#    overall = (avez + aveo)/2
    return avez

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
    odclassIIcut = []
    odclassIIIcut = []
    print "...Finding compound IDs..."
    alldata = TWENTYFIVEOD + FIFTYOD + SEVENTYFIVEOD + HUNDREDOD
    for od in alldata:
        if od <= 35.0:
            odclassIcut.append(od)
        elif od > 35.0:
            odclassIIIcut.append(od)
            if od >= 50.0:
                odclassIIcut.append(od)
    countplate = 0
    countrow = 0
    rowdict = {0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G', 7:'H', 8:'I', 9:'J', 10:'K', 11:'L', 12:'M', 13:'N', 14:'O', 15:'P'}
#    print len(odclassIIIcut)
    for plateg, plateo in itertools.izip(NORMALGFPDATA, NORMALODDATA):
#        print len(i)
        for rowg, rowo in itertools.izip(plateg,plateo):
            for datg in range(len(rowg)):
                if rowg[datg] in abovefiftygfp and rowo[datg] in odclassIIcut:
                    if datg < 9:
                        CLASSIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]])
                    else:
                        CLASSIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+str(datg+1),plate_ID[countplate]])
                elif rowg[datg] in belowfiftygfp and rowo[datg] in odclassIIIcut:
                    if (rowo[datg]/rowg[datg]) >= 2 or (rowo[datg]/rowg[datg]) < 0:
                        if datg < 9:
                            CLASSIIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]])
                        else:
                            CLASSIIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+str(datg+1),plate_ID[countplate]])
                elif rowg[datg] in abovethirtyfivegfp:
                    if (rowg[datg]/rowo[datg]) >= 2 or (rowg[datg]/rowo[datg]) < 0:
                        if datg < 9:
                            CLASSIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]])
                        else:
                            CLASSIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+str(datg+1),plate_ID[countplate]])

            countrow += 1
        countrow = 0
        countplate += 1
#    countplate = 0
#    countrow = 0
#    for plateg, plateo in itertools.izip(NORMALGFPDATA, NORMALODDATA):
#            print len(i)
#        for rowg, rowo in itertools.izip(plateg,plateo):
#            for datg in range(len(rowg)):
#                if rowg[datg] in belowfiftygfp and rowo[datg] in odclassIIIcut:
#                    if (rowo[datg]/rowg[datg]) >= 2 or (rowo[datg]/rowg[datg]) < 0:
#                        if datg < 9:
#                            CLASSIIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+('0'+str(datg+1)),plate_ID[countplate]])
#                        else:
#                            CLASSIIIHIT.append([rowg[datg],rowo[datg],rowdict[countrow]+str(datg+1),plate_ID[countplate]])
#            countrow += 1
#        countrow = 0
#        countplate += 1
    print "...Still working..."
#    print len(CLASSIIHIT)
    for file in os.listdir(plate_path): #iterating through the files contained inside of a parent folder
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
            filename = plate_path + "/" + file
            data = csv.reader(open(filename, 'rU'), dialect='excel')
            for rows in data:
                for hits in CLASSIHIT:
                    id = hits[3]
                    if id == rows[3].upper():
                        hits.append(rows[1])
                        hits.append(rows[2])
#            for rows in data:
                for antibio in CLASSIIHIT:
                        antibioid = antibio[3]
                        if antibioid == rows[3].upper():
                            antibio.append(rows[1])
                            antibio.append(rows[2])
                for h in CLASSIIIHIT:
                    hid = h[3]
                    if hid == rows[3].upper():
                        h.append(rows[1])
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
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
            filename = comp_path + "/" + file
            data1 = csv.reader(open(filename, 'rU'), dialect='excel')
            for info in data1:
                for a in range(len(classIplateid)):
                    if classIplateid[a] == info[0] and classIplateloc[a] == info[1]:
                        CLASSIHIT[a].append(info[6])
                        CLASSIHIT[a].append(info[7])
                for b in range(len(classIIplateid)):
                    if classIIplateid[b] == info[0] and classIIplateloc[b] == info[1]:
                        CLASSIIHIT[b].append(info[6])
                        CLASSIIHIT[b].append(info[7])
                for c in range(len(classIIIplateid)):
                    if classIIIplateid[c] == info[0] and classIIIplateloc[c] == info[1]:
                        CLASSIIIHIT[c].append(info[6])
                        CLASSIIIHIT[c].append(info[7])
    return

def plotCIdata(CLASSIHIT, folder):
    print "...Plotting data..."

    plt.plot(TWENTYFIVEOD,TWENTYFIVEGFP,'o', color='0.95')
    plt.plot(FIFTYOD,FIFTYGFP,'o', color='0.95')
    plt.plot(SEVENTYFIVEOD,SEVENTYFIVEGFP,'o', color='0.95')
    plt.plot(HUNDREDOD,HUNDREDGFP,'o', color='0.95')
    for i in CLASSIHIT:
        plt.plot(i[1], i[0], 'o', color='g')
    plt.xlim(-50,120)
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

    plt.plot(TWENTYFIVEOD,TWENTYFIVEGFP,'o', color='0.95')
    plt.plot(FIFTYOD,FIFTYGFP,'o', color='0.95')
    plt.plot(SEVENTYFIVEOD,SEVENTYFIVEGFP,'o', color='0.95')
    plt.plot(HUNDREDOD,HUNDREDGFP,'o', color='0.95')
    for i in CLASSIIHIT:
        plt.plot(i[1], i[0], 'o', color='r')
    plt.xlim(-50,120)
    plt.ylim(-50,120)
    plt.xlabel("Growth inhibition (% of positive control)")
    plt.ylabel("Fluorescence inhibition (% of positive control)")
    plt.title("Plot of Class II hits from the aprA'::GFP HTS")
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
    print "...Plotting data..."

    plt.plot(TWENTYFIVEOD,TWENTYFIVEGFP, 'o', color='0.95')
    plt.plot(FIFTYOD,FIFTYGFP, 'o', color='0.95')
    plt.plot(SEVENTYFIVEOD,SEVENTYFIVEGFP, 'o', color='0.95')
    plt.plot(HUNDREDOD,HUNDREDGFP, 'o', color='0.95')
    for i in CLASSIIIHIT:
        plt.plot(i[1], i[0], 'o', color='c')
    plt.xlim(-50,120)
    plt.ylim(-50,120)
    plt.xlabel("Growth inhibition (% of positive control)")
    plt.ylabel("Fluorescence inhibition (% of positive control)")
    plt.title("Plot of Class III hits from the aprA'::GFP HTS")
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
    print "...Plotting data..."

    plt.plot(TWENTYFIVEOD,TWENTYFIVEGFP, 'o', color='0.95')
    plt.plot(FIFTYOD,FIFTYGFP, 'o', color='0.95')
    plt.plot(SEVENTYFIVEOD,SEVENTYFIVEGFP, 'o', color='0.95')
    plt.plot(HUNDREDOD,HUNDREDGFP, 'o', color='0.95')
    for i in CLASSIHIT:
        plt.plot(i[1], i[0], 'o', color='g')
    for j in CLASSIIHIT:
        plt.plot(j[1], j[0], 'o', color='r')
    for k in CLASSIIIHIT:
        plt.plot(k[1], k[0], 'o', color='c')
    plt.xlim(-50,120)
    plt.ylim(-50,120)
    plt.xlabel("Growth inhibition (% of positive control)")
    plt.ylabel("Fluorescence inhibition (% of positive control)")
    plt.title("Plot of Class I, II, and III hits\n from the aprA'::GFP HTS")
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
    print "...Making .csv files for each class of hits..."
    outf = open(path + '/' + 'Class I hits.csv', 'wb')
    outcsv = csv.writer(outf)
    outcsv.writerow(['Class I hits are binned at > 35% GFP inhibition and at least a two-fold difference between GFP and OD'])
    outcsv.writerow(["Fluorescence inhibition (% of positive control)", "Growth inhibition (% of positive control)", "Well location", "Plate number", "Library", "Library plate ID", "Compound catalog number", "Compound Name"])
    for i in CLASSIHIT:
        outcsv.writerow(i)
    outf1 = open(path + '/' + 'Class II hits.csv', 'wb')
    outcsv = csv.writer(outf1)
    outcsv.writerow(['Class II hits are binned at > 50% GFP inhibition and > 50% growth inhibition'])
    outcsv.writerow(["Fluorescence inhibition (% of positive control)", "Growth inhibition (% of positive control)", "Well location", "Plate number", "Library", "Library plate ID", "Compound catalog number", "Compound Name"])
    for j in CLASSIIHIT:
        outcsv.writerow(j)
    outf1 = open(path + '/' + 'Class III hits.csv', 'wb')
    outcsv = csv.writer(outf1)
    outcsv.writerow(['Class III hits are binned at < 75% GFP inhibition and > 75% growth inhibition'])
    outcsv.writerow(["Fluorescence inhibition (% of positive control)", "Growth inhibition (% of positive control)", "Well location", "Plate number", "Library", "Library plate ID", "Compound catalog number", "Coumpound Name"])
    for k in CLASSIIIHIT:
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

