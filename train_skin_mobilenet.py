import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt

# ================= PATHS =================
train_dir = r"C:\Users\Admin\Downloads\Skin_dataset_split\train"
test_dir  = r"C:\Users\Admin\Downloads\Skin_dataset_split\test"

IMG_SIZE = 224
BATCH_SIZE = 32

# ================= DATA =================
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

# ================= CLASS WEIGHTS =================
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_data.classes),
    y=train_data.classes
)
class_weights = dict(enumerate(class_weights))
print("Class Weights:", class_weights)

# ================= MODEL =================
base_model = MobileNetV2(
    weights="imagenet",
    include_top=False,
    input_shape=(224,224,3)
)

# -------- STAGE 1 (Frozen) --------
base_model.trainable = False

x = GlobalAveragePooling2D()(base_model.output)
x = Dense(128, activation='relu')(x)
x = Dropout(0.3)(x)
output = Dense(4, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=output)

model.compile(
    optimizer=Adam(learning_rate=1e-4),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

early_stop = EarlyStopping(
    monitor="val_accuracy",
    patience=3,
    restore_best_weights=True
)

print("\n🚀 Stage 1 Training (Frozen)...\n")

history1 = model.fit(
    train_data,
    validation_data=test_data,
    epochs=6,
    class_weight=class_weights,
    callbacks=[early_stop]
)

# -------- STAGE 2 (Fine-Tune Last 20 Layers) --------
base_model.trainable = True

for layer in base_model.layers[:-20]:
    layer.trainable = False

model.compile(
    optimizer=Adam(learning_rate=5e-6),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

print("\n🚀 Stage 2 Fine-Tuning...\n")

history2 = model.fit(
    train_data,
    validation_data=test_data,
    epochs=8,
    class_weight=class_weights,
    callbacks=[early_stop]
)

# ================= SAVE =================
model.save("skin_model_mobilenet.h5")
print("\n✅ Model Saved as skin_model_mobilenet.h5")

# ================= PLOT =================
plt.plot(history1.history['accuracy'] + history2.history['accuracy'], label="Train")
plt.plot(history1.history['val_accuracy'] + history2.history['val_accuracy'], label="Val")
plt.legend()
plt.title("Training vs Validation Accuracy")
plt.show()