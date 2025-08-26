import cv2
import detector
from ultralytics import YOLO
from detector import Detector
'''
import cv2
from ultralytics import YOLO

model = YOLO(r"C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\runs\\plate_detection\\weights\\best.pt")
webcam = cv2.VideoCapture(0)

while True:
    ret, frame = webcam.read()
    if not ret:
        break

    # Modelden sonuçları al
    results = model(frame, show=False, stream=True)

    # Tespit edilen tüm nesneleri işleme
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = model.names[int(box.cls[0])]
            confidence = box.conf[0]
            print("Güven skoru:", confidence)

            # Dikdörtgen ve etiket ekle
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{label}: {confidence:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Kareyi göster ve 'q' tuşuna basılınca çık
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    cv2.imshow("Plaka Tespiti", frame)

# Kaynakları serbest bırak
webcam.release()
cv2.destroyAllWindows()
'''


# PlateDetector sınıfının bir örneğini oluştur
# YOLO modelinizin yolunu buraya ekleyin
import detector
model_path = "C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\runs\\plate_detection\\weights\\best.pt"
plate_detector = Detector(model_path)

# Kamera kaynağını başlat
webcam = cv2.VideoCapture(0)
# Modeli ve Detector sınıfını sadece bir kez oluşturun
model_path = "C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\runs\\plate_detection\\weights\\best.pt"
plate_detector = Detector(model_path)

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
        break

# Kaynakları serbest bırak ve pencereleri kapat
webcam.release()
cv2.destroyAllWindows()