import tensorflow as tf

print("\n=== BRAIN MODEL ===\n")
brain = tf.keras.models.load_model(r"C:\Users\Admin\Desktop\medical_cnn_project\backend\brain_tumor_mobilenet.h5", compile=False)
brain.summary()

print("\n=== SKIN MODEL ===\n")
skin = tf.keras.models.load_model(r"C:\Users\Admin\Desktop\medical_cnn_project\backend\skin_model_mobilenet_v2.h5", compile=False)
skin.summary()

print("\n=== CHEST MODEL ===\n")
chest = tf.keras.models.load_model(r"C:\Users\Admin\Desktop\medical_cnn_project\backend\medical_xray_finetuned.h5", compile=False)
chest.summary()