import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt

# Paths
train_dir = r"C:\Users\Admin\Downloads\archive\dataset\train"
test_dir  = r"C:\Users\Admin\Downloads\archive\dataset\test"

IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 10   # small extra training

# Data generators
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

# 🔹 Load previously trained MobileNet model
model = load_model("medical_xray_mobilenet.h5")

# 🔹 Unfreeze last 20 layers for fine-tuning
for layer in model.layers[-20:]:
    layer.trainable = True

# Compile with LOWER learning rate (important)
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

print("🔬 Starting fine-tuning...")

history = model.fit(
    train_data,
    epochs=EPOCHS,
    validation_data=test_data
)

# Save improved model
model.save("medical_xray_finetuned.h5")

print("\n✅ Fine-tuning completed. Best model saved!")

# Plot accuracy
plt.plot(history.history["accuracy"], label="Train Accuracy")
plt.plot(history.history["val_accuracy"], label="Val Accuracy")
plt.legend()
plt.title("Fine-Tuned Model Accuracy")
plt.show()
