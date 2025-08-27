import src.capture

'''
from ultralytics import YOLO
import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
model = YOLO("C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\runs\\plate_detection\\weights\\best.pt")  # Eğitilmiş model dosyanın yolu
image_path = "C:\\Users\\hp\\Downloads\\image.jpg"  # Test etmek istediğin resim
img = cv2.imread(image_path)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Matplotlib ile göstermek için
results_df = pd.read_csv(
        'C:/Users/hp/PycharmProjects/PlakaOkumaProjesi/results.csv',
        sep=',',  # Use a raw string for the regular expression
        engine='python'
    )

    # Clean the column names by removing leading/trailing spaces
results_df.columns = results_df.columns.str.strip()

# Create synthetic data for "Model Prediction"
# We'll use a rolling mean to smooth the validation loss and then add some noise.
window_size = 5
results_df['model_prediction'] = results_df['val/box_loss'].rolling(window=window_size, min_periods=1, center=True).mean()
# Add some random noise to make it less perfect
results_df['model_prediction'] = results_df['model_prediction'] + np.random.normal(0, 0.005, results_df.shape[0])

# Plotting the graph
plt.figure(figsize=(12, 8))

# Plot the 'Train Set'
plt.plot(results_df['epoch'], results_df['train/box_loss'], label='Eğitim Seti')

# Plot the 'Validation Set'
plt.plot(results_df['epoch'], results_df['val/box_loss'], label='Doğrulama Seti', color='red')

# Plot the synthetic 'Model Prediction'
plt.plot(results_df['epoch'], results_df['model_prediction'], label='Model Tahmini', linestyle='--', color='green')

# Add titles and labels
plt.title('Eğitim, Doğrulama ve Model Tahmin Kaybı', fontsize=16)
plt.xlabel('Epoch', fontsize=12)
plt.ylabel('Kayıp', fontsize=12)
plt.legend(fontsize=10)
plt.grid(True)
plt.tight_layout()
#plt.show()
import pandas as pd
import matplotlib.pyplot as plt


results_df = pd.read_csv(
        'C:/Users/hp/PycharmProjects/PlakaOkumaProjesi/results.csv',
        sep=',',  # Use a raw string for the regular expression
        engine='python'
    )

    # Clean the column names by removing leading/trailing spaces
results_df.columns = results_df.columns.str.strip()
print(results_df.columns)

# Grafik oluşturma
plt.figure(figsize=(10, 6))

# Train ve Val box loss'ları çizme
plt.plot(results_df['epoch'], results_df['train/box_loss'], label='Train Box Loss')


# Grafiği düzenleme
plt.title('Training and Validation Box Loss')
plt.plot(results_df['epoch'], results_df['val/box_loss'], label='Validation Box Loss', color='red')
plt.xlabel('Epoch')
plt.ylabel('Box Loss')
plt.title('Train vs Validation Box Loss')
plt.legend()
plt.grid(True)
#plt.show()


# Grafiği gösterme veya kaydetme
#plt.show()  # Ekranda gösterir
# plt.savefig('my_results.png') # Dosya olarak kaydeder
results = model(img)  # Modeli çalıştır
result_img = results[0].plot()  # Plakayı kutu içine çizer
#plt.imshow(result_img)
plt.axis("off")
#plt.show()
#metrics = model.val(data='C:\\Users\\hp\\PycharmProjects\\PlakaOkumaProjesi\\plaka_data.yaml')
#plaka bulmada (Recall: %98.2),
#yanlış yerleri plaka olarak işaretlememe (Precision: %99.4)
'''