import os
import shutil
import random

# ============================
# CHANGE THESE PATHS
# ============================

source_dir = r"C:\Users\Admin\Downloads\Skin_dataset"
output_dir = r"C:\Users\Admin\Downloads\Skin_dataset_split"

# Exact folder names from your screenshot
selected_classes = [
    "Melanoma",
    "Melanocytic Nevi (NV)",
    "Basal Cell Carcinoma",
    "Benign Keratosis"
]

train_ratio = 0.8  # 80% train

# ============================
# DELETE OLD SPLIT
# ============================

if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
    print("Old split folder deleted.\n")

# ============================
# CREATE TRAIN & TEST FOLDERS
# ============================

for split in ["train", "test"]:
    for cls in selected_classes:
        os.makedirs(os.path.join(output_dir, split, cls), exist_ok=True)

print("Train/Test folders created.\n")

# ============================
# SPLIT DATASET
# ============================

for cls in selected_classes:

    cls_path = os.path.join(source_dir, cls)

    if not os.path.exists(cls_path):
        print(f"❌ Folder not found: {cls_path}")
        continue

    images = [f for f in os.listdir(cls_path)
              if f.lower().endswith((".jpg", ".jpeg", ".png"))]

    print(f"Processing {cls}")
    print("Total images:", len(images))

    random.shuffle(images)

    split_index = int(len(images) * train_ratio)
    train_images = images[:split_index]
    test_images = images[split_index:]

    # Copy train images
    for i, img in enumerate(train_images):
        shutil.copy(
            os.path.join(cls_path, img),
            os.path.join(output_dir, "train", cls, img)
        )

        if (i + 1) % 500 == 0:
            print(f"  Copied {i+1} train images...")

    # Copy test images
    for i, img in enumerate(test_images):
        shutil.copy(
            os.path.join(cls_path, img),
            os.path.join(output_dir, "test", cls, img)
        )

        if (i + 1) % 200 == 0:
            print(f"  Copied {i+1} test images...")

    print(f"  Done → Train: {len(train_images)} | Test: {len(test_images)}\n")

print("✅ DATASET SPLIT COMPLETE.\n")

# ============================
# VERIFY SPLIT
# ============================

print("Verifying test set:\n")

test_dir = os.path.join(output_dir, "test")

for cls in selected_classes:
    cls_path = os.path.join(test_dir, cls)
    print(cls, "→", len(os.listdir(cls_path)))