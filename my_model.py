import os
import random
import shutil
from ultralytics import YOLO


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

model = YOLO(r"C:\Users\hp\PycharmProjects\PlakaOkumaProjesi\runs\plate_detection\weights\best.pt")

metrics = model.val()
print(metrics)
