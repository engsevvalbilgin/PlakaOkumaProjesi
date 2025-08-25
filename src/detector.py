import cv2
from ultralytics import YOLO

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
                label = self.model.names[int(box.cls[0])]
                confidence = box.conf[0]

                # Dikdörtgen ve etiket ekle
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label}: {confidence:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return frame

# Bu dosyanın doğrudan çalıştırılmasını önlemek için aşağıdaki kontrolü ekleyebilirsiniz
