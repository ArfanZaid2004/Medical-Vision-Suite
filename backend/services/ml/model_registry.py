import os

import cv2
import numpy as np
import tensorflow as tf

from core.config import BASE_DIR, IMG_SIZE

# Load trained models once at startup.
CHEST_MODEL = tf.keras.models.load_model(
    os.path.join(BASE_DIR, "medical_xray_finetuned.h5"), compile=False
)
BRAIN_MODEL = tf.keras.models.load_model(
    os.path.join(BASE_DIR, "brain_tumor_mobilenet.h5"), compile=False
)
SKIN_MODEL = tf.keras.models.load_model(
    os.path.join(BASE_DIR, "skin_model_mobilenet_v2.h5"), compile=False
)

CHEST_CLASSES = ["Covid", "Normal", "Pneumonia", "Pneumothorax", "Tuberculosis"]
BRAIN_CLASSES = ["Glioma", "Meningioma", "No Tumor", "Pituitary"]
SKIN_CLASSES = [
    "Basal Cell Carcinoma",
    "Benign Keratosis",
    "Melanocytic Nevi (NV)",
    "Melanoma",
]


def preprocess_image(path):
    img = cv2.imread(path)
    if img is None:
        raise ValueError("Invalid image")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = img / 255.0
    return np.expand_dims(img, axis=0)
