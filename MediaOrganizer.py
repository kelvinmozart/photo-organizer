import shutil
import json
from multiprocessing.spawn import prepare
from pathlib import Path
from datetime import datetime
from xmlrpc.client import DateTime

from PIL import Image, ExifTags


VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}


class MediaOrganizer:
    def __init__(self):
        pass

    def get_photo_date(file_path: Path) -> datetime:
        with Image.open(file_path) as img:
            photo_date = img._getexif() or {}

            for tag_id, value in photo_date.items():
                if ExifTags.TAGS.get(tag_id) != "DateTimeOriginal":
                    continue

                return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")

        raise ValueError(f"DateTimeOriginal not found in {file_path}")

    def prepare_directories(destination: Path) -> dict:
        destination.mkdir(parents=True, exist_ok=True)

        pdf_dir = destination / "pdfs"
        videos_dir = destination / "Videos"
        errors_dir = destination / "error_files"

        pdf_dir.mkdir(exist_ok=True)
        videos_dir.mkdir(exist_ok=True)
        errors_dir.mkdir(exist_ok=True)

        return {
            "pdfs": pdf_dir,
            "videos": videos_dir,
            "errors": errors_dir,
            "root": destination,
        }

    def print_summary(stats: dict):
        print(f"Total copied: {stats['copied']}")
        print(f"Videos copied: {stats['videos']}")
        print(f"PDFs copied: {stats['pdfs']}")
        print(f"Errors: {len(stats['errors'])}")

    def organize_media(source: Path, destination: Path):
        dirs = Path.prepare_directories(destination)

        stats = {
            "copied": 0,
            "videos": 0,
            "pdfs": 0,
            "errors": [],
        }

        for file in source.rglob("*"):
            if not file.is_file():
                continue

            try:
                if file.suffix.lower() in VIDEO_EXTENSIONS:
                    shutil.copy2(file, dirs.videos_dir / file.name)
                    stats["videos"] += 1
                    continue

                if file.suffix.lower() == ".pdf":
                    shutil.copy2(file, dirs.pdf_dir / file.name)
                    stats["pdfs"] += 1
                    continue

                date = Path.get_photo_date(file)
                folder = destination / date.strftime("%Y-%m")
                folder.mkdir(exist_ok=True)

                new_name = f"{date.strftime('%Y%m%d_%H%M%S')}{file.suffix.lower()}"
                shutil.copy2(file, folder / new_name)
                stats["copied"] += 1

                if stats["copied"] % 250 == 0:
                    print(f"{stats['copied']} processed files")

            except Exception as e:
                stats["errors"].append({"file": str(file), "error": str(e)})
                shutil.copy2(file, dirs.errors_dir / file.name)

        with open("error_report.json", "w", encoding="utf-8") as f:
            json.dump(
                {"copy_errors": stats["errors"]},
                f,
                indent=4,
                ensure_ascii=False,
            )

        Path.print_summary(stats)