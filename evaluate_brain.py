import tensorflow as tf
import numpy as np
import os
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Load trained model
model = tf.keras.models.load_model(
    r"C:\Users\Admin\Desktop\medical_cnn_project\backend\brain_tumor_mobilenet.h5",
    compile=False
)

# Dataset path
test_dir = r"C:\Users\Admin\Desktop\medical_cnn_project\datasets\brain_tumor_dataset\Testing"
IMG_SIZE = 224
BATCH_SIZE = 32

# Data generator
test_datagen = ImageDataGenerator(rescale=1./255)

test_data = test_datagen.flow_from_directory(
    test_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=False,
    color_mode="rgb"
)

# Predictions
pred_probs = model.predict(test_data)
y_pred = np.argmax(pred_probs, axis=1)
y_true = test_data.classes
class_names = list(test_data.class_indices.keys())

# Confusion matrix
cm = confusion_matrix(y_true, y_pred)

# Classification report
report = classification_report(y_true, y_pred, target_names=class_names)
print("\n📊 Classification Report:\n")
print(report)

# Plot confusion matrix
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=class_names,
            yticklabels=class_names)

plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Brain Tumor Confusion Matrix")
plt.show()
