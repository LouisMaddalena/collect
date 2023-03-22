import os
import datetime
import argparse

#Simple accompanying script to create new collect.txt files in all folders and sub folders within a given path
#Within each content.txt file the original creation date of that folder will be written in sortable date format

#Script also has option to rename files run as follows:
# Python3 new_collect_file.py --fix "conllect.txt" "wrong_file.txt" 




def create_collect_file(folder_path):
    collect_file = os.path.join(folder_path, 'collect.txt')
    if not os.path.exists(collect_file):
        folder_creation_time = os.path.getctime(folder_path)
        creation_date = datetime.datetime.fromtimestamp(folder_creation_time).strftime("Date:%Y_%m_%d")
        category = "Category:"
        with open(collect_file, 'w') as file:
            file.write(f"{creation_date}\n{category}")

def fix_mispelled_file(folder_path, correct_name, mispelled_name):
    mispelled_file = os.path.join(folder_path, mispelled_name)
    correct_file = os.path.join(folder_path, correct_name)
    if os.path.exists(mispelled_file) and not os.path.exists(correct_file):
        os.rename(mispelled_file, correct_file)

def crawl_directory_tree(start_path, fix=False, correct_name=None, mispelled_name=None):
    for root, dirs, files in os.walk(start_path):
        if fix:
            fix_mispelled_file(root, correct_name, mispelled_name)
        else:
            create_collect_file(root)
        for dir in dirs:
            subdir_path = os.path.join(root, dir)
            if fix:
                fix_mispelled_file(subdir_path, correct_name, mispelled_name)
            else:
                create_collect_file(subdir_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create collect.txt files in directories.')
    parser.add_argument('--fix', nargs=2, metavar=('correct_name', 'mispelled_name'), help='Fix mispelled filenames')

    args = parser.parse_args()

    start_path = input("Begin Directory Tree Path: ")  # Replace with your directory path

    if args.fix:
        correct_name, mispelled_name = args.fix
        crawl_directory_tree(start_path, fix=True, correct_name=correct_name, mispelled_name=mispelled_name)
    else:
        crawl_directory_tree(start_path)
