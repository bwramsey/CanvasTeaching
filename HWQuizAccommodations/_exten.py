from canvasapi import Canvas
import concurrent.futures
import csv

# this script sets time extensions for SLDS students
# add your API Key below
API_URL = "https://********************"  # Replace with your Canvas instance
API_KEY = "**************************"  # Replace with your API key

# setup the connection to Carmen
carmen = Canvas( API_URL, API_KEY )

#strQuizName = "Participation Warmup: An Application of Limits (AAOL)"
# File name of csv of slds students (Format: [Name, 1.5, sect#])
strSLDSFilename = "slds.csv"
strQuizFilename = "quizNames.csv"

# HW Quizzes are 10 minutes
halfTime = 5
fullTime = 10

# course section-to-carmenID dictionary
# update with your values
sections = [12345]
dictID = {12345:902104}
NUM_SECTIONS = 1

# read the quiznames from the csv file
quizFile = open(strQuizFilename, 'r', encoding="utf-8-sig")
csvQuizNames = csv.reader( quizFile )
quizNameList = list( csvQuizNames )  

# read the slds accommodations from csv file
sldsFile = open(strSLDSFilename, 'r', encoding="utf-8-sig")
csvSLDSNames = csv.reader( sldsFile )
sldsFullDataList = list( csvSLDSNames )  


print("Setting accommodations for the following:")
for qz in quizNameList:
    print(qz[0])



# For each section
# Define the thread tasks -> One thread for each section
def setExtensions(sect):
    # read SLDS students for the section
    sldsDataList = [ [ s[0], s[1] ] for s in sldsFullDataList if len(s)>0 and s[2]==str(sect)]
    #print( sldsDataList )

    # setup list of slds student names and accommodations
    # These are read from the slds.csv file, not from Carmen
    extNames = []
    extAllow = []
    for std in sldsDataList:
        extNames.append(std[0])
        extAllow.append(std[1])

    # initialize dictionary of Name:extended_time for the slds students
    extTime = {}
    # populate the extTime dictionary
    for i in range(len(extAllow)):
        if extAllow[i] == '1.5':
            extTime[extNames[i]] = halfTime
        elif extAllow[i] == '2' or extAllow[i] == '2.0':
            extTime[extNames[i]] = fullTime
        elif extAllow[i] == '2.5':
            extTime[extNames[i]] = fullTime + halfTime
        else:
            print("Unknown extension: " + str(extAllow[i]) + " for student:" + extNames[i])

    # connect to the course
    course = carmen.get_course(dictID[sect])
    usrs = course.get_users()

    # initialize dictionary of Name:id for slds students in this section
    # Students here are read from the Carmen course
    extID = {}
    # populate dictionary of Name:id for slds students
    for u in usrs:
        if u.name in extNames:
            extID[u.name]= u.id

    # construct the extensions string to send to Carmen.
    # since HW Quizzes are same length, this should work for them, too.
    if extID:
        ext = []
        for std in extNames:
    #        if std in extTime.keys():
            if std in extID.keys():     # extID is a (possibly proper) subset of extTime.keys(), read from the current course
                ext.append( {'user_id':extID[std], 'extra_time':extTime[std]})
            else:
                print( "Student: " + std + " not found?")

        # find all quizzes from the course
        quizzes = course.get_quizzes()

        # for each quiz to be updated
        for strQuizName in [q[0] for q in quizNameList if len(q)>0]:    
            # find the quiz with that name
            tmp = [q for q in quizzes if q.title == strQuizName]
            if len(tmp) == 0:
                print( "Quiz named: ", strQuizName, " not found.")
                exit()
            # if there's one found...
            theOne = tmp[0]
            print("Section: " + str(sect) + " Setting extensions for Quiz titled:", theOne)
            theOne.set_extensions( ext )

    print(f"Section: {sect} completed.")



# Mainline -> setup the threads and let them run
with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_SECTIONS) as executor:
    # Submit tasks to the executor
    futures = [executor.submit(setExtensions, sectn) for sectn in sections]

    # Wait for all tasks to complete
    for future in concurrent.futures.as_completed(futures):
        result = future.result() # Get the result of the task (if any)