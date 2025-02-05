import os
import shutil
import json
from datetime import datetime
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
        print(f"Não foi possível obter EXIF para {file_path}: {e}")
        return None

    # Use the last modification date as fallback
    file_stat = os.stat(file_path)
    return datetime.fromtimestamp(file_stat.st_mtime)

def organize_photos_by_creation_date(source_folder, destination_folder):
    """" Organizes photos into folders based on the photo creation date """

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    copied_files_count = 0
    error_files_count  = 0
    exif_error_count   = 0
    error_files        = []
    exif_error_files   = []

    for root, _, files in os.walk(source_folder):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                creation_date = get_photo_creation_date(file_path)
                if creation_date is None:
                    exif_error_count += 1
                    exif_error_files.append(file_path)
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
    source_folder      = "C:/Example/Photos"            # Path of the folder with photos
    destination_folder = "C:/Example/Photos organized"  # Organized folder path

    organize_photos_by_creation_date(source_folder, destination_folder)