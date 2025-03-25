import csv  # working with csv files
import os   # reading/writing files/directories
import sys  # for sys.exit if no valid file is found
from enum import Enum # enumeration for different assignment types
import concurrent.futures # parallel threading

from canvasapi import Canvas

# enum to handle the different assignment types
class AssignmentType(Enum):
    MIDTERM = 1
    WRITTENHOMEWORK = 2
    FINAL = 3

MAX_THREADS = 10

API_URL = "*****" # Replace ***** with the URL to your Canvas instance
API_KEY = "*****" # Repalce ***** with your Canvas API key

# CHANGE IN HERE to match the assignment types you need --------------------------------------------
# This block sets assignmentName and aType (the assignment type).
# The assignment type will determine how many files got downloaded from Gradescope.
k = int(input("Which type? (1) Midterm or (2) Written Homework or (3) Final?"))
while k not in [1, 2, 3]:
    k = int(input("Which type? (1) Midterm or (2) Written Homework or (3) Final"))
if k == 1:
    MNum = input("Which Midterm number (1 - 5): ")
    while int(MNum) not in [1, 2, 3, 4, 5]:
        MNum = input("Which Midterm number (1 - 5): ")

    assignmentName = "Midterm " + MNum
    aType = AssignmentType.MIDTERM

elif k == 2:
    MNum = input("Which WH number (1 - 5): ")
    while int(MNum) not in [1, 2, 3, 4, 5]:
        MNum = input("Which WH number (1 - 5): ")
    
    assignmentName = "Written Homework " + MNum
    aType = AssignmentType.WRITTENHOMEWORK

elif k==3:
    assignmentName = "Final Exam"
    aType = AssignmentType.FINAL

print( "Transferring: " + assignmentName )

# course section-to-canvasID dictionary
sections = []  # list of the registrar's section numbers for the lecture section
dictCourseID = {} # dictionary assigning to each registrar section number, the Canvas ID number for the section


# Important columns from Gradescope exported grade csv
gradeSIDColumn = 2 # ID column from Gradescope -> use ID for matching with Canvas gradebook
gradeScoreColumn = 5 # column from Gradescope wth assignment score
gradeStatusColumn = 7 # column to check if assignment is 'Graded' or 'Missing'


# setup the connection to canvas
canvas = Canvas( API_URL, PAM_KEY )

# -------------------------------------------------------------------------------------


# search the directory for ".csv" files
fileList = []
for file in os.listdir("./"):
    if file.endswith(".csv"):
        fileList.append( file )

if len(fileList) < 1:
    sys.exit("Move a valid gradebook file into this directory. ")

# print a list of csv files for the user to select
for num, name in enumerate( fileList, start=1 ):
    print( str(num) +") " + name )

# for WH, only 1 GS file to read
if aType == AssignmentType.WRITTENHOMEWORK:
    indx = input("Enter number for gradebook file to use: ")
    gradeFilename = fileList[int(indx)-1]
    print("You selected:" + gradeFilename)

    # open the csv file and attach it to a reader
    gradeFile = open(gradeFilename, 'r')
    csvGrade =csv.reader( gradeFile )
    gradeDataList = list( csvGrade )
    # Close up the files
    gradeFile.close()

# for midterm or final, 4 GS files (one for each exam form)
elif aType == AssignmentType.MIDTERM or aType == AssignmentType.FINAL:
    indxA = input("Enter number for score file from Gradescope for FORM A: ")
    gradeFilenameA = fileList[int(indxA)-1]
    print(gradeFilenameA)
    indxB = input("Enter number for score file from Gradescope for FORM B: ")
    gradeFilenameB = fileList[int(indxB)-1]
    print(gradeFilenameB)
    indxC = input("Enter number for score file from Gradescope for FORM C: ")
    gradeFilenameC = fileList[int(indxC)-1]
    print(gradeFilenameC)
    indxD = input("Enter number for score file from Gradescope for FORM D: ")
    gradeFilenameD = fileList[int(indxD)-1]
    print(gradeFilenameD)

    gradeFileA = open(gradeFilenameA, 'r')
    csvGradeA =csv.reader( gradeFileA )
    gradeDataList =  list( csvGradeA )
    gradeFileB = open(gradeFilenameB, 'r')
    csvGradeB =csv.reader( gradeFileB )
    gradeDataListB =  list( csvGradeB )
    gradeFileC = open(gradeFilenameC, 'r')
    csvGradeC =csv.reader( gradeFileC )
    gradeDataListC =  list( csvGradeC )
    gradeFileD = open(gradeFilenameD, 'r')
    csvGradeD =csv.reader( gradeFileD )
    gradeDataListD =  list( csvGradeD )

    gradeDataList.extend(gradeDataListB)
    gradeDataList.extend(gradeDataListC)
    gradeDataList.extend(gradeDataListD)
    gradeFileA.close()
    gradeFileB.close()
    gradeFileC.close()    
    gradeFileD.close()



# remove header row and missing papers from data
# this list should only have the rows corresponding to graded submissions.
gradeDataList = [x for x in gradeDataList if x[gradeStatusColumn] != "Status" and x[gradeStatusColumn]== "Graded" ]

# initialilze a couple dictionaries to track student scores and student IDs. 
# Use the registrar system's SIS_ID as the key instead of student names so
# this can deal with multiple students with same name
dictIDScore={ } # SIS_ID:Score
dictIDtoID = { } # SIS_ID:CanvasID


#use grade list to setup dictIDScore dictionary
for stdt in gradeDataList:
    # only work with "Graded" assignments
    if stdt[gradeStatusColumn] == 'Graded':
        if float(stdt[gradeScoreColumn]) < 0:
            stdt[gradeScoreColumn] = '0'
        dictIDScore[ stdt[gradeSIDColumn] ] = stdt[gradeScoreColumn]


# send scores for a section to Canvas for processing
def sendScore(sectn):
    dictIDtoID = {} # reinitialize the ID-to-ID dictionary
    crs = canvas.get_course( dictCourseID[sectn] )
    # grab the STUDENTS from canvas
    canvasStdtList = crs.get_users(enrollment_role='StudentEnrollment')
    
    # setup the SIS_ID:CanvasID list
    for std in canvasStdtList:
        dictIDtoID[ std.sis_user_id ] = std.id

    # find the assignment from assignmentName string setup earlier
    allAssigns = crs.get_assignments()
    tmp = [a for a in allAssigns if a.name == assignmentName ]
    if len(tmp) == 0:
        print( "Assignment: " + assignmentName + " not found in section: ", sectn )
    else:
        asn = tmp[0]
        print( "Assignment found in section: ", sectn)

        # now we can write the data
        for std in canvasStdtList:
            if std.sis_user_id in dictIDScore.keys():
                subm = asn.get_submission(dictIDtoID[std.sis_user_id])
                subm.edit(submission={'posted_grade':dictIDScore[std.sis_user_id]})
    print(f"Section {sectn}: Transfer completed.")

# Mainline -> setup the threads and let them run. Spins each lecture section as a separate thread.
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    # Submit tasks to the executor
    futures = [executor.submit(sendScore, sect) for sect in sections]

    # Wait for all tasks to complete
    for future in concurrent.futures.as_completed(futures):
        result = future.result() # Get the result of the task (if any)