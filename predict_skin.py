import tensorflow as tf
import numpy as np
import cv2
import sys
import os

# ================= LOAD MODEL =================
MODEL_PATH = "skin_model_final.h5"

if not os.path.exists(MODEL_PATH):
    print("❌ Model file not found!")
    exit()

model = tf.keras.models.load_model(MODEL_PATH)
print("✅ Model Loaded Successfully")

# ================= CLASS NAMES =================
# Confirmed from your class_indices
class_names = [
    "Basal Cell Carcinoma",
    "Benign Keratosis",
    "Melanocytic Nevi (NV)",
    "Melanoma"
]

# ================= GET IMAGE PATH =================
if len(sys.argv) < 2:
    print("❌ Please provide image path")
    print("Example:")
    print("python predict_skin.py image.jpg")
    exit()

image_path = sys.argv[1]

if not os.path.exists(image_path):
    print("❌ Image path not found")
    exit()

# ================= READ IMAGE =================
img = cv2.imread(image_path)

if img is None:
    print("❌ Unable to read image")
    exit()

# Convert BGR → RGB
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Resize to training size
img = cv2.resize(img, (224, 224))

# 🔥 IMPORTANT: SAME PREPROCESSING AS TRAINING
img = img.astype("float32") / 255.0

# Add batch dimension
img = np.expand_dims(img, axis=0)

# ================= PREDICT =================
prediction = model.predict(img)

print("\n===== Prediction Probabilities =====")

for i, class_name in enumerate(class_names):
    prob = prediction[0][i] * 100
    print(f"{class_name}: {prob:.2f}%")

predicted_index = np.argmax(prediction)
predicted_class = class_names[predicted_index]
confidence = prediction[0][predicted_index] * 100

print("\n🎯 Final Prediction:", predicted_class)
print(f"🔥 Confidence: {confidence:.2f}%")