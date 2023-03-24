import os
import sys
import argparse
from pathlib import Path
import shutil

#inspired by Sean Li's bash script called "Collect"

# Function to find collect.txt files in the given directory and its subdirectories
def find_collect_txt_files(path):
    path = os.path.abspath(path)
    for folder, _, files in os.walk(path):
        if 'collect.txt' in files or '.collect.txt' in files:
            file_name = 'collect.txt' if 'collect.txt' in files else '.collect.txt'
            yield os.path.join(folder, file_name)
            
#Function to hide collect files from user and other scripts that omit hidden files            
def hide_collect_txt_files(path):
    path = os.path.abspath(path)
    for folder, _, files in os.walk(path):
        if 'collect.txt' in files:
            old_path = os.path.join(folder, 'collect.txt')
            new_path = os.path.join(folder, '.collect.txt')
            os.rename(old_path, new_path)
            print(f'Renamed {old_path} to {new_path}')

# Function to parse collect.txt file and extract date and categories
def parse_collect_txt(file_path):
    date = None
    categories = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.lower().startswith('date:'):
                date = line.strip().split(':')[1]
            elif line.lower().startswith('category:'):
                categories.append(line.strip().split(':')[1])
    print(f'Parsed {file_path}: Date={date}, Categories={categories}')
    return date, categories

# Function to create symbolic links based on the categories and date
def create_sym_links(collect_txt_path, date, categories, base_collect_path):
    folder_path = os.path.abspath(os.path.dirname(collect_txt_path))
    for category in categories:
        target_path = os.path.join(base_collect_path, 'Category', category)
        Path(target_path).mkdir(parents=True, exist_ok=True)
        sym_link_path = os.path.join(target_path, os.path.basename(folder_path))
        if not os.path.exists(sym_link_path):
            os.symlink(folder_path, sym_link_path)
            print(f'Sym link created: {sym_link_path} -> {folder_path}')
        else:
            print(f'Sym link already exists: {sym_link_path}')

    target_path = os.path.join(base_collect_path, 'Date', date)
    Path(target_path).mkdir(parents=True, exist_ok=True)
    sym_link_path = os.path.join(target_path, os.path.basename(folder_path))
    if not os.path.exists(sym_link_path):
        os.symlink(folder_path, sym_link_path)
        print(f'Sym link created: {sym_link_path} -> {folder_path}')
    else:
        print(f'Sym link already exists: {sym_link_path}')

# Function to remove directories at the specified path
def remove_directories(collect_path):
    if not os.path.exists(collect_path):
        print(f'Directory not found: {collect_path}')
        return

    date_path = os.path.join(collect_path, 'Date')
    category_path = os.path.join(collect_path, 'Category')

    if os.path.exists(date_path):
        shutil.rmtree(date_path)
        print(f'Removed directory: {date_path}')
    else:
        print(f'Date directory not found: {date_path}')

    if os.path.exists(category_path):
        shutil.rmtree(category_path)
        print(f'Removed directory: {category_path}')
    else:
        print(f'Category directory not found: {category_path}')


# Main function
def main():
    # Parse command-line arguments
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Process collect.txt files and create sym links.')
    parser.add_argument('-r', '--remove', action='store_true', help='Remove directories that were created')
    parser.add_argument('-p', '--path', default='/Users/louismaddalena/Documents/', help='Path to search for collect.txt files')
    parser.add_argument('-c', '--collect', default='/Users/louismaddalena/Documents/__Collect__', help='Path to create the __Collect__ directory')




    args = parser.parse_args()

    # If the remove flag is set, remove the directories and return
    if args.remove:
        remove_directories(args.collect)
        return

    if not os.path.exists(args.collect):
        os.makedirs(args.collect)
        os.makedirs(os.path.join(args.collect, 'Date'))
        os.makedirs(os.path.join(args.collect, 'Category'))

    print(f'Searching for collect.txt files in {args.path}')
    for collect_txt_path in find_collect_txt_files(args.path):
        date, categories = parse_collect_txt(collect_txt_path)
        if date and categories:
            print(f'Processing {collect_txt_path}')
            create_sym_links(collect_txt_path, date, categories, args.collect)

    print(f'Sym links created in {args.collect}')

# Entry point for the script
if __name__ == '__main__':
    main()
