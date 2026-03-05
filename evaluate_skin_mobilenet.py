import tensorflow as tf
import numpy as np
import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# ================= PATHS =================
MODEL_PATH = "skin_model_mobilenet_v2.h5"
test_dir = r"C:\Users\Admin\Desktop\medical_cnn_project\datasets\Skin_dataset_split\test"

IMG_SIZE = 224
BATCH_SIZE = 32

# ================= LOAD MODEL =================
model = tf.keras.models.load_model(MODEL_PATH, compile=False)
print("✅ Model Loaded")

# ================= TEST DATA =================
test_datagen = ImageDataGenerator(rescale=1./255)

test_data = test_datagen.flow_from_directory(
    test_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=False  # VERY IMPORTANT
)

class_names = list(test_data.class_indices.keys())
print("Classes:", class_names)

# ================= PREDICT =================
predictions = model.predict(test_data)
y_pred = np.argmax(predictions, axis=1)
y_true = test_data.classes

# ================= ACCURACY =================
accuracy = np.mean(y_pred == y_true)
print(f"\n🎯 Overall Test Accuracy: {accuracy*100:.2f}%")

# ================= CLASSIFICATION REPORT =================
print("\n📊 Classification Report:\n")
print(classification_report(y_true, y_pred, target_names=class_names))

# ================= CONFUSION MATRIX =================
cm = confusion_matrix(y_true, y_pred)

plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt='d',
            xticklabels=class_names,
            yticklabels=class_names,
            cmap="Blues")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()