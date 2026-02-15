import pytesseract
import re

from PIL import Image, ImageOps

class OCRProcessor:
    def __init__(self, lang="jpn"):
        self.lang = lang

    def extract_text(self, image:Image) -> str:
        try:
            img = self.apply_grayscale(image)
            return self.format_text(
                pytesseract.image_to_string(
                    img,
                    lang=self.lang,
                    config="--psm 6",
                )
            )
        except pytesseract.TesseractNotFoundError:
            return "[TESSERACT NOT INSTALLED]"
    
    def apply_grayscale(self, image) -> Image:
        return ImageOps.grayscale(image)

    def format_text(self, text) -> str:
        return re.sub(r"\s+", "", text)