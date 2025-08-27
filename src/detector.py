import os

import cv2
from ultralytics import YOLO
import plate_reader
from src.plate_reader import PlateReader
import plate_database
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()
class Detector:
    def __init__(self, model_path):
        """
        Plaka tespit modelini yükler.
        """
        self.model = YOLO(model_path)

    def detect_and_draw(self, frame):
        """
        Verilen kare üzerinde plaka tespiti yapar ve sonuçları kareye çizer.
        """
        # Modelden sonuçları al
        results = self.model(frame, show=False, stream=True)

        # Tespit edilen tüm nesneleri işleme
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w = x2 - x1
                h = y2 - y1

                # PlateReader (x,y,w,h) formatı bekliyor
                plate_reader_obj = PlateReader(frame, (x1, y1, w, h))
                plate_text = plate_reader_obj.read_plate()
                if plate_text:
                    plate_database.saveDatabase(plate_text)
                    return 0
                else:
                    print("No plate detected")
                label = self.model.names[int(box.cls[0])]
                confidence = box.conf[0]

                # Dikdörtgen ve etiket ekle
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label}: {confidence:.2f}:{plate_text}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return frame

'''image_path = "C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\images\\6.jpg"
frame = cv2.imread(image_path)

detector = Detector(os.environ['model_path'])
detector.detect_and_draw(frame)'''