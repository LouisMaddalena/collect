# Collect


Collect.py
(Collect.py was inspired by Sean Li's bash script of the same name)

Simple Python script that collects folders and files into a __Collect__ directory at the users perferred location and then creates Symlinks within Category folders for easily finding data stored deep within file structures. 

The script requires a collect.txt file to be placed in any directory that you would like visible to the script, formatted as follows:

Date:YYYY_MM_DD 

Category:Category One

Category:Category Two 

Take note there is no space after the colon.  Also note that you can have as many categories as you would like, the contents of the folder will have a symlink in all categories. 

