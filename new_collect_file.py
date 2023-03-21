import os
import datetime

def create_content_file(folder_path):
    content_file = os.path.join(folder_path, 'content.txt')
    if not os.path.exists(content_file):
        folder_creation_time = os.path.getctime(folder_path)
        creation_date = datetime.datetime.fromtimestamp(folder_creation_time).strftime("Date:%Y_%m_%d")
        with open(content_file, 'w') as file:
            file.write(creation_date)

def crawl_directory_tree(start_path):
    for root, dirs, files in os.walk(start_path):
        create_content_file(root)
        for dir in dirs:
            subdir_path = os.path.join(root, dir)
            create_content_file(subdir_path)

if __name__ == '__main__':
    start_path = input("Parent Director to Add Content.txt files to: ") 
    crawl_directory_tree(start_path)
