from config.config import Config
from screenshots.screenshots import Screenshots

from datetime import date

class Main:
    def __init__(self):
        today = date.today()

        config = Config()
        screenshots = Screenshots(config)
        images = screenshots.get_images_for_date(today)

if __name__=='__main__':
    Main()