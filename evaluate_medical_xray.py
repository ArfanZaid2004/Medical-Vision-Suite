import tensorflow as tf
import numpy as np
import os
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ================= LOAD MODEL =================
MODEL_PATH = MODEL_PATH = r"C:\Users\Admin\Desktop\medical_cnn_project\backend\medical_xray_finetuned.h5"

model = tf.keras.models.load_model(MODEL_PATH, compile=False)
print("✅ Model Loaded Successfully")

# ================= DATASET PATH =================
test_dir = r"C:\Users\Admin\Desktop\medical_cnn_project\datasets\chest_dataset\test"

IMG_SIZE = 224
BATCH_SIZE = 32

# ================= DATA GENERATOR =================
test_datagen = ImageDataGenerator(rescale=1./255)

test_data = test_datagen.flow_from_directory(
    test_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=False,
    color_mode="rgb"
)

class_names = list(test_data.class_indices.keys())
print("Classes:", class_names)

# ================= PREDICTIONS =================
pred_probs = model.predict(test_data)
y_pred = np.argmax(pred_probs, axis=1)
y_true = test_data.classes

# ================= ACCURACY =================
accuracy = np.mean(y_pred == y_true)
print(f"\n🎯 Overall Test Accuracy: {accuracy*100:.2f}%")

# ================= CLASSIFICATION REPORT =================
print("\n📊 Classification Report:\n")
print(classification_report(y_true, y_pred, target_names=class_names))

# ================= CONFUSION MATRIX =================
cm = confusion_matrix(y_true, y_pred)

plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=class_names,
            yticklabels=class_names)

plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Medical X-Ray Confusion Matrix")
plt.show()