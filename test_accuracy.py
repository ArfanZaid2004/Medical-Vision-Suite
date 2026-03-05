
import tensorflow as tf
import numpy as np
import cv2
import os

# 🔹 Load fine-tuned model
model = tf.keras.models.load_model("medical_xray_finetuned.h5")

# 🔹 Class names
classes = ["Covid", "Normal", "Pneumonia", "Pneumothorax", "Tuberculosis"]

IMG_SIZE = 224

# 🔹 Folder containing 10 test images
folder_path = r"C:\Users\Admin\Downloads\testing"   # ← change if needed

print("\n🔬 Predicting images in folder...\n")

# Loop through all images in folder
for file in os.listdir(folder_path):

    if not file.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    img_path = os.path.join(folder_path, file)

    # Read & preprocess
    img = cv2.imread(img_path)
    if img is None:
        print(f"{file} → ❌ Cannot read image")
        continue

    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    # Predict
    preds = model.predict(img, verbose=0)
    pred_class = classes[np.argmax(preds)]
    confidence = float(np.max(preds) * 100)

    print(f"{file:25} → {pred_class:12} ({confidence:5.1f}%)")

print("\n✅ Folder testing completed.")
