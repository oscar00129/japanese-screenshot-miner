from config.config import Config
from screenshots.screenshots import Screenshots
from interface.crop_image import ImageSelector

from datetime import date

class Main:
    def __init__(self):
        today = date.today()

        config = Config()
        screenshots = Screenshots(config)
        images = screenshots.get_images_for_date(today)

        selector = ImageSelector(images, today)
        selector.run()

if __name__=='__main__':
    Main()