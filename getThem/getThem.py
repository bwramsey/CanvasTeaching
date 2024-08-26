from canvasapi import Canvas
from urllib import request
import csv
import time

API_URL = "..."
API_KEY = "..."

# section numbers from Registrar system. The files downloaded will be named after these section numbers.
sections = [...]
# dictionary to get lookup canvas course_id from section numbers
dictCourseID = {...}

# initialize the canvas object
carmen = Canvas( API_URL, API_KEY )

#setup dictionary of courses
dictCourse = {}
for sec in sections:
    dictCourse[sec] = carmen.get_course( dictCourseID[sec] )
    print( "Section: " + str(sec) + " is course: " + str(dictCourse[sec]))

# prompt for the Check-in week we're using. This tells us the name of the quiz being searched for below
cNum = input("Which check-in week is this?: ")
strCName = "Check-in: Week " + str(cNum)


# create dictionary of the checkin surveys
dictCheckin = {}
for sec in sections:
    print( "Searching for Check-in in section " + str(sec) )
    quizzes = dictCourse[sec].get_quizzes()
    tmp = [t for t in quizzes if t.title == strCName]
    if len(tmp) > 0:
        dictCheckin[sec] = tmp[0]
        print(strCName + " found in section " + str(sec))
    else:
        print("Section " + str(sec) + " does not have survey named: " + strCName)
        exit()

# list of sections for whom the "files" attribute is not yet ready to download
# the section numbers will be removed from here as their files are downloaded
reportFlag = [sec for sec in sections]

# setup dictionary of checkin reports.
# may be making initial call to create the reports...
dictReport = {}
for sec in sections:
    dictReport[sec] = dictCheckin[sec].create_report('student_analysis')


# loop through sections for which there are still reports to download
while len(reportFlag) > 0:
    for sec in reportFlag:
        # it's ready to download once the report has the "file" attribute
        if hasattr( dictReport[sec], "file" ):
            # download the report and write to a csv, then mark the section as having been read (remove section from reportFlag list)
            response=request.urlopen(dictReport[sec].file['url'])
            csvResp = response.read()
            csvstr = str(csvResp).strip("b'")
            lines=csvstr.split("\\n")
            print("Writing file: " + str(sec) + ".csv")
            f = open(str(sec)+".csv", "w")
            for line in lines:
                f.write( line + "\n")
            f.close()
            reportFlag.remove(sec)

    # if there are  still reports to find, wait 3 seconds
    if len(reportFlag)>0:
        time.sleep(3)
exit()


