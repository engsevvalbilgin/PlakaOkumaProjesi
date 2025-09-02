import os
import random
import shutil
from ultralytics import YOLO
import pandas as pd
import matplotlib.pyplot as plt

# Dataset klasörleri
'''
src_images = "C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\images"
src_labels = "C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\labels"
dst = "dataset"

os.makedirs(f"{dst}/images/train", exist_ok=True)
os.makedirs(f"{dst}/images/val", exist_ok=True)
os.makedirs(f"{dst}/labels/train", exist_ok=True)
os.makedirs(f"{dst}/labels/val", exist_ok=True)

files = os.listdir(src_images)
random.shuffle(files)
split = int(len(files) * 0.8)

for i, f in enumerate(files):
    label_file = f.replace(".jpg", ".txt")
    if i < split:
        shutil.copy(os.path.join(src_images, f), f"{dst}/images/train/")
        shutil.copy(os.path.join(src_labels, label_file), f"{dst}/labels/train/")
    else:
        shutil.copy(os.path.join(src_images, f), f"{dst}/images/val/")
        shutil.copy(os.path.join(src_labels, label_file), f"{dst}/labels/val/")

# Modeli eğit
model = YOLO("yolov8n.pt")  # küçük model, hızlı
model.train(
    data="C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\plaka_data.yaml",
    epochs=100,
    imgsz=640,
    batch=16,
    name="plate_detection",
    project="C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\runs"
)
'''
# Eğitilen modeli test et
'''
model = YOLO("C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\runs\\plate_detection\\weights\\best.pt")
data_path = "C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\plaka_data.yaml"
metrics = model.val(data=data_path, plots=True, save=True)
print(metrics)'''
# Veriyi oku
'''results_path = 'C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\runs\\plate_detection\\results.csv'
 # Kendi dosya yolunu yazmalısın
results = pd.read_csv(results_path)

# Grafik çizimi
plt.figure(figsize=(10, 6))
plt.plot(results['epoch'], results['train/box_loss'], label='Train Kaybı')
plt.plot(results['epoch'], results['val/box_loss'], label='Validation Kaybı')

plt.title('Eğitim ve Doğrulama Kaybı Grafiği')
plt.xlabel('Epoch')
plt.ylabel('Kayıp (Loss)')
plt.legend()
plt.grid(True)
plt.show()

# Grafik çizimi
plt.figure(figsize=(10, 6))
plt.plot(results['epoch'], results['metrics/mAP50(B)'], label='Eğitim mAP@0.50')
plt.plot(results['epoch'], results['metrics/mAP50-95(B)'], label='Doğrulama mAP@0.50-0.95')


plt.title('Eğitim ve Doğrulama mAP Grafiği')
plt.xlabel('Epoch')
plt.ylabel('mAP Değeri')
plt.legend()
plt.grid(True)
plt.show()

'''