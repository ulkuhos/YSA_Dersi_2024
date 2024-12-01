# -*- coding: utf-8 -*-
"""Ulku_MLP_Models_Midterm_Project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1hpAE2mNdWdPFp2qoAQ5msmHy9VskZvZ0
"""

# Veri işleme
import pandas as pd
import numpy as np

# Model oluşturma ve değerlendirme
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# TensorFlow ve Keras
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input

# Gerekli PyTorch modüllerini ekleme
from torchvision import datasets, transforms

# Veri setini indirip yükleme (eğitim ve test setleri)
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))  # Veriyi normalize et
])

# Eğitim ve test setleri
train_data = datasets.GTSRB(root='./data', split='train', transform=transform, download=True)
test_data = datasets.GTSRB(root='./data', split='test', transform=transform, download=True)

# Veri seti boyutlarını kontrol et
print(f"Eğitim verisi boyutu: {len(train_data)}")
print(f"Test verisi boyutu: {len(test_data)}")

# Gerekli kütüphaneler
from torchvision.transforms import functional as F

# Eğitim setindeki görüntüleri numpy formatına dönüştürme ve yeniden boyutlandırma
X_train = np.array([F.resize(img[0], (32, 32)).numpy().flatten() for img in train_data])
y_train = np.array([img[1] for img in train_data])

# Test setindeki görüntüleri numpy formatına dönüştürme ve yeniden boyutlandırma
X_test = np.array([F.resize(img[0], (32, 32)).numpy().flatten() for img in test_data])
y_test = np.array([img[1] for img in test_data])

# Veriyi ölçeklendirme
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("Veri başarıyla ölçeklendirildi.")
print(f"Ölçeklendirilmiş eğitim verisi boyutu: {X_train_scaled.shape}")
print(f"Ölçeklendirilmiş test verisi boyutu: {X_test_scaled.shape}")

# Eğitim veri setinden birkaç örneği görselleştirme
import matplotlib.pyplot as plt

# Görüntülerin ilk 10 tanesini görselleştirme
# Görsellerin normalize edilmiş değerlerini [0, 1] aralığına çekerek düzeltiyoruz
fig, axes = plt.subplots(1, 10, figsize=(15, 5))  # 1 satır, 5 sütun
for i, ax in enumerate(axes):
   # Görüntüyü yeniden boyutlandır ve normalize etmeden göster
    img = train_data[i][0].permute(1, 2, 0).numpy()  # Tensörü numpy array'e çevir. # Görüntüyü (H, W, C) formatına çevir
    img = (img - img.min()) / (img.max() - img.min())  # Görseli 0-1 aralığına döndür
    ax.imshow(img)  # Görüntüyü göster
    ax.set_title(f"Label: {train_data[i][1]}")  # Etiket ekle
    ax.axis('off')  # Eksenleri kapat
plt.show()

# Etiketlerin dağılımını kontrol etme
import numpy as np
labels = [train_data[i][1] for i in range(len(train_data))]
unique, counts = np.unique(labels, return_counts=True)

print("Sınıf dağılımı:")
for u, c in zip(unique, counts):
    print(f"Label {u}: {c} örnek")

# İlk 10 görüntüyü etiketlerle görselleştirme
fig, axes = plt.subplots(1, 10, figsize=(20, 5))
for i, ax in enumerate(axes):
    img = train_data[i][0].permute(1, 2, 0).numpy()
    img = (img - img.min()) / (img.max() - img.min())
    ax.imshow(img)
    ax.set_title(f"Label: {train_data[i][1]}")
    ax.axis('off')
plt.show()

# Farklı 10 sınıftan birer örnek seçip görselleştirme
fig, axes = plt.subplots(1, 10, figsize=(20, 5))
unique_labels = set()
i = 0

for img, label in train_data:
    if label not in unique_labels:
        img = img.permute(1, 2, 0).numpy()
        img = (img - img.min()) / (img.max() - img.min())
        axes[i].imshow(img)
        axes[i].set_title(f"Label: {label}")
        axes[i].axis('off')
        unique_labels.add(label)
        i += 1
    if i == 10:  # 10 farklı sınıfı görselleştir
        break
plt.show()

"""# 1- MLP MODELLERİ

Gerekli kütüphaneler ve kurumları

## MLP MODEL 1 : Model Eğitimi
"""

from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report

mlp_model1 = MLPClassifier(
    max_iter=100,  # 100 epoch
    batch_size=16,  # Her iterasyonda 16 örnek
    random_state=42
)
mlp_model1.fit(X_train_scaled, y_train)

y_pred_model1 = mlp_model1.predict(X_test_scaled)
print("Model 1 - Performans (Düşük Epoch ve Küçük Batch Size)")
print(classification_report(y_test, y_pred_model1))

"""## MLP MODEL 1 : RandomSearchCV ile Hiperparametre Optimizasyonu"""

from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import RandomizedSearchCV
import numpy as np

# Hiperparametre aralığını tanımladık
param_dist_model1 = {
    'hidden_layer_sizes': [(50,), (100,), (50, 50)],  # Daha az kombinasyon
    'activation': ['relu', 'tanh'],  # Aktivasyon fonksiyonları
    'solver': ['adam'],  # Daha hızlı optimizasyon algoritması
    'alpha': [0.0001, 0.001],  # L2 regülarizasyon
    'batch_size': [32],  # Sabit batch size
    'learning_rate_init': [0.001, 0.005],  # Öğrenme oranı
    'max_iter': [100]  # Düşük epoch sayısı
}

# RandomizedSearchCV tanımlama
random_search_model1 = RandomizedSearchCV(
    MLPClassifier(random_state=42, early_stopping=True),  # Early stopping ile eğitim süresini kısaltma
    param_distributions=param_dist_model1,
    n_iter=10,  # Rastgele 10 kombinasyon dene
    cv=3,  # 3 katlı çapraz doğrulama
    scoring='accuracy',  # Doğruluk metriği
    n_jobs=-1,  # Tüm işlemcileri kullan
    verbose=2  # İşlem ilerlemesini göster
)

# Modeli eğitme
random_search_model1.fit(X_train_scaled, y_train)

# En iyi hiperparametreleri ve sonuçları yazdırma
print("Model 1 - En iyi hiperparametreler:", random_search_model1.best_params_)
print("Model 1 - En iyi doğruluk skoru (cv):", random_search_model1.best_score_)

# En iyi modeli test seti üzerinde değerlendirme
best_model1 = random_search_model1.best_estimator_
y_pred_model1 = best_model1.predict(X_test_scaled)
print("Model 1 - Performans (Hiperparametre Optimizasyonu ile)")
print(classification_report(y_test, y_pred_model1))

"""**Sonuç olarak:** Model 1, hiperparametre optimizasyonuyla %81 doğruluk elde etmiştir. Sonuçta macro metriklerde precision: %78, recall: %75, f1-score: %76 değerlerine ulaşıldığını görmekteyiz. Büyük sınıflarda yüksek performans, küçük sınıflarda ise ortalama düzeyde bir başarı sağlamıştır diyebiliriz. Genel olarak model dengeli bir performans göstermiştir.

## MLP MODEL 1 :  Kayıp değerleri grafiği
"""

import matplotlib.pyplot as plt

# Model 1'in kayıp eğrisi (loss_curve_) kontrol edilerek görselleştirilmesi
if hasattr(best_model1, "loss_curve_"):
    plt.figure(figsize=(10, 6))
    plt.plot(best_model1.loss_curve_, label='Eğitim Kaybı (Loss)', marker='o')
    plt.title('Model 1 - Eğitim Sürecinde Kayıp Grafiği')
    plt.xlabel('Epoch')
    plt.ylabel('Kayıp (Loss)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()
else:
    print("Model 1'de loss_curve_ özelliği bulunamadı.")

"""**Grafik bize,** Model 1'in eğitim sürecinde kaybın hızlı bir şekilde azaldığını ve yaklaşık olarak 15. epoch'tan sonra daha stabil hale geldiğini gösteriyor. Bu, modelin başarılı bir şekilde öğrendiğini ve genelleme yeteneğinin iyi olduğunu gösteriyor.

## MLP MODEL 1 : Karışıklık Matrisi:
"""

from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Model 1 için karışıklık matrisi oluşturma
cm_model1 = confusion_matrix(y_test, y_pred_model1)

# Karışıklık matrisini görselleştirme
plt.figure(figsize=(12, 10))
sns.heatmap(cm_model1, annot=True, fmt='d', cmap='Blues', cbar=True)
plt.title('Model 1 - Karışıklık Matrisi')
plt.xlabel('Tahmin Edilen Etiket')
plt.ylabel('Gerçek Etiket')
plt.show()

"""# NOT: Model 1'in İlk Hali ve RandomizedSearchCV ile Optimize Edilmiş Hali Arasındaki Fark:

RandomizedSearchCV ile optimize edilen model 1, hiperparametre optimizasyonu sayesinde genel doğrulukta iyileşme sağlamış ve sınıf bazında recall ve F1-Score değerlerinde tutarlılık göstermiştir. Bu, optimize edilen modelin gerçek dünya verileri üzerinde daha genel geçer bir performansa sahip olabileceğini bizlere göstermektedir.

Optimize edilmiş modelde, %5 doğruluk artışı ve daha tutarlı sınıf performansı ile daha başarılı bir sonuç verdiğini gözlemliyoruz.

## MLP MODEL 2 : Model Eğitimi
"""

mlp_model2 = MLPClassifier(
    hidden_layer_sizes=(30, 30),  # İki katman, her biri 30 nöron
    max_iter=150,  # 150 epoch
    batch_size=32,  # Her iterasyonda 32 örnek
    learning_rate_init=0.01,  # Öğrenme oranı 0.01
    random_state=42
)
mlp_model2.fit(X_train_scaled, y_train)

y_pred_model2 = mlp_model2.predict(X_test_scaled)
print("Model 2 - Performans (Düşük Oranlarla)")
print(classification_report(y_test, y_pred_model2))

"""## MLP MODEL 2 : RandomizedSearchCV ile Hiperparametre Optimizasyonu"""

from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import RandomizedSearchCV
import numpy as np

# Hiperparametre aralıkları
param_dist_model2 = {
    'hidden_layer_sizes': [(30, 30), (50, 30), (30, 30, 30)],  # Farklı katman yapılarını test etme
    'activation': ['relu', 'tanh'],  # Aktivasyon fonksiyonları
    'solver': ['adam'],  # Daha hızlı optimizasyon algoritması
    'alpha': [0.0001, 0.001, 0.01],  # L2 regülarizasyon parametresi
    'batch_size': [16, 32],  # Mini-batch boyutları
    'learning_rate_init': [0.001, 0.01, 0.005],  # Öğrenme oranları
    'max_iter': [150]  # Epoch sayısı sabit tutuldu
}

# RandomizedSearchCV tanımlama
random_search_model2 = RandomizedSearchCV(
    MLPClassifier(random_state=42, early_stopping=True),  # Early stopping ile fazla iterasyonları engelleme
    param_distributions=param_dist_model2,
    n_iter=10,  # Rastgele 10 farklı kombinasyon deneme
    cv=3,  # 3 katlı çapraz doğrulama
    scoring='accuracy',  # Doğruluk metriği
    n_jobs=-1,  # Tüm işlemcileri kullan
    verbose=2
)

# Modeli eğitme
random_search_model2.fit(X_train_scaled, y_train)

# En iyi hiperparametreleri ve sonuçları yazdırma
print("Model 2 - En iyi hiperparametreler:", random_search_model2.best_params_)
print("Model 2 - En iyi doğruluk skoru (cv):", random_search_model2.best_score_)

# En iyi modeli test seti üzerinde değerlendirme
best_model2 = random_search_model2.best_estimator_
y_pred_model2 = best_model2.predict(X_test_scaled)
print("Model 2 - Performans (Hiperparametre Optimizasyonu ile)")
print(classification_report(y_test, y_pred_model2))

"""**Sonuç olarak,** Model 2, %78 doğruluk ile orta düzey bir başarı sağlamıştır. Macro metriklerde precision: %75, recall: %70, f1-score: %71 elde edilmiştir. Daha derin yapı sayesinde genel doğruluk seviyesi artmış ancak küçük sınıflarda performans değişimleri gözlemlemekteyiz.

# NOT: Model 2'nin İlk Hali ve RandomizedSearchCV ile Optimize Edilmiş Hali Arasındaki Fark:

Doğruluk ve optimzasyon metriklerinde belirgin bir artış sağlanmıştır:
İlk hali neredeyse işlevsel değilken (%34 doğruluk), optimize edilmiş hali bize tutarlı sonuçlar vermiştir (%78 doğruluk).
Precision, recall ve F1-Score değerleri tüm sınıflar genelinde önemli ölçüde iyileşmiştir.
RandomizedSearchCV, hiperparametre optimizasyonu ile modelin öğrenme kapasitesini artırmış, daha etkili bir eğitim sağlamış olduğunu görmekteyiz. Optimize edilen modelin, genel olarak çok daha başarılı olduğu görülmektedir.

## MLP MODEL 2 : Kayıp Değerleri Grafiği
"""

import matplotlib.pyplot as plt

# Model 2'nin eğitim sürecindeki kayıp değerleri kontrol et
if hasattr(best_model2, "loss_curve_"):
    plt.figure(figsize=(10, 6))
    plt.plot(best_model2.loss_curve_, label='Eğitim Kaybı (Loss)', color='blue')
    plt.title('Model 2 - Eğitim Sürecindeki Kayıp Değerleri')
    plt.xlabel('Epoch')
    plt.ylabel('Kayıp (Loss)')
    plt.legend()
    plt.grid()
    plt.show()
else:
    print("Model 2'de 'loss_curve_' özelliği bulunamadı.")

"""**Grafik bize,** Model 2'nin eğitim sürecindeki kayıp değerlerinin (loss) epoch'lara göre hızlı bir şekilde azaldığını göstermektedir. İlk birkaç epoch'ta kayıp değeri hızla düşerek modelin öğrenmeye başladığını gözlemliyoruz. 15. epoch'tan itibaren kayıp sabitlenmeye başlıyor ve öğrenme süreci daha stabil hale geliyor. Model, hızlı bir optimizasyon süreci geçirmiş ve genel olarak baktığımız iyi bir dengeye ulaşmış olduğunu gözlemliyoruz.

## MLP MODEL 2 : Karışıklık Matrisi:
"""

from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Model 2'nin tahmin sonuçları (y_pred_model2) ve gerçek etiketler (y_test)
cm_model2 = confusion_matrix(y_test, y_pred_model2)

# Karışıklık matrisinin görselleştirilmesi
plt.figure(figsize=(10, 8))
sns.heatmap(cm_model2, annot=True, fmt='d', cmap='Blues', xticklabels=np.unique(y_test), yticklabels=np.unique(y_test))
plt.title('Model 2 - Karışıklık Matrisi')
plt.xlabel('Tahmin Edilen Etiket')
plt.ylabel('Gerçek Etiket')
plt.tight_layout()
plt.show()

"""## MLP MODEL 3 : Model Eğitimi"""

mlp_model3 = MLPClassifier(
    hidden_layer_sizes=(50,),  # Tek katman, 50 nöron
    max_iter=200,  # 200 epoch
    batch_size=64,  # Her iterasyonda 64 örnek
    activation='logistic',  # Sigmoid aktivasyon fonksiyonu
    learning_rate_init=0.005,  # Öğrenme oranı 0.005
    random_state=42
)
mlp_model3.fit(X_train_scaled, y_train)

y_pred_model3 = mlp_model3.predict(X_test_scaled)
print("Model 3 - Performans (Aktivasyon Fonksiyonunu Değiştiren)")
print(classification_report(y_test, y_pred_model3))

"""## MLP MODEL 3 : RandomizedSearchCV ile Hiperparametre Optimizasyonu"""

from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import RandomizedSearchCV
import numpy as np
import matplotlib.pyplot as plt

# Hiperparametre aralıkları
param_dist_model3 = {
    'hidden_layer_sizes': [(50,), (100,), (50, 50)],  # Tek ve iki katmanlı yapılar
    'activation': ['logistic', 'relu', 'tanh'],  # Farklı aktivasyon fonksiyonları
    'solver': ['adam'],  # Daha hızlı optimizasyon algoritması
    'alpha': [0.0001, 0.001, 0.01],  # L2 regülarizasyon parametresi
    'batch_size': [32, 64],  # Mini-batch boyutları
    'learning_rate_init': [0.001, 0.005, 0.01],  # Öğrenme oranları
    'max_iter': [200]  # Epoch sayısı sabit tutuldu
}

# RandomizedSearchCV tanımlama
random_search_model3 = RandomizedSearchCV(
    MLPClassifier(random_state=42, early_stopping=True),  # Early stopping ile fazla iterasyonları engelleme
    param_distributions=param_dist_model3,
    n_iter=10,  # Rastgele 10 farklı kombinasyon dene
    cv=3,  # 3 katlı çapraz doğrulama
    scoring='accuracy',  # Doğruluk metriği
    n_jobs=-1,  # Tüm işlemcileri kullan
    verbose=2
)

# Modeli eğitme
random_search_model3.fit(X_train_scaled, y_train)

# En iyi hiperparametreleri ve sonuçları yazdırma
print("Model 3 - En iyi hiperparametreler:", random_search_model3.best_params_)
print("Model 3 - En iyi doğruluk skoru (cv):", random_search_model3.best_score_)

# En iyi modeli seçme
best_model3 = random_search_model3.best_estimator_

# Eğitim kaybı grafiği
if hasattr(best_model3, "loss_curve_"):
    plt.figure(figsize=(8, 6))
    plt.plot(best_model3.loss_curve_, label='Eğitim Kaybı (Loss)')
    plt.title('Model 3 - Eğitim Sürecinde Kayıp Grafiği')
    plt.xlabel('Epoch')
    plt.ylabel('Kayıp (Loss)')
    plt.legend()
    plt.grid()
    plt.show()
else:
    print("Modelde loss_curve_ özelliği bulunamadı.")

# Test seti üzerindeki performansı değerlendirme
y_pred_model3 = best_model3.predict(X_test_scaled)
print("Model 3 - Performans (Hiperparametre Optimizasyonu ile)")
print(classification_report(y_test, y_pred_model3))

"""**Sonuç olarak:** Model 3, %80 doğruluk oranı ile büyük sınıflarda (ör. 13, 12, 10) yüksek performans gösterirken, küçük sınıflarda (ör. 0, 19, 20) zayıf kalmıştır; 100 nöronlu tek katman, relu aktivasyonu ve adam optimizasyonu ile dengeli sonuçlar ürettiğini görüyoruz, fakat model için iyileştirme potansiyeli bulunmakta olduğunu söyleyebiliriz.

# NOT: Model 3'ün İlk Hali ve RandomizedSearchCV ile Optimize Edilmiş Hali Arasındaki Fark:

Optimize edilen modelde, doğruluk değerinde %6 artış ve optimizasyon metriklerinde belirgin iyileşmeler sağlamıştır.
Özellikle küçük örnekleme sahip sınıflarda (Sınıf 0, 19, 41) recall ve F1-Score değerlerinde iyileşme sağlanmıştır.
Daha büyük örneklem destekli sınıflarda (Sınıf 12, 38) ise doğruluk korunarak modelin genel performansı artırılmıştır.
Sonuç: RandomizedSearchCV ile optimize edilen model, genel doğruluk ve sınıf dengesi açısından daha tutarlı ve başarılı bir sonuç verdiğini gözlemlemekteyiz.

## MLP MODEL 3 : Kayıp Değerleri Grafiği
"""

import matplotlib.pyplot as plt

# Model 3'ün kayıp değerlerini kontrol etme ve görselleştirme
if hasattr(best_model3, "loss_curve_"):
    plt.figure(figsize=(8, 6))
    plt.plot(best_model3.loss_curve_, label='Eğitim Kaybı (Loss)')
    plt.title('Model 3 - Eğitim Sürecinde Kayıp Grafiği', fontsize=16)
    plt.xlabel('Epoch', fontsize=14)
    plt.ylabel('Kayıp (Loss)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.show()
else:
    print("Model 3'te 'loss_curve_' özelliği bulunamadı.")

"""**Grafik bize,** Model 3'ün kaybının (loss) ilk birkaç epoch'ta hızlı bir şekilde düştüğünü ve ardından 20. epoch'tan sonra stabil bir seviyeye ulaştığını göstermektedir. Bu, modelin hızlı öğrenme kapasitesine ve başarılı bir optimizasyon sürecinde olduğunu bize göstermektedir.

## MLP MODEL 3 : Karışıklık Matrisi:
"""

from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Model 3'ün gerçek ve tahmin edilen değerlerini kullanarak karışıklık matrisini hesaplama
confusion_mtx_model3 = confusion_matrix(y_test, y_pred_model3)

# Karışıklık matrisini görselleştirme
plt.figure(figsize=(12, 10))
sns.heatmap(confusion_mtx_model3, annot=True, fmt='d', cmap='Blues', cbar=True)
plt.title("Model 3 - Karışıklık Matrisi", fontsize=16)
plt.xlabel("Tahmin Edilen Etiket", fontsize=14)
plt.ylabel("Gerçek Etiket", fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.show()

"""## MLP MODEL 4 : Model Eğitimi"""

mlp_model4 = MLPClassifier(
    hidden_layer_sizes=(64, 32),  # İki katman: 64 ve 32 nöron
    max_iter=250,  # 250 epoch
    batch_size=32,  # Her iterasyonda 32 örnek işlenecek
    learning_rate_init=0.002,  # Daha düşük öğrenme oranı
    random_state=42
)
mlp_model4.fit(X_train_scaled, y_train)

y_pred_model4 = mlp_model4.predict(X_test_scaled)
print("Model 4 - Performans (Düşük Öğrenme Oranı)")
print(classification_report(y_test, y_pred_model4))

"""## MLP MODEL 4 : RandomizedSearchCV ile Hiperparametre Optimizasyonu"""

"from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import RandomizedSearchCV
import numpy as np
import matplotlib.pyplot as plt

# Hiperparametre aralıkları
param_dist_model4 = {
    'hidden_layer_sizes': [(64, 32), (128, 64), (64, 32, 16)],  # Farklı katman yapıları
    'activation': ['relu', 'tanh'],  # Aktivasyon fonksiyonları
    'solver': ['adam'],  # Hızlı optimizasyon algoritması
    'alpha': [0.0001, 0.001, 0.01],  # L2 regülarizasyon parametresi
    'batch_size': [16, 32],  # Mini-batch boyutları
    'learning_rate_init': [0.001, 0.002, 0.005],  # Öğrenme oranları
    'max_iter': [250]  # Epoch sayısı sabit tutuldu
}

# RandomizedSearchCV tanımlama
random_search_model4 = RandomizedSearchCV(
    MLPClassifier(random_state=42, early_stopping=True),  # Early stopping ile fazla iterasyonları engelle
    param_distributions=param_dist_model4,
    n_iter=10,  # Rastgele 10 farklı kombinasyon dene
    cv=3,  # 3 katlı çapraz doğrulama
    scoring='accuracy',  # Doğruluk metriği
    n_jobs=-1,  # Tüm işlemcileri kullan
    verbose=2
)

# Modeli eğitme
random_search_model4.fit(X_train_scaled, y_train)

# En iyi hiperparametreleri ve sonuçları yazdırma
print("Model 4 - En iyi hiperparametreler:", random_search_model4.best_params_)
print("Model 4 - En iyi doğruluk skoru (cv):", random_search_model4.best_score_)

# En iyi modeli seçme
best_model4 = random_search_model4.best_estimator_

# Eğitim kaybı grafiği çizme
if hasattr(best_model4, "loss_curve_"):
    plt.figure(figsize=(8, 6))
    plt.plot(best_model4.loss_curve_, label='Eğitim Kaybı (Loss)')
    plt.title('Model 4 - Eğitim Sürecinde Kayıp Grafiği')
    plt.xlabel('Epoch')
    plt.ylabel('Kayıp (Loss)')
    plt.legend()
    plt.grid()
    plt.show()
else:
    print("Modelde loss_curve_ özelliği bulunamadı.")

# Test seti üzerindeki performansı değerlendirme
y_pred_model4 = best_model4.predict(X_test_scaled)
print("Model 4 - Performans (Hiperparametre Optimizasyonu ile)")
print(classification_report(y_test, y_pred_model4))

"""**Sonuç olarak:** Model %80 doğruluk oranına ulaşmıştır. Çok katmanlı bir yapı (64, 32, 16), ReLU aktivasyonu ve adam optimizasyonu ile öğrenme oranı 0.001 olarak optimize edilmiştir. Büyük sınıflarda (ör. sınıf 13, 12, 10) yüksek başarı gösterirken, küçük veri gruplarında (ör. sınıf 0, 19, 24) performans düşüşü yaşamıştır. Genel olarak modelimiz dengeli bir performans sergileyerek büyük sınıflarda etkili sonuçlar sağladığını bize göstermiştir.

# NOT: Model 4'ün İlk Hali ve RandomizedSearchCV ile Optimize Edilmiş Hali Arasındaki Fark:

Optimize edilen model, bazı küçük sınıflarda (Sınıf 30, 41) recall ve F1-Score'da iyileşme sağlamış, ancak büyük sınıflar ve genel doğruluk açısından performansı ilk modelle benzer kalmıştır.
Optimize edilen model, daha derin bir yapıya sahip olduğu için bazı sınıflar için daha iyi uyum sağlamış, ancak overfitting riskine yol açabilecek hafif performans düşüşleri gözlemlenmiştir.
Sonuç: İlk model, genel performans açısından daha dengeli ve başarılıdır. Optimize edilen model, belirli sınıflarda iyileşmeler gösterse de genel doğruluk ve metriklerde hafif bir düşüş yaşamıştır.

## MLP MODEL 4 : Kayıp Değerleri Grafiği
"""

import matplotlib.pyplot as plt

# Model 4'ün kayıp değerlerini görselleştir
if hasattr(best_model4, "loss_curve_"):
    plt.figure(figsize=(8, 6))
    plt.plot(best_model4.loss_curve_, label='Eğitim Kaybı (Loss)')
    plt.title('Model 4 - Eğitim Sürecinde Kayıp Grafiği', fontsize=16)
    plt.xlabel('Epoch', fontsize=14)
    plt.ylabel('Kayıp (Loss)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.show()
else:
    print("Model 4'te 'loss_curve_' özelliği bulunamadı.")

"""**Grafik bize,** Model 4'ün eğitim kaybında, hızlı bir başlangıç kaybı azalması gösteriyor ve yaklaşık 10. epoch'tan sonra kayıp değerinin oldukça düşük seviyelerde sabitlendiğini ortaya koyuyor. Bu durum, modelin hızlı bir şekilde öğrenme kapasitesine ulaştığını ve eğitim süreci boyunca kararlılığını koruduğunu bize göstermektedir. Kaybın 0.25 seviyesine kadar düştüğü görmekteyiz, bu da modelin genel başarımının iyi olduğunu bize ifade etmektedir.

## MLP MODEL 4 : Karışıklık Matrisi
"""

from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Model 4'ün tahmin sonuçları
confusion_mtx_model4 = confusion_matrix(y_test, y_pred_model4)

# Karışıklık matrisini görselleştir
plt.figure(figsize=(12, 10))
sns.heatmap(confusion_mtx_model4, annot=True, fmt='d', cmap='Blues', cbar=True)
plt.title("Model 4 - Karışıklık Matrisi", fontsize=16)
plt.xlabel("Tahmin Edilen Etiket", fontsize=14)
plt.ylabel("Gerçek Etiket", fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.show()

"""## 4 MLP Modelinin Performans Sonuçları Grafiği"""

import matplotlib.pyplot as plt
import numpy as np

# Modellerin sonuçları
models = ["Model 1", "Model 2", "Model 3", "Model 4"]
accuracy = [0.81, 0.78, 0.80, 0.80]
precision_macro = [0.78, 0.75, 0.75, 0.77]
recall_macro = [0.75, 0.70, 0.72, 0.71]
f1_macro = [0.76, 0.71, 0.73, 0.72]
precision_weighted = [0.81, 0.79, 0.80, 0.81]

# Grafik oluşturma
x = np.arange(len(models))
width = 0.15

fig, ax = plt.subplots(figsize=(10, 6))

# Her metriği yan yana çubuklarla gösterme
ax.bar(x - 2 * width, accuracy, width, label="Accuracy", color="skyblue")
ax.bar(x - width, precision_macro, width, label="Precision (Macro Avg)", color="orange")
ax.bar(x, recall_macro, width, label="Recall (Macro Avg)", color="green")
ax.bar(x + width, f1_macro, width, label="F1-Score (Macro Avg)", color="red")
ax.bar(x + 2 * width, precision_weighted, width, label="Precision (Weighted Avg)", color="purple")

# Ayarlar
ax.set_xlabel("Models")
ax.set_ylabel("Scores")
ax.set_title("Comparison of Model Metrics")
ax.set_xticks(x)
ax.set_xticklabels(models)
ax.legend(loc="best")
plt.ylim(0, 1)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Grafiği gösterme
plt.show()

"""**Grafik bize, **"""