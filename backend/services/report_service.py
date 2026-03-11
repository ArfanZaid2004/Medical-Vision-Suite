from datetime import datetime

from services.reporting.pdf_builder import build_prediction_report_pdf


def build_pdf_response_payload(payload, upload_dir, static_dir):
    patient = payload.get("patient") or {}
    result = payload.get("result") or {}
    if not result.get("prediction"):
        return {"error": "Missing prediction data"}, None, None, 400

    payload["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf_bytes = build_prediction_report_pdf(
        payload=payload,
        upload_dir=upload_dir,
        static_dir=static_dir,
    )

    scan_type = (result.get("type") or "scan").replace(" ", "_").lower()
    patient_name = (patient.get("name") or "patient").replace(" ", "_").lower()
    filename = f"medical_report_{scan_type}_{patient_name}.pdf"
    return None, pdf_bytes, filename, 200
