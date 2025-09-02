# Türkçe Plaka Tanıma Sistemi

Bu proje, YOLOv8 kullanarak Türkçe plaka tespiti ve tanıma işlemi yapan bir derin öğrenme modeli içerir. Model, özel olarak Türk plakaları için eğitilmiştir ve gerçek zamanlı olarak görüntü ve video akışlarında plaka tespiti yapabilir.

## 📋 İçerikler

- [Özellikler](#-özellikler)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Veri Seti](#-veri-seti)
- [Model Eğitimi](#-model-eğitimi)
- [Sonuçlar](#-sonuçlar)
- [Lisans](#-lisans)

## ✨ Özellikler

- YOLOv8 tabanlı yüksek doğruluklu plaka tespiti
- Türk plakaları için optimize edilmiş model
- Gerçek zamanlı çalışabilme özelliği
- Eğitim ve doğrulama için veri seti bölümleme desteği
- Ağırlık dosyaları ve eğitim metrikleri kaydı

## 🛠️ Kurulum

1. Gerekli kütüphaneleri yükleyin:

```bash
pip install -r requirements.txt
```

2. YOLOv8 modelini indirin veya kendi eğittiğiniz modeli kullanın.

## 🚀 Kullanım

### Eğitim İçin

```python
from ultralytics import YOLO

# Modeli yükle
model = YOLO("yolov8n.pt")  # Temel model

# Modeli eğit
results = model.train(
    data="plaka_data.yaml",
    epochs=60,
    imgsz=640,
    batch=16,
    name="plate_detection",
    project="runs"
)
```

### Test Etme

```python
from ultralytics import YOLO

# Eğitilmiş modeli yükle
model = YOLO("runs/plate_detection/weights/best.pt")

# Modeli değerlendir
metrics = model.val()
print(metrics)
```

## 📊 Veri Seti

Projede kullanılan veri seti aşağıdaki linkten indirilebilir:
[Turkish License Plate Dataset - Kaggle](https://www.kaggle.com/datasets/smaildurcan/turkish-license-plate-dataset/data)

Veri seti aşağıdaki yapıda düzenlenmiştir:

```
dataset/
├── images/
│   ├── train/
│   └── val/
└── label/
    ├── train/
    └── val/
```
Veri seti linki:https://www.kaggle.com/datasets/smaildurcan/turkish-license-plate-dataset/data
## 🎯 Model Eğitimi

Model eğitimi için aşağıdaki parametreler kullanılmıştır:

- Model: YOLOv8n
- Epoch: 60
- Görüntü Boyutu: 640x640
- Batch Boyutu: 16
- Optimizasyon: SGD
- Öğrenme Oranı: ---

## 📈 Sonuçlar

Eğitim sonrası model performans metrikleri `runs/plate_detection` dizininde kaydedilir. Bu metrikler:

- mAP (mean Average Precision)
- Precision
- Recall
- F1-Score

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına bakınız.

## 📞 İletişim

Herhangi bir sorunuz veya geri bildiriminiz için lütfen bir konu açın.

---

Bu proje YOLOv8 kullanılarak geliştirilmiştir. Daha fazla bilgi için [Ultralytics YOLOv8 Dokümantasyonu](https://docs.ultralytics.com/)'nu ziyaret edebilirsiniz.
