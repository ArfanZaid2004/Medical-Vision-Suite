import tensorflow as tf
import numpy as np
import cv2
import sys

# 🔹 Load trained model
model = tf.keras.models.load_model("medical_xray_finetuned.h5")


# 🔹 Class names (must match training folders order)
classes = ["Covid", "Normal", "Pneumonia", "Pneumothorax", "Tuberculosis"]

# 🔹 Image size (same as training)
IMG_SIZE = 224


def predict_image(img_path):
    # Read image
    img = cv2.imread(img_path)

    if img is None:
        print("❌ Image not found. Check file path.")
        return

    # Resize and normalize
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = img / 255.0

    # Add batch dimension
    img = np.expand_dims(img, axis=0)

    # Predict
    predictions = model.predict(img)
    class_index = np.argmax(predictions)

    
    confidence = np.max(predictions)

    print("\n🩺 Predicted Disease:", classes[class_index])
    print("📊 Confidence:", round(float(confidence) * 100, 2), "%")


# 🔹 Run from terminal: python predict.py image.jpg
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict.py <image_path>")
    else:
        predict_image(sys.argv[1])
