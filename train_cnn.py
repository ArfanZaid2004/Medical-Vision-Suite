import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt

# 🔹 Dataset paths
train_dir = r"C:\Users\Admin\Downloads\archive\dataset\train"
test_dir  = r"C:\Users\Admin\Downloads\archive\dataset\test"

# 🔹 Image settings
IMG_SIZE = 224
BATCH_SIZE = 32

# 🔹 Data generators (normalization)
train_datagen = ImageDataGenerator(rescale=1./255)
test_datagen  = ImageDataGenerator(rescale=1./255)

train_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

test_data = test_datagen.flow_from_directory(
    test_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

# 🔹 CNN Model
model = models.Sequential([
    layers.Conv2D(32, (3,3), activation="relu", input_shape=(224,224,3)),
    layers.MaxPooling2D(2,2),

    layers.Conv2D(64, (3,3), activation="relu"),
    layers.MaxPooling2D(2,2),

    layers.Conv2D(128, (3,3), activation="relu"),
    layers.MaxPooling2D(2,2),

    layers.Flatten(),
    layers.Dense(128, activation="relu"),
    layers.Dropout(0.5),

    layers.Dense(5, activation="softmax")  # 5 classes
])

# 🔹 Compile model
model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# 🔹 Train model
history = model.fit(
    train_data,
    epochs=10,
    validation_data=test_data
)

# 🔹 Save trained model
model.save("medical_xray_cnn.h5")

print("\n✅ Training completed. Model saved as medical_xray_cnn.h5")

# 🔹 Plot accuracy graph
plt.plot(history.history["accuracy"], label="Train Accuracy")
plt.plot(history.history["val_accuracy"], label="Validation Accuracy")
plt.legend()
plt.title("Training vs Validation Accuracy")
plt.show()
