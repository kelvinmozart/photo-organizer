import time
from pathlib import Path

from MediaOrganizer import MediaOrganizer

if __name__ == "__main__":
    inicio = time.time()

    sources = [
        Path("C:/Example/Photos"),
        """Path("C:/Example/Photos 2")"""
    ]

    destination = Path("C:/Example/Photos organized")

    organizer = MediaOrganizer()

    for source in sources:
        organizer.organize_media(source, destination)

    print(f"Execution time: {time.time() - inicio:.2f}s")