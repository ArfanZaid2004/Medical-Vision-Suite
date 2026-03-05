import tensorflow as tf
import numpy as np
import tensorflow.keras.backend as K
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import matplotlib.pyplot as plt

# ================= FOCAL LOSS =================
def focal_loss(gamma=2., alpha=0.25):
    def loss(y_true, y_pred):
        epsilon = K.epsilon()
        y_pred = K.clip(y_pred, epsilon, 1. - epsilon)
        cross_entropy = -y_true * K.log(y_pred)
        weight = alpha * K.pow(1 - y_pred, gamma)
        return K.sum(weight * cross_entropy, axis=1)
    return loss

# ================= PATHS =================
train_dir = r"C:\Users\Admin\Downloads\Skin_dataset_split\train"
test_dir  = r"C:\Users\Admin\Downloads\Skin_dataset_split\test"

IMG_SIZE = 224
BATCH_SIZE = 32

# ================= STRONGER AUGMENTATION =================
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    zoom_range=0.2,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True,
    brightness_range=[0.8,1.2]
)

test_datagen = ImageDataGenerator(rescale=1./255)

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

# ================= MODEL =================
base_model = MobileNetV2(
    weights="imagenet",
    include_top=False,
    input_shape=(224,224,3)
)

# -------- STAGE 1 (Frozen Base) --------
base_model.trainable = False

x = GlobalAveragePooling2D()(base_model.output)
x = Dense(128, activation='relu')(x)
x = Dropout(0.4)(x)
output = Dense(4, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=output)

model.compile(
    optimizer=Adam(1e-4),
    loss=focal_loss(),
    metrics=["accuracy"]
)

early_stop = EarlyStopping(monitor="val_accuracy", patience=4, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor="val_loss", factor=0.3, patience=3)

print("\n🚀 Stage 1 Training...\n")

history1 = model.fit(
    train_data,
    validation_data=test_data,
    epochs=8,
    callbacks=[early_stop, reduce_lr]
)

# -------- STAGE 2 (Fine-Tune Last 40 Layers) --------
base_model.trainable = True

for layer in base_model.layers[:-40]:
    layer.trainable = False

model.compile(
    optimizer=Adam(1e-5),
    loss=focal_loss(),
    metrics=["accuracy"]
)

print("\n🚀 Stage 2 Fine-Tuning...\n")

history2 = model.fit(
    train_data,
    validation_data=test_data,
    epochs=15,
    callbacks=[early_stop, reduce_lr]
)

model.save("skin_model_mobilenet_v2.h5")
print("\n✅ Model Saved as skin_model_mobilenet_v2.h5")

plt.plot(history1.history['accuracy'] + history2.history['accuracy'], label="Train")
plt.plot(history1.history['val_accuracy'] + history2.history['val_accuracy'], label="Val")
plt.legend()
plt.title("MobileNet V2 Training Curve")
plt.show()