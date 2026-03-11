from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from repositories.auth_repository import get_user_role
from services.prediction_service import predict_and_store
from core.utils import is_allowed_image

predict_bp = Blueprint("predict_bp", __name__)


@predict_bp.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    original_name = secure_filename(file.filename or "")
    if not original_name:
        return jsonify({"error": "Invalid file name"}), 400
    if not is_allowed_image(original_name):
        return jsonify({"error": "Unsupported file type"}), 400

    selected_type = (request.form.get("type") or "").strip().lower()
    user_id = request.form.get("user_id", type=int)
    patient_name = (request.form.get("patient_name") or "").strip()
    patient_age = request.form.get("patient_age", type=int)
    patient_sex = (request.form.get("patient_sex") or "").strip()

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    if not patient_name or patient_age is None or not patient_sex:
        return jsonify({"error": "Missing patient details"}), 400

    entered_by_role = get_user_role(user_id)
    if not entered_by_role:
        return jsonify({"error": "User not found"}), 404

    payload, status = predict_and_store(
        file_storage=file,
        original_name=original_name,
        selected_type=selected_type,
        user_id=user_id,
        entered_by_role=entered_by_role,
        patient_name=patient_name,
        patient_age=patient_age,
        patient_sex=patient_sex,
        static_folder=current_app.static_folder,
        host_url=request.host_url,
    )
    return jsonify(payload), status
