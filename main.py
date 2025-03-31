import os
import shutil
import json
from datetime import datetime
import time
from PIL      import Image, ExifTags

def get_photo_creation_date(file_path):
    """ Gets the creation date of a photo from the EXIF metadata """

    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    if ExifTags.TAGS.get(tag) == "DateTimeOriginal":
                        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception as e:
        print(f"Could not retrieve EXIF for {file_path}: {e}")
        return None

    # Use the last modification date as fallback
    file_stat = os.stat(file_path)
    return datetime.fromtimestamp(file_stat.st_mtime)

def ensure_folder_exists(folder_path):
    """Ensures that a folder exists, creating it if necessary."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def organize_photos_by_creation_date(source_folder, destination_folder):
    """" Organizes photos into folders based on the photo creation date """

    ensure_folder_exists(destination_folder)

    error_folder = os.path.join(destination_folder, "error_files")
    video_folder = os.path.join(destination_folder, "Videos")

    ensure_folder_exists(error_folder)
    ensure_folder_exists(video_folder)

    copied_files_count = 0
    error_files_count  = 0
    exif_error_count   = 0
    error_files        = []
    exif_error_files   = []

    for root, _, files in os.walk(source_folder):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                # Check if the file is a video
                if file_extension in [".mp4", ".avi", ".mov", ".mkv"]:
                    shutil.move(file_path, os.path.join(video_folder, file))
                    print(f"Moved video: {file_path} -> {os.path.join(video_folder, file)}")
                    continue

                creation_date = get_photo_creation_date(file_path)
                if creation_date is None:
                    exif_error_count += 1
                    exif_error_files.append(file_path)
                    shutil.move(file_path, os.path.join(error_folder, file))
                    continue

                # Creates folder name in "YYYY-MM" format
                folder_name   = creation_date.strftime("%Y-%m")
                target_folder = os.path.join(destination_folder, folder_name)

                # Create the destination folder if necessary
                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)

                # Rename the file with a sequential counter
                file_extension = os.path.splitext(file)[1]
                new_file_name  = f"photo_{copied_files_count + 1:04d}{file_extension}"
                target_path    = os.path.join(target_folder, new_file_name)

                # Copy the file to the corresponding folder
                shutil.copy2(file_path, target_path)
                copied_files_count += 1
                print(f"Copied: {file_path} -> {target_path}")
            except Exception as e:
                error_files_count += 1
                error_files.append({"file": file_path, "error": str(e)})
                print(f"Error when copying {file_path}: {e}")

    # Generates the JSON file with errors
    error_report = {
        "exif_errors": exif_error_files,
        "copy_errors": error_files
    }
    try:
        with open("error_report.json", "w", encoding="utf-8") as json_file:
            json.dump(error_report, json_file, ensure_ascii=False, indent=4)
        print("error_report.json file generated successfully.")
    except Exception as e:
        print(f"Error generating JSON file: {e}")
    
    print(f"Total files copied: {copied_files_count}")
    print(f"Total files with error: {error_files_count}")
    print(f"Total files with EXIF ​​error: {exif_error_count}")

if __name__ == "__main__":
    source_folder      = "D:/backup notebook/Camera"            # Path of the folder with photos
    destination_folder = "C:/Teste"  # Organized folder path

    inicio = time.time()
    organize_photos_by_creation_date(source_folder, destination_folder)
    fim = time.time()
    print(f"Execution time: {fim - inicio:.2f} seconds")