import cv2
from ultralytics import YOLO
from src.plate_reader import PlateReader
from dotenv import load_dotenv
import os

load_dotenv()


class Detector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.plate_reader = PlateReader()

    def detect_plate(self, frame):
        results = self.model(frame, show=False)

        plates_found = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w, h = x2 - x1, y2 - y1

                plate_text = self.plate_reader.read_plate(frame, (x1, y1, w, h))
                if plate_text:
                    plates_found.append(plate_text)
                # Tespit edilen plakayı çiz
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, plate_text, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            return frame, plates_found