import os
import sys
import re
import logging

def find_current_folders(google_drive_path):
    current_folders = []

    for root, dirs, _ in os.walk(google_drive_path):
        # Ignore folders containing "_Production_Resources"
        if "_Production_Resources" in root:
            continue

        for dir_name in dirs:
            if "CURRENT" in dir_name:
                current_folders.append(os.path.join(root, dir_name))

    return current_folders

def extract_showname_epnumber(current_folder_path):
    parent_dir = os.path.dirname(current_folder_path)
    parent_parts = parent_dir.split(os.sep)

    show_name = parent_parts[-3]
    ep_number = parent_parts[-2]

    return show_name, ep_number

def create_symlink(show_name, ep_number, current_folder_path, show_bids_path):
    symlink_name = f"{show_name}_{ep_number}_Bids"
    symlink_path = os.path.join(show_bids_path, symlink_name)

    os.symlink(current_folder_path, symlink_path)

def main(google_drive_path, show_bids_path):
    logging.basicConfig(filename='crawler.log', level=logging.INFO, format='%(asctime)s %(message)s')

    try:
        current_folders = find_current_folders(google_drive_path)

        for folder in current_folders:
            try:
                show_name, ep_number = extract_showname_epnumber(folder)
                create_symlink(show_name, ep_number, folder, show_bids_path)
            except Exception as e:
                logging.error(f"Error processing folder {folder}: {e}")
    except Exception as e:
        logging.error(f"Error during execution: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python google_drive_crawler.py /path/to/google_drive /path/to/show_bids")
        sys.exit(1)

    google_drive_path = sys.argv[1]
    show_bids_path = sys.argv[2]

    main(google_drive_path, show_bids_path)
