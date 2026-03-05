import os
import uuid

import numpy as np
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from config import UPLOAD_DIR
from db import get_db_connection, init_db
from ml import (
    BRAIN_CLASSES,
    BRAIN_MODEL,
    CHEST_CLASSES,
    CHEST_MODEL,
    SKIN_CLASSES,
    SKIN_MODEL,
    preprocess_image,
)
from utils import build_image_url, is_allowed_image

app = Flask(__name__)
CORS(app)
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    role = (data.get("role") or "technician").strip().lower()
    if role not in {"doctor", "technician"}:
        return jsonify({"error": "Invalid role"}), 400
    if not email or not username or not password:
        return jsonify({"error": "Username, email and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return jsonify({"error": "Email already registered"}), 409
        pw_hash = generate_password_hash(password)
        cur.execute(
            "INSERT INTO users (email, username, password_hash, role) VALUES (%s, %s, %s, %s)",
            (email, username, pw_hash, role),
        )
        conn.commit()
        return jsonify({"message": "User registered"}), 201
    finally:
        cur.close()
        conn.close()


@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT id, email, username, role, password_hash FROM users WHERE email = %s",
            (email,),
        )
        user = cur.fetchone()
        success = bool(user and check_password_hash(user["password_hash"], password))
        cur.execute(
            """
            INSERT INTO login_events (email, success, ip_address, user_agent)
            VALUES (%s, %s, %s, %s)
            """,
            (email, success, request.remote_addr, request.headers.get("User-Agent", "")[:255]),
        )
        conn.commit()
        if not success:
            return jsonify({"error": "Invalid email or password"}), 401
        return jsonify(
            {
                "message": "Login successful",
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "username": user["username"],
                    "role": user["role"],
                },
            }
        )
    finally:
        cur.close()
        conn.close()


@app.route("/auth/profile", methods=["GET"])
def get_profile():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT id, email, username, role, created_at FROM users WHERE id = %s",
            (user_id,),
        )
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user)
    finally:
        cur.close()
        conn.close()


@app.route("/auth/profile", methods=["PUT"])
def update_profile():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    username = (data.get("username") or "").strip()
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cur.fetchone():
            return jsonify({"error": "User not found"}), 404
        cur.execute("UPDATE users SET username = %s WHERE id = %s", (username, user_id))
        conn.commit()
        cur.execute("SELECT id, email, username, role FROM users WHERE id = %s", (user_id,))
        updated = cur.fetchone()
        return jsonify({"message": "Profile updated", "user": updated})
    finally:
        cur.close()
        conn.close()


@app.route("/auth/change-password", methods=["POST"])
def change_password():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    current_password = data.get("current_password") or ""
    new_password = data.get("new_password") or ""
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    if not current_password or not new_password:
        return jsonify({"error": "Current and new password are required"}), 400
    if len(new_password) < 6:
        return jsonify({"error": "New password must be at least 6 characters"}), 400

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        if not check_password_hash(user["password_hash"], current_password):
            return jsonify({"error": "Current password is incorrect"}), 401
        pw_hash = generate_password_hash(new_password)
        cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (pw_hash, user_id))
        conn.commit()
        return jsonify({"message": "Password changed successfully"})
    finally:
        cur.close()
        conn.close()


@app.route("/history", methods=["GET"])
def history():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT role FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        if user["role"] == "doctor":
            cur.execute(
                """
                SELECT
                    p.id, p.entered_by_role, p.scan_type, p.prediction, p.confidence,
                    p.patient_name, p.patient_age, p.patient_sex, p.image_filename,
                    p.created_at, u.email AS uploaded_by
                FROM predictions p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.created_at DESC
                """
            )
        else:
            cur.execute(
                """
                SELECT
                    p.id, p.entered_by_role, p.scan_type, p.prediction, p.confidence,
                    p.patient_name, p.patient_age, p.patient_sex, p.image_filename,
                    p.created_at, u.email AS uploaded_by
                FROM predictions p
                JOIN users u ON p.user_id = u.id
                WHERE p.user_id = %s
                ORDER BY p.created_at DESC
                """,
                (user_id,),
            )
        rows = cur.fetchall()
        for row in rows:
            row["image_url"] = build_image_url(row.get("image_filename"))
        return jsonify(rows)
    finally:
        cur.close()
        conn.close()


@app.route("/uploads/<path:filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/predict", methods=["POST"])
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

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT role FROM users WHERE id = %s", (user_id,))
        uploader = cur.fetchone()
        if not uploader:
            return jsonify({"error": "User not found"}), 404
        entered_by_role = uploader["role"]
    finally:
        cur.close()
        conn.close()

    _, ext = os.path.splitext(original_name)
    saved_filename = f"{uuid.uuid4().hex}{ext.lower()}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)
    file.save(saved_path)
    keep_file = False
    try:
        img = preprocess_image(saved_path)
        if selected_type == "chest":
            pred = CHEST_MODEL.predict(img, verbose=0)
            confidence = float(np.max(pred))
            label = CHEST_CLASSES[np.argmax(pred)]
            result = {"type": "Chest X-ray", "prediction": label, "confidence": round(confidence * 100, 2)}
        elif selected_type == "brain":
            pred = BRAIN_MODEL.predict(img, verbose=0)
            confidence = float(np.max(pred))
            label = BRAIN_CLASSES[np.argmax(pred)]
            result = {"type": "Brain MRI", "prediction": label, "confidence": round(confidence * 100, 2)}
        elif selected_type == "skin":
            pred = SKIN_MODEL.predict(img, verbose=0)
            confidence = float(np.max(pred))
            label = SKIN_CLASSES[np.argmax(pred)]
            result = {"type": "Skin Lesion", "prediction": label, "confidence": round(confidence * 100, 2)}
        else:
            return jsonify({"error": "Invalid type selected"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO predictions (
                    user_id, entered_by_role, scan_type, prediction, confidence,
                    patient_name, patient_age, patient_sex, image_filename
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    entered_by_role,
                    result["type"],
                    result["prediction"],
                    result["confidence"],
                    patient_name,
                    patient_age,
                    patient_sex,
                    saved_filename,
                ),
            )
            conn.commit()
            keep_file = True
        finally:
            cur.close()
            conn.close()

        result["image_url"] = build_image_url(saved_filename)
        return jsonify(result)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    finally:
        if not keep_file and os.path.exists(saved_path):
            os.remove(saved_path)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
