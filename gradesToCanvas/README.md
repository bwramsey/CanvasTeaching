# What it does
*gradesToCanvas* takes the exported grade csv files from an assignment in Gradescope and uses them to transfer the grades to the Canvas gradebook. It is setup to work for several Canvas course sections using the same Gradescope course.

# When setting up Gradescope
To do this, we need a common StudentID that can be shared between Gradescope and Canvas. It is setup to use our registrar's student ID number as this intermediary as it is already in Canvas as the *sis_user_id* field of the canvasapi student. When adding students to the Gradescope roster, include this as Gradescope's *Student ID* field.

