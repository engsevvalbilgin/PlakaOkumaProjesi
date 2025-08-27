import cv2
import pytesseract
import re
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from dotenv import load_dotenv
# .env dosyasını yükle
load_dotenv()
class PlateReader:

    def __init__(self, img, box):
        self.image = img
        self.box = box
    def read_plate(self):
        x, y, w, h = self.box
        plate=self.image[y:y+h,x:x+w]

        gray=cv2.cvtColor(plate,cv2.COLOR_BGR2GRAY)
        gray=cv2.bilateralFilter(gray,11,17,17)
        thresh = cv2.adaptiveThreshold(gray, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)

        config="--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ŞÇĞÜÖİ"
        text = pytesseract.image_to_string(thresh, config=config, lang="eng")
        match = re.search(r"(\d{2}[A-ZÇĞİÖŞÜ]{1,3}\d{2,4})", text)
        if match:
            return match.group(1)
        return ""



