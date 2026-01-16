import shutil
import json
from pathlib import Path
from datetime import datetime
from PIL import Image, ExifTags


VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}


class MediaOrganizer:
    def __init__(self):
        pass

    def get_photo_date(file_path):
        try:
            with Image.open(file_path) as img:
                exif_data = img._getexif() or {}
                for tag, value in exif_data.items():
                    if ExifTags.TAGS.get(tag) == "DateTimeOriginal":
                        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
        except Exception:
            pass

        return datetime.fromtimestamp(file_path.stat().st_mtime)

    def organize_media(source: Path, destination: Path):
        destination.mkdir(parents=True, exist_ok=True)

        pdf_dir = destination / "pdfs"
        videos_dir = destination / "Videos"
        errors_dir = destination / "error_files"
        pdf_dir.mkdir(exist_ok=True)
        videos_dir.mkdir(exist_ok=True)
        errors_dir.mkdir(exist_ok=True)

        copied = 0
        videos_copied = 0
        pdfs_copied = 0
        exif_errors = []
        copy_errors = []

        for file in source.rglob("*"):
            if not file.is_file():
                continue

            try:
                if file.suffix.lower() in VIDEO_EXTENSIONS:
                    shutil.copy2(file, videos_dir / file.name)
                    videos_copied += 1
                    continue

                if file.suffix.lower() == ".pdf":
                    shutil.copy2(file, pdf_dir / file.name)
                    pdfs_copied += 1
                    continue

                date = Path.get_photo_date(file)
                folder = destination / date.strftime("%Y-%m")
                folder.mkdir(exist_ok=True)

                new_name = f"{date.strftime('%Y%m%d_%H%M%S')}{file.suffix.lower()}"
                shutil.copy2(file, folder / new_name)
                copied += 1

                if copied % 250 == 0:
                    print(f"{copied} arquivos processados")

            except Exception as e:
                copy_errors.append({"file": str(file), "error": str(e)})
                shutil.copy2(file, errors_dir / file.name)

        with open("error_report.json", "w", encoding="utf-8") as f:
            json.dump(
                {"copy_errors": copy_errors, "exif_errors": exif_errors},
                f,
                indent=4,
                ensure_ascii=False,
            )

        print(f"Total copied: {copied}")
        print(f"Videos copied: {videos_copied}")
        print(f"PDFs copied: {pdfs_copied}")
        print(f"Errors: {len(copy_errors)}")