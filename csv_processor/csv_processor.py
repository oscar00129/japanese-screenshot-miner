from datetime import date
from pathlib import Path
import csv

class CSVProcessor:
    def __init__(self, today:date):
        self.today = today

    def append_to_csv(self, output_folder: Path, text: str, image_name: str):
        csv_path = output_folder / f"{self.today}.csv"

        with open(csv_path, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerow([
                f'{text}\n<img src="{image_name}">',
                "",
                ""
            ])