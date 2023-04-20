# Collect


Collect.py
(Collect.py was inspired by Sean Li's bash script of the same name)

Simple Python script that collects folders and files into a __Collect__ directory at the users perferred location and then creates Symlinks within Category folders for easily finding data stored deep within file structures. 

The script requires a collect.txt file to be placed in any directory that you would like visible to the script, formatted as follows:

Date:YYYY_MM_DD 

Category:Category One

Category:Category Two 

Take note there is no space after the colon.  Also note that you can have as many categories as you would like, the contents of the folder will have a symlink in all categories. 

There are some helper scripts that the user can launch separately, such as new_collect_file.py, to add collect files to all subfolders within a given path. The collect file will be pre-populated with the date in the correct format based on the folders original creation date.  This script also has a --fix command line argument to fix misspelled or mislabled content.txt files as a batch rename. 

# Bids_Collect

bids_collect.py is a simialr but differnt execution of a similar idea. Used to keep a list of "Current" folders aggregated in a single location for reducing friction ina given workflow.  Since in this usecase, the folders all share the same name, and the "Current" folders are on a shared drive, using folder name rather than collect.txt is used in this script. 
