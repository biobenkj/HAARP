__author__ = 'benjaminjohnson'


import os
import subprocess
import datetime
import csv
import itertools
import matplotlib.pyplot as plt
from matplotlib_venn import venn2
from matplotlib_venn import venn3
import numpy as np
import scipy.stats as sp



C1_FD = []
C2_FD = []
C3_FD = []

C1_SD = []
C2_SD = []
C3_SD = []

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
    print "Creating a folder with which the comparison data will be placed."
    print "Default subfolder location will be in 'Comparison_Data' which is located on the Desktop"
    defined_path = find_path() + "/Comparison_Data"
    now = datetime.datetime.now()
    #all data folder will go into HTMAD_Data, if it doesn't already exist from previous runs it wil be created
    if not os.path.isdir(defined_path):
        os.mkdir(defined_path)
        print "Created folder 'Comparison_Data' on the Desktop"
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
    input1 = str(raw_input("Please enter the name of the folder on the Desktop containing the first dataset to compare:"))
    data_path1 = path + "/" + input1
    while not os.path.isdir(data_path1):
        new_input1 = str(raw_input("Sorry the software could not be find that folder on the desktop, try typing the folder name again or Q to quit:"))
        if new_input1.upper() == "Q":
            quit()
        data_path1 = path + "/" + new_input1
    input2 = str(raw_input("Please enter the name of the folder on the Desktop containing the second dataset to compare:"))
    data_path2 = path + "/" + input2
    while not os.path.isdir(data_path2):
        new_input2 = str(raw_input("Sorry the software could not be find that folder on the desktop, try typing the folder name again or Q to quit:"))
        if new_input2.upper() == "Q":
            quit()
        data_path2 = path + "/" + new_input2
    #    create_folder()
    return data_path1, data_path2

def read_inputs(data1, data2):
    for file in os.listdir(data1):
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
            filename1 = data1 + "/" + file
            dataset = csv.reader(open(filename1, 'rU'), dialect='excel')
            if file == 'Class I hits.csv':
                for row in dataset:
                    if row[0].startswith('Class') or row[0].startswith('Fluorescence'):
                        continue
                    else:
                        row.append('AprA Class I')
                        row.append('')
                        C1_FD.append(row)
            elif file == 'Class II hits.csv':
                for row in dataset:
                    if row[0].startswith('Class') or row[0].startswith('Fluorescence'):
                        continue
                    else:
                        row.append('AprA Class II')
                        row.append('')
                        C2_FD.append(row)
            else:
                for row in dataset:
                    if row[0].startswith('Class') or row[0].startswith('Fluorescence'):
                        continue
                    else:
                        row.append('AprA Class III')
                        row.append('')
                        C3_FD.append(row)

    for file in os.listdir(data2):
        extension = os.path.splitext(file)[1]   #finds the extension of the file, which for our purposes needs to be .txt
        if extension == ".csv": #checking if the file is a text file (ie ends in .txt)
            filename2 = data2 + "/" + file
            dataset = csv.reader(open(filename2, 'rU'), dialect='excel')
            if file == 'Class I hits.csv':
                for row in dataset:
                    if row[0].startswith('Class') or row[0].startswith('Fluorescence'):
                        continue
                    else:
                        row.append('')
                        row.append('HspX Class I')
                        C1_SD.append(row)
            elif file == 'Class II hits.csv':
                for row in dataset:
                    if row[0].startswith('Class') or row[0].startswith('Fluorescence'):
                        continue
                    else:
                        row.append('')
                        row.append('HspX Class II')
                        C2_SD.append(row)
            else:
                for row in dataset:
                    if row[0].startswith('Class') or row[0].startswith('Fluorescence'):
                        continue
                    else:
                        row.append('')
                        row.append('HspX Class III')
                        C3_SD.append(row)
#    ALL_FIRST_DATA = C1_FD + C2_FD + C3_FD
#    ALL_SECOND_DATA = C1_SD + C2_SD + C3_SD
    print len(C1_FD), len(C2_FD), len(C3_FD)

    print len(C1_SD), len(C2_SD), len(C3_SD)

    return


def comparison():
    ALL_FIRST_DATA = C1_FD + C2_FD + C3_FD
    ALL_SECOND_DATA = C1_SD + C2_SD + C3_SD
    for ahit in C1_FD:
        for nhit in ALL_SECOND_DATA:
            if ahit[4] == nhit[4] and ahit[5] == nhit[5]:
                ahit[11] = nhit[11]
    for ahit2 in C2_FD:
        for nhit in ALL_SECOND_DATA:
            if ahit2[4] == nhit[4] and ahit2[5] == nhit[5]:
                ahit2[11] = nhit[11]
    for ahit3 in C3_FD:
        for nhit in ALL_SECOND_DATA:
            if ahit3[4] == nhit[4] and ahit3[5] == nhit[5]:
                ahit3[11] = nhit[11]

    for hhit1 in C1_SD:
        for nhit in ALL_FIRST_DATA:
                if hhit1[4] == nhit[4] and hhit1[5] == nhit[5]:
                    hhit1[10] = nhit[10]
    for hhit2 in C2_SD:
        for nhit in ALL_FIRST_DATA:
            if hhit2[4] == nhit[4] and hhit2[5] == nhit[5]:
                hhit2[10] = nhit[10]
    for hhit3 in C3_SD:
        for nhit in ALL_FIRST_DATA:
            if hhit3[4] == nhit[4] and hhit3[5] == nhit[5]:
                hhit3[10] = nhit[10]
    return

def makeavenndiagram(folder):
    apracount = 0
    hspxcount = 0
    bothcount = 0
    ALL_FIRST_DATA = C1_FD + C2_FD + C3_FD
    ALL_SECOND_DATA = C1_SD + C2_SD + C3_SD
    for i in ALL_SECOND_DATA:
        if i[11].startswith('HspX') and i[10].startswith('AprA'):
            bothcount += 1
        elif i[11].startswith('HspX'):
            hspxcount += 1
    print "...Making a Venn Diagram of hits..."
    venn2(subsets=(166, hspxcount, bothcount), set_labels = ('AprA HTS-specific hits', 'HspX HTS-specific hits', 'Common hits'))
    plt.title('AprA and HspX HTS hit comparisons')
    outf = open(folder + '/' + 'Venn Diagram.png', 'w')
    plt.savefig(folder + "/" + 'Venn Diagram.png', dpi=300)
    outf.close()
    plt.clf()
    return

def fancyvenndiagram(folder):
    apraCIcount = 0
    hspxbothCIcount = 0
    hspxbothCIIcount = 0
    hspxbothCIIIcount = 0
    hspxCIcount = 0
    hspxCIIcount = 0
    hspxCIIIcount = 0
    ALL_SECOND_DATA = C1_SD + C2_SD + C3_SD
    for i in C1_SD:
        if i[8] == 'AprA Class I' and i[9] == 'HspX Class I':
            hspxbothCIcount += 1
        elif i[8] == 'AprA Class II' and i[9] == 'HspX Class I':
            hspxbothCIIcount += 1
        elif i[8] == 'AprA Class III' and i[9] == 'HspX Class I':
            hspxbothCIIIcount += 1
        else:
            hspxCIcount += 1
    for j in ALL_SECOND_DATA:
#        if j[9] == 'HspX Class I' and j[8] != 'AprA Class I':
#            if j[8] == 'AprA Class II':
#                continue
#            elif j[8] == 'AprA Class III':
#                continue
#            else:
#            hspxCIcount += 1
        if j[9] == 'HspX Class II' and j[8] != 'AprA Class I':
#            if j[8] == 'AprA Class II':
#                continue
#            elif j[8] == 'AprA Class III':
#                continue
#            else:
            hspxCIIcount += 1
        elif j[9] == 'HspX Class III' and j[8] != 'AprA Class I':
#            if j[8] == 'AprA Class II':
#                continue
#            elif j[8] == 'AprA Class III':
#                continue
#            else:
            hspxCIIIcount += 1
#    print 'apraCIcount = %d' % apraCIcount
#    print 'hspxbothCIcount = %d' % hspxbothCIcount
#    print 'hspxbothCIIcount = %d' % hspxbothCIIcount
#    print 'hspxbothCIIIcount = %d' % hspxbothCIIIcount
#    print 'hspxCIcount = %d' % hspxCIcount
#    print 'hspxCIIcount = %d' % hspxCIIcount
#    print 'hspxCIIIcount = %d' % hspxCIIIcount
    venn3(subsets = (149, 238, 14, 815, 19, 0,0), set_labels = ('AprA CI hits', 'HspX CI hits', 'HspX CII hits'))
    plt.title('AprA and HspX HTS hit comparisons')
    outf = open(folder + '/' + 'Venn Diagram1.png', 'w')
    plt.savefig(folder + "/" + 'Venn Diagram1.png', dpi=300)
    outf.close()
    plt.clf()

    apraCIIcount = 0
    hspxbothCIcount = 0
    hspxbothCIIcount = 0
    hspxbothCIIIcount = 0
    hspxCIcount = 0
    hspxCIIcount = 0
    hspxCIIIcount = 0
    ALL_SECOND_DATA = C1_SD + C2_SD + C3_SD
    for i in C2_SD:
        if i[8] == 'AprA Class I' and i[9] == 'HspX Class II':
            hspxbothCIcount += 1
        elif i[8] == 'AprA Class II' and i[9] == 'HspX Class II':
            hspxbothCIIcount += 1
        elif i[8] == 'AprA Class III' and i[9] == 'HspX Class II':
            hspxbothCIIIcount += 1
        else:
            hspxCIIcount += 1
    for j in ALL_SECOND_DATA:
        if j[9] == 'HspX Class I' and j[8] != 'AprA Class II':
#            if j[8] == 'AprA Class I':
#                continue
#            elif j[8] == 'AprA Class III':
#                continue
#            else:
            hspxCIcount += 1
#        elif j[9] == 'HspX Class II' and j[8] != 'AprA Class II':
#            if j[8] == 'AprA Class I':
#                continue
#            elif j[8] == 'AprA Class III':
#                continue
#            else:
#            hspxCIIcount += 1
        elif j[9] == 'HspX Class III' and j[8] != 'AprA Class II':
#            if j[8] == 'AprA Class I':
#                continue
#            elif j[8] == 'AprA Class III':
#                continue
#            else:
            hspxCIIIcount += 1
#    venn3(subsets = (370, 235, 17, 516, 318, 0,0), set_labels = ('AprA CII\nhits', 'HspX CI\nhits', 'HspX CII\nhits'))
    venn2(subsets = (370, 516, 318), set_labels = ('AprA CII\nhits', 'HspX CII\nhits', 'Common CII\n hits'))
    plt.title('AprA and HspX HTS hit comparisons')
    outf = open(folder + '/' + 'Venn Diagram2.png', 'w')
    plt.savefig(folder + "/" + 'Venn Diagram2.png', dpi=300)
    outf.close()
    plt.clf()
    print 'apraCIcount = %d' % apraCIcount
    print 'hspxbothCIcount = %d' % hspxbothCIcount
    print 'hspxbothCIIcount = %d' % hspxbothCIIcount
    print 'hspxbothCIIIcount = %d' % hspxbothCIIIcount
    print 'hspxCIcount = %d' % hspxCIcount
    print 'hspxCIIcount = %d' % hspxCIIcount
    print 'hspxCIIIcount = %d' % hspxCIIIcount

    apraCIIIcount = 0
    hspxbothCIcount = 0
    hspxbothCIIcount = 0
    hspxbothCIIIcount = 0
    hspxCIcount = 0
    hspxCIIcount = 0
    hspxCIIIcount = 0
    ALL_SECOND_DATA = C1_SD + C2_SD + C3_SD
    for i in C3_FD:
        if i[9] == 'HspX Class I':
            hspxbothCIcount += 1
        elif i[9] == 'HspX Class II':
            hspxbothCIIcount += 1
        elif i[9] == 'HspX Class III':
            hspxbothCIIIcount += 1
        else:
            apraCIIIcount += 1
    for j in ALL_SECOND_DATA:
        if j[9] == 'HspX Class I' and j[8] != 'AprA Class III':
#            if j[8] == 'AprA Class I':
#                continue
#            elif j[8] == 'AprA Class III':
#                continue
#            else:
            hspxCIcount += 1
        elif j[9] == 'HspX Class II' and j[8] != 'AprA Class III':
#            if j[8] == 'AprA Class I':
#                continue
#            elif j[8] == 'AprA Class III':
#                continue
#            else:
            hspxCIIcount += 1
        elif j[9] == 'HspX Class III' and j[8] != 'AprA Class III':
#            if j[8] == 'AprA Class I':
#                continue
#            elif j[8] == 'AprA Class III':
#                continue
#            else:
            hspxCIIIcount += 1
    venn3(subsets = (apraCIIIcount, hspxCIcount, hspxbothCIcount, hspxCIIcount, hspxbothCIIcount, 0,0), set_labels = ('AprA CIII hits', 'HspX CI hits', 'HspX CII hits'))
    plt.title('AprA and HspX HTS hit comparisons')
    outf = open(folder + '/' + 'Venn Diagram3.png', 'w')
    plt.savefig(folder + "/" + 'Venn Diagram3.png', dpi=300)
    outf.close()
    plt.clf()
    return

def writeitout(folder):
    print "...Making .csv files for each class of hits..."
    outf = open(folder + '/' + 'AprA Class I hits comparison.csv', 'wb')
    outcsv = csv.writer(outf)
    #    outcsv.writerow(['Class I hits are binned at > 35% GFP inhibition and at least a two-fold difference between GFP and OD'])
    outcsv.writerow(["Fluorescence inhibition (% of positive control)", "Growth inhibition (% of positive control)", "Well location", "Plate number", "Library", "Library plate ID", "Compound catalog number", "Compound Name", "AprA Class Type", "HspX Class Type"])
    for i in C1_FD:
        outcsv.writerow(i)
    outf = open(folder + '/' + 'AprA Class II hits comparison.csv', 'wb')
    outcsv = csv.writer(outf)
    #    outcsv.writerow(['Class I hits are binned at > 35% GFP inhibition and at least a two-fold difference between GFP and OD'])
    outcsv.writerow(["Fluorescence inhibition (% of positive control)", "Growth inhibition (% of positive control)", "Well location", "Plate number", "Library", "Library plate ID", "Compound catalog number", "Compound Name", "AprA Class Type", "HspX Class Type"])
    for i in C2_FD:
        outcsv.writerow(i)
    outf = open(folder + '/' + 'AprA Class III hits comparison.csv', 'wb')
    outcsv = csv.writer(outf)
    #    outcsv.writerow(['Class I hits are binned at > 35% GFP inhibition and at least a two-fold difference between GFP and OD'])
    outcsv.writerow(["Fluorescence inhibition (% of positive control)", "Growth inhibition (% of positive control)", "Well location", "Plate number", "Library", "Library plate ID", "Compound catalog number", "Compound Name", "AprA Class Type", "HspX Class Type"])
    for i in C3_FD:
        outcsv.writerow(i)
    outf = open(folder + '/' + 'HspX Class I hits comparison.csv', 'wb')
    outcsv = csv.writer(outf)
    #    outcsv.writerow(['Class I hits are binned at > 35% GFP inhibition and at least a two-fold difference between GFP and OD'])
    outcsv.writerow(["Fluorescence inhibition (% of positive control)", "Growth inhibition (% of positive control)", "Well location", "Plate number", "Library", "Library plate ID", "Compound catalog number", "Compound Name", "AprA Class Type", "HspX Class Type"])
    for i in C1_SD:
        outcsv.writerow(i)
    outf = open(folder + '/' + 'HspX Class II hits comparison.csv', 'wb')
    outcsv = csv.writer(outf)
    #    outcsv.writerow(['Class I hits are binned at > 35% GFP inhibition and at least a two-fold difference between GFP and OD'])
    outcsv.writerow(["Fluorescence inhibition (% of positive control)", "Growth inhibition (% of positive control)", "Well location", "Plate number", "Library", "Library plate ID", "Compound catalog number", "Compound Name", "AprA Class Type", "HspX Class Type"])
    for i in C2_SD:
        outcsv.writerow(i)
    outf = open(folder + '/' + 'HspX Class III hits comparison.csv', 'wb')
    outcsv = csv.writer(outf)
    #    outcsv.writerow(['Class I hits are binned at > 35% GFP inhibition and at least a two-fold difference between GFP and OD'])
    outcsv.writerow(["Fluorescence inhibition (% of positive control)", "Growth inhibition (% of positive control)", "Well location", "Plate number", "Library", "Library plate ID", "Compound catalog number", "Compound Name", "AprA Class Type", "HspX Class Type"])
    for i in C3_SD:
        outcsv.writerow(i)
    return

