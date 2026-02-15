import tomllib
from pathlib import Path

from generator.generator import Generator as g

class Config:
    def __init__(self):
        self.read_config_file()
    
    def read_config_file(self):
        try:
            with open("config.toml", "rb") as f:
                config = tomllib.load(f)
                self.screnshot_folder_names = config.get('screenshot_folders', [])
                self.screnshot_folders = [Path(folder_name) for folder_name in self.screnshot_folder_names]
                self.anki_img_folder = config.get('anki_img_folder', '')

        except FileNotFoundError:
            print("Config file not found. Generating...")
            g.generate_config_file()
            self.read_config_file()
