import tensorflow as tf
import numpy as np
import cv2
import sys

# Load trained MobileNet brain tumor model
model = tf.keras.models.load_model("brain_tumor_mobilenet.h5")

# Class names (must match dataset folder order)
classes = ["glioma", "meningioma", "notumor", "pituitary"]

IMG_SIZE = 224

# Get image path from command line
if len(sys.argv) < 2:
    print("❌ Please provide MRI image path")
    sys.exit()

img_path = sys.argv[1]

# Read image
img = cv2.imread(img_path)

if img is None:
    print("❌ Cannot read image. Check path.")
    sys.exit()

# Preprocess
img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
img = img / 255.0
img = np.expand_dims(img, axis=0)

# Predict
preds = model.predict(img)
pred_class = classes[np.argmax(preds)]
confidence = float(np.max(preds) * 100)

print("\n🧠 Brain MRI Prediction")
print(f"Predicted Tumor Type: {pred_class}")
print(f"Confidence: {confidence:.2f}%\n")
