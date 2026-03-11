from io import BytesIO

from flask import Blueprint, current_app, jsonify, request, send_file

from core.config import UPLOAD_DIR
from services.report_service import build_pdf_response_payload

report_bp = Blueprint("report_bp", __name__)


@report_bp.route("/report/pdf", methods=["POST"])
def generate_report_pdf():
    payload = request.get_json(silent=True) or {}
    error, pdf_bytes, filename, status = build_pdf_response_payload(
        payload=payload,
        upload_dir=UPLOAD_DIR,
        static_dir=current_app.static_folder,
    )
    if error:
        return jsonify(error), status

    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )
