from config.config import Config
from datetime import datetime
from pathlib import Path

from datetime import date

class Screenshots:
    def __init__(self, config:Config):
        self.config = config
    
    def get_images_for_date(self, today:date) -> list[Path]:
        image_paths = []
        for folder in self.config.screnshot_folders:
            for file in folder.rglob("*.jpg"):
                if "thumbnails" in file.parts:
                    continue

                if "cache" in file.parts:
                    continue

                file_date = datetime.fromtimestamp(
                    file.stat().st_mtime
                ).date()

                if file_date == today:
                    image_paths.append(file)
        return image_paths