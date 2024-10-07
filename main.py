import os
import re
import shutil
from PIL import Image, ImageOps
import glob
import zipfile
import subprocess

testing = False
test_folder_path = "C:\\Users\\nickm\\Downloads\\jul312"


def convert_heic_to_jpg(folder_path):
    if not os.path.isdir(folder_path):
        print("The specified folder does not exist.")
        return

    if not folder_path.endswith('\\'):
        folder_path += '\\'

    cmd = f'for %i in ("{folder_path}*.heic") do heif-convert "%i" && del "%i"'

    try:
        subprocess.run(cmd, shell=True, check=True)
        print("Conversion and deletion completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")


def create_unique_name(base_name):
    counter = 0
    unique_name = base_name
    while os.path.exists(unique_name):
        unique_name = f"{base_name}({counter})"
        counter += 1
    return unique_name


def handle_most_recent_zip():
    downloads_folder = "C:\\Users\\nickm\\Downloads"

    # Use glob to get a list of zip files in the directory
    zip_files = glob.glob(os.path.join(downloads_folder, '*.zip'))

    if not zip_files:
        print("No ZIP files found in the Downloads folder.")
        return None

    most_recent_zip = max(zip_files, key=os.path.getmtime)
    print(f"Most recent ZIP file: {most_recent_zip}")

    extract_to = create_unique_name(
        os.path.join(downloads_folder, os.path.splitext(os.path.basename(most_recent_zip))[0]))
    os.makedirs(extract_to, exist_ok=True)

    # Unzip the file
    with zipfile.ZipFile(most_recent_zip, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(most_recent_zip)
    print(f"ZIP file extracted to: {extract_to}")

    return extract_to


# un-rotates photos that have been rotated by an EXIF tag
def rotate_photos(fpath):
    f = os.listdir(fpath)

    for file_name in f:
        file_path = os.path.join(fpath, file_name)

        if file_name.lower().endswith('.mp4'):
            os.remove(file_path)
            print(f'Deleted {file_name}')
        try:
            img = ImageOps.exif_transpose(Image.open(file_path))
            if img.width == 1800:
                # Rotate 90 degrees right
                img = img.transpose(Image.ROTATE_270)
                img.save(file_path)
                print(f"Rotated {file_name} 90 degrees right.")
        except Exception as e:
            print(f"Error processing {file_name}: {e}")


# converts string in "HHMMSS" format to int seconds
def hhmmss_to_seconds(hhmmss):
    hours = int(hhmmss[:2])
    minutes = int(hhmmss[2:4])
    seconds = int(hhmmss[4:])
    return hours * 3600 + minutes * 60 + seconds


def organize_photos_into_folders(folder_path):
    files = os.listdir(folder_path)
    extract_HHMMSS_regex = '_|\\(\\d\\)|\\.(?:jpg|png)'
    files.sort(key=lambda x: hhmmss_to_seconds(re.split(extract_HHMMSS_regex, x)[1]))

    # Create initial folder with label of first image's HHMMSS number
    initial_time = hhmmss_to_seconds(re.split(extract_HHMMSS_regex, files[0])[1])
    initial_folder_path = os.path.join(folder_path, str(initial_time))
    os.makedirs(initial_folder_path, exist_ok=True)

    # Loop through files and organize them into folders
    current_folder_path = initial_folder_path
    for i in range(len(files) - 1):
        current_file = files[i]
        next_file = files[i + 1]

        current_time = hhmmss_to_seconds(re.split(extract_HHMMSS_regex, current_file)[1])
        next_time = hhmmss_to_seconds(re.split(extract_HHMMSS_regex, next_file)[1])
        difference = next_time - current_time

        src = os.path.join(folder_path, current_file)
        dst = os.path.join(current_folder_path, current_file)
        shutil.move(src, dst)

        if difference > 150:
            # Create a new folder with label of next image's HHMMSS number
            next_folder_path = os.path.join(folder_path, str(next_time))
            os.makedirs(next_folder_path, exist_ok=True)
            current_folder_path = next_folder_path
    last_file = files[-1]
    src = os.path.join(folder_path, last_file)
    dst = os.path.join(current_folder_path, last_file)
    shutil.move(src, dst)
    print("Files organized into folders based on time differences.")


if testing:
    folder_path = test_folder_path
else:
    folder_path = handle_most_recent_zip()

convert_heic_to_jpg(folder_path)
rotate_photos(folder_path)
organize_photos_into_folders(folder_path)