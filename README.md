# Photo Organizer

This script was created with the help of GitHub Copilot to organize your photos into folders based on their creation date (month and year).

## Features

- Extracts the creation date from the EXIF metadata of photos.
- Supports both image files (e.g., .jpg, .jpeg, .png) and video files (e.g., .mp4).
- Organizes photos into folders named by the month and year of their creation date.
- Generates a JSON report of any errors encountered during the process.

## Usage

1. Set the `source_folder` variable to the path of the folder containing your photos.
2. Set the `destination_folder` variable to the path where you want the organized photos to be saved.
3. Run the script.

```python
if __name__ == "__main__":
    source_folder = "C:/Example/Photos"            # Path of the folder with photos
    destination_folder = "C:/Example/Photos organized"  # Organized folder path
