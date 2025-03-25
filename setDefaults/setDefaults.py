from canvasapi import Canvas
import csv

API_URL = "***" # the URL of 
API_KEY = "*****" # Replace the ***** with your Carmen API key
CanvasCourseNumber = *** #Enter Canvas course number here

# the name of the file to indicate which assignments to set defaults for
strAssnFilename = "ClosedAssns.csv" # CSV file with assignment names down the first column

AssnFile = open(strAssnFilename, 'r', encoding="utf-8-sig")
csvAssnNames = csv.reader( AssnFile )
AssnNameList = list( csvAssnNames )  
AssnNameList = [a[0] for a in AssnNameList] # go from list of list of names to just list of names


canvas = Canvas( API_URL, API_KEY )
course = canvas.get_course(CanvasCourseNumber)
assns = course.get_assignments()
usrs = course.get_users()


# given a submission from the Carmen course, find the name of the submitting user
# Only needed for displaying status info when a blank is found in the gradebook.
def getNameFromSubmission( subm ):
    temp = [u for u in usrs if u.id == subm.user_id]
    if temp:
        return temp[0].name
    else:
        return ''

#loop through each assignment, printing status info to terminal.
for assignmentName in AssnNameList:
	print(f"Working on: {assignmentName}")
  
	tmp = [asn for asn in assns if asn.name == assignmentName]
	if not tmp:
		print(f"Assignment: {assignmentName} not found")
		continue

  # Assignment names should be unique
	asn=tmp[0]
	subs = asn.get_submissions()
	
	# If no score AND not excused	(Have to check both conditions. Canvas leaves score as None if assignment was excused.)
	for s in subs:
		if s.score is None and not s.excused:
			print(f"Found a blank one: {getNameFromSubmission(s)}") # Print status
			s.edit(submission={'posted_grade':0}) # saves 0 as the student's new score
	



 
 
