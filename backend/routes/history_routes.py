from flask import Blueprint, jsonify, send_from_directory, request

from core.config import UPLOAD_DIR
from services.history_service import get_history

history_bp = Blueprint("history_bp", __name__)


@history_bp.route("/history", methods=["GET"])
def history():
    payload, status = get_history(request.args.get("user_id", type=int))
    return jsonify(payload), status


@history_bp.route("/uploads/<path:filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)
