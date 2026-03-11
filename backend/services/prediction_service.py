import os
import traceback
import uuid

import numpy as np

from core.config import UPLOAD_DIR
from core.utils import build_image_url
from services.ml.gradcam import generate_fallback_overlay, generate_gradcam_overlay
from services.ml.model_registry import (
    BRAIN_CLASSES,
    BRAIN_MODEL,
    CHEST_CLASSES,
    CHEST_MODEL,
    SKIN_CLASSES,
    SKIN_MODEL,
    preprocess_image,
)
from repositories.prediction_repository import insert_prediction


def _predict_for_scan_type(selected_type, img):
    if selected_type == "chest":
        pred = CHEST_MODEL.predict(img, verbose=0)
        class_index = int(np.argmax(pred))
        confidence = float(np.max(pred))
        return (
            {
                "type": "Chest X-ray",
                "prediction": CHEST_CLASSES[class_index],
                "confidence": round(confidence * 100, 2),
            },
            CHEST_MODEL,
            class_index,
        )
    if selected_type == "brain":
        pred = BRAIN_MODEL.predict(img, verbose=0)
        class_index = int(np.argmax(pred))
        confidence = float(np.max(pred))
        return (
            {
                "type": "Brain MRI",
                "prediction": BRAIN_CLASSES[class_index],
                "confidence": round(confidence * 100, 2),
            },
            BRAIN_MODEL,
            class_index,
        )
    if selected_type == "skin":
        pred = SKIN_MODEL.predict(img, verbose=0)
        class_index = int(np.argmax(pred))
        confidence = float(np.max(pred))
        return (
            {
                "type": "Skin Lesion",
                "prediction": SKIN_CLASSES[class_index],
                "confidence": round(confidence * 100, 2),
            },
            SKIN_MODEL,
            class_index,
        )
    raise ValueError("Invalid type selected")


def predict_and_store(
    *,
    file_storage,
    original_name,
    selected_type,
    user_id,
    entered_by_role,
    patient_name,
    patient_age,
    patient_sex,
    static_folder,
    host_url,
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    gradcam_dir = os.path.join(static_folder, "gradcam")
    os.makedirs(gradcam_dir, exist_ok=True)

    _, ext = os.path.splitext(original_name)
    saved_filename = f"{uuid.uuid4().hex}{ext.lower()}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)

    gradcam_filename = f"{uuid.uuid4().hex}_gradcam.jpg"
    gradcam_saved_path = os.path.join(gradcam_dir, gradcam_filename)
    gradcam_error = None

    keep_file = False
    file_storage.save(saved_path)
    try:
        img = preprocess_image(saved_path)
        result, model, class_index = _predict_for_scan_type(selected_type, img)

        try:
            generate_fallback_overlay(saved_path, gradcam_saved_path)
        except Exception as err:
            gradcam_error = f"fallback_failed:{err}"
            traceback.print_exc()
            gradcam_filename = None
            gradcam_saved_path = None

        try:
            if gradcam_saved_path:
                generate_gradcam_overlay(
                    image_path=saved_path,
                    model=model,
                    class_index=class_index,
                    output_path=gradcam_saved_path,
                    image_size=img.shape[1],
                    last_conv_layer_name="Conv_1",
                )
        except Exception as err:
            gradcam_error = f"{err} | fallback_overlay_used"
            traceback.print_exc()

        insert_prediction(
            user_id=user_id,
            entered_by_role=entered_by_role,
            scan_type=result["type"],
            prediction=result["prediction"],
            confidence=result["confidence"],
            patient_name=patient_name,
            patient_age=patient_age,
            patient_sex=patient_sex,
            image_filename=saved_filename,
        )
        keep_file = True

        result["image_url"] = build_image_url(saved_filename)
        result["gradcam"] = f"/static/gradcam/{gradcam_filename}" if gradcam_filename else None
        result["gradcam_url"] = (
            f"{host_url.rstrip('/')}/static/gradcam/{gradcam_filename}" if gradcam_filename else None
        )
        result["gradcam_error"] = gradcam_error
        return result, 200
    except ValueError as err:
        return {"error": str(err)}, 400
    finally:
        if not keep_file and os.path.exists(saved_path):
            os.remove(saved_path)
        if not keep_file and gradcam_saved_path and os.path.exists(gradcam_saved_path):
            os.remove(gradcam_saved_path)
