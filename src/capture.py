import cv2
import os
from dotenv import load_dotenv
from src.detector import Detector
from src.plate_database import PlateDatabase

load_dotenv()


def start_capture():
    """Kameradan görüntü yakalar, plaka tespit eder ve DB'ye kaydeder."""
    db_path = os.path.join(os.environ['data_path'], 'vehicles.db')
    plate_db = PlateDatabase(db_path)

    model_path = os.environ['model_path']
    plate_detector = Detector(model_path)

    webcam = cv2.VideoCapture(0)

    while True:
        ret, frame = webcam.read()
        if not ret:
            break

        processed_frame, plates = plate_detector.detect_plate(frame)

        if plates:
            for plate in plates:
                plate_db.record_plate_event(plate)

        cv2.imshow("Plaka Tespiti", processed_frame)

        key = cv2.waitKey(1)
        if key == ord('q'):  # q ile çıkış
            break

    webcam.release()
    cv2.destroyAllWindows()
