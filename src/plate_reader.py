import cv2
import easyocr
import re
import time

# EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False)

class PlateReader:
    def __init__(self, max_wait=5):
        self.max_wait = max_wait  # Maks bekleme süresi saniye
        self.reader = reader

    def read_plate(self, img, box):
        x, y, w, h = box
        plate_roi = img[y:y + h, x:x + w]

        gray = cv2.cvtColor(plate_roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3,3), 0)

        start_time = time.time()
        text = ""
        result = self.reader.readtext(gray, detail=0)
        if result:
            text = ''.join(result).upper().replace(" ", "")
            text = text.replace("O","0").replace("I","1")
            if text.startswith("TR"):
                text = text[2:]
            match = re.search(r"(\d{2}[A-Z]{1,3}\d{2,4})", text)
            if match:
                return match.group(1)
            time.sleep(0.05)  # Kısa bekleme, CPU çok yorulmasın

        print(f"{text}")
        return ""



import cv2
import Levenshtein

# PlateReader sınıfın önceden tanımlı olmalı
plate_reader = PlateReader()

test_images = [
    cv2.imread('C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\dataset\\images\\train\\1.jpg'),
    cv2.imread('C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\dataset\\images\\train\\5.jpg'),
    cv2.imread('C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\dataset\\images\\train\\11.jpg'),
    cv2.imread('C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\dataset\\images\\train\\19.jpg')
]

test_boxes_norm = [
    (0, 0.515392, 0.458412, 0.214023, 0.025641),
    (0, 0.570024, 0.503440, 0.187842, 0.023139),
    (0, 0.537195, 0.477054, 0.230476, 0.02920),(0, 0.486311, 0.544325, 0.294421, 0.033302)
]

true_plates = ["79DR707", "66AP857", "06TIH40","66AAP914"]
predicted_plates = []

for img, box in zip(test_images, test_boxes_norm):
    h_img, w_img, _ = img.shape
    # YOLO format: x_center, y_center, w, h
    _, x_center_norm, y_center_norm, w_norm, h_norm = box

    # Piksele çevir
    x_center = x_center_norm * w_img
    y_center = y_center_norm * h_img
    w_box = w_norm * w_img
    h_box = h_norm * h_img

    # Sol üst ve sağ alt köşe
    x1 = int(x_center - w_box/2)
    y1 = int(y_center - h_box/2)
    x2 = int(x_center + w_box/2)
    y2 = int(y_center + h_box/2)

    # Piksel box
    box_pixel = (x1, y1, x2-x1, y2-y1)  # read_plate fonksiyonuna uyumlu

    # OCR
    plate = plate_reader.read_plate(img, box_pixel)
    predicted_plates.append(plate)

# Doğruluk ölçümü
total_score = 0
for pred, true in zip(predicted_plates, true_plates):
    score = 1 - (Levenshtein.distance(pred, true) / max(len(pred), len(true)))
    total_score += score

average_score = total_score / len(true_plates)
print(f"Ortalama karakter doğruluğu: {average_score*100:.2f}%")
