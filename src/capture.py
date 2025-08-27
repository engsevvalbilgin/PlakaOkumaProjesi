import cv2
from detector import Detector
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()
# PlateDetector sınıfının bir örneğini oluştur
# YOLO modelinizin yolunu buraya ekleyin
import detector

plate_detector = Detector(os.environ['model_path'])

# Kamera kaynağını başlat
webcam = cv2.VideoCapture(0)
# Modeli ve Detector sınıfını sadece bir kez oluşturun


while True:
    ret, frame = webcam.read()
    frame = cv2.resize(frame, (640, 480))
    if not ret:
        break

    # Detector sınıfını kullanarak kareyi işle ve sonuçları al
    processed_frame = plate_detector.detect_and_draw(frame)

    # İşlenmiş kareyi göster
    cv2.imshow("Plaka Tespiti", processed_frame)
    key =cv2.waitKey(1)
    # 'q' tuşuna basıldığında döngüden çık
    if  key == ord('q'):
        webcam.release()
        break

# Kaynakları serbest bırak ve pencereleri kapat

cv2.destroyAllWindows()

