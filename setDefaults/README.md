The Canvas gradebook provides a method to set default scores for single assignments at a time. When a course has many assignments, or the course is spread over many sections, that method is not practical. **setDefaults** is written to overcome that problem. 

# What it does:
It takes a set of assignment names. For each assignment, it searches your Canvas gradebook to find any blank entries, and sets their scores to 0. 
(It skips anyone that either already has a score in the gradebook for that assignment, or has the assignment excused from their grade.)


**Dependencies**: This uses the python canvasapi library.

# To Use
Update the first column of the closedAssns.csv file with the name of the assignments whose default scores you are setting. Make sure the names you enter match the assignment names in Canvas. 

# Things to update in the file
Make sure to set the *API_URL* variable to the url of your Canvas instance, *API_KEY* to your Canvas API key, and *CanvasCourseNumber* to the Canvas id number for your course (that you can read from the address bar from inside your Canvas class).

# To run:
From a terminal in the directory:

    python setDefaults.py

# What if you want to set the default score to something besides 0?
Find the bottom line of the setDefaults.py file. It should currently look like this:

    s.edit(submission={'posted_grade':0})

Change that 0 to the score you want the assignments to be defaulted to.
