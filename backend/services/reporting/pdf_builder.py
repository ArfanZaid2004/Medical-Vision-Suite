from datetime import datetime
from io import BytesIO
import os
from urllib.parse import unquote, urlparse

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def _resolve_local_path(url_or_path, upload_dir, static_dir):
    if not url_or_path:
        return None
    if os.path.isabs(url_or_path) and os.path.exists(url_or_path):
        return url_or_path

    parsed = urlparse(url_or_path)
    raw_path = unquote(parsed.path or url_or_path)

    if raw_path.startswith("/uploads/"):
        filename = raw_path.split("/uploads/", 1)[1]
        candidate = os.path.join(upload_dir, filename)
        return candidate if os.path.exists(candidate) else None

    if raw_path.startswith("/static/"):
        rel = raw_path.split("/static/", 1)[1]
        candidate = os.path.join(static_dir, rel)
        return candidate if os.path.exists(candidate) else None

    candidate = os.path.join(upload_dir, os.path.basename(raw_path))
    if os.path.exists(candidate):
        return candidate
    return None


def _confidence_theme(confidence):
    if not isinstance(confidence, (int, float)):
        return ("Unknown", colors.HexColor("#64748B"), colors.HexColor("#F1F5F9"))
    if confidence >= 90:
        return ("High", colors.HexColor("#166534"), colors.HexColor("#DCFCE7"))
    if confidence >= 70:
        return ("Moderate", colors.HexColor("#92400E"), colors.HexColor("#FEF3C7"))
    return ("Low", colors.HexColor("#991B1B"), colors.HexColor("#FEE2E2"))


def _disease_summary(scan_type, prediction):
    scan_key = (scan_type or "").lower()
    pred = (prediction or "").lower()

    summaries = {
        "brain": {
            "glioma": "Pattern suggests glioma-like features on MRI. Recommend neurologic and radiologic correlation.",
            "meningioma": "Pattern is consistent with meningioma-like morphology. Correlate with lesion location and clinical findings.",
            "pituitary": "Findings resemble pituitary-region tumor pattern. Endocrine and neuro-ophthalmic assessment may be useful.",
            "no tumor": "No major tumor-like pattern detected in this scan. Formal specialist review is still recommended.",
        },
        "skin": {
            "melanoma": "Lesion appears suspicious for melanoma-like features. Urgent dermatology review is advised.",
            "melanocytic nevi": "Lesion is more consistent with nevus-like benign pattern. Monitor for evolution over time.",
            "basal cell carcinoma": "Pattern resembles basal cell carcinoma-like lesion. Clinical exam and biopsy confirmation are advised.",
            "benign keratosis": "Pattern is compatible with benign keratosis-like features, though clinical confirmation remains important.",
        },
        "chest": {
            "pneumonia": "CXR pattern suggests pneumonia-like opacity. Correlate with symptoms, vitals, and inflammatory markers.",
            "pneumothorax": "Features are compatible with possible pneumothorax. Assess urgency clinically and confirm with radiology.",
            "tuberculosis": "Pattern may indicate tuberculosis-related pulmonary changes. Correlate with microbiology and history.",
            "covid": "Findings are compatible with COVID-like pulmonary involvement. Clinical and lab correlation is recommended.",
            "normal": "No major abnormal thoracic pattern is detected by the model in this image.",
        },
    }

    if "brain" in scan_key or "mri" in scan_key:
        for key, value in summaries["brain"].items():
            if key in pred:
                return value
    elif "skin" in scan_key or "lesion" in scan_key or "derm" in scan_key:
        for key, value in summaries["skin"].items():
            if key in pred:
                return value
    elif "chest" in scan_key or "x-ray" in scan_key or "xray" in scan_key:
        for key, value in summaries["chest"].items():
            if key in pred:
                return value

    return "Model output should be interpreted with complete clinical history and specialist review."


def _draw_wrapped_text(pdf, text, x, y, max_width, line_height=12):
    words = str(text or "").split()
    if not words:
        return y
    line = words[0]
    current_y = y
    for word in words[1:]:
        test = f"{line} {word}"
        if pdf.stringWidth(test, "Helvetica", 10) <= max_width:
            line = test
        else:
            pdf.drawString(x, current_y, line)
            current_y -= line_height
            line = word
    pdf.drawString(x, current_y, line)
    return current_y - line_height


def _draw_logo_mark(pdf, x, y, size, color=colors.white):
    """
    Draws a plus-style Medical Vision mark.
    x, y represent the lower-left point of the mark bounding box.
    """
    arm = size * 0.36
    radius = size * 0.12
    pdf.setFillColor(color)
    # Center both bars to form a symmetric medical plus mark.
    pdf.roundRect(x + ((size - arm) / 2), y, arm, size, radius, stroke=0, fill=1)
    pdf.roundRect(x, y + ((size - arm) / 2), size, arm, radius, stroke=0, fill=1)


def build_prediction_report_pdf(payload, upload_dir, static_dir):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 36
    content_w = width - (2 * margin)
    y = height - margin

    generated_at = payload.get("generated_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_id = payload.get("report_id") or f"MVS-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    patient = payload.get("patient", {})
    result = payload.get("result", {})
    confidence = result.get("confidence")
    conf_level, conf_text, conf_bg = _confidence_theme(confidence)
    note_text = _disease_summary(result.get("type"), result.get("prediction"))

    summary_lines = [
        ("Patient Name", patient.get("name", "-")),
        ("Patient Age", str(patient.get("age", "-"))),
        ("Patient Sex", patient.get("sex", "-")),
        ("Scan Type", result.get("type", "-")),
        ("Prediction", result.get("prediction", "-")),
        ("Confidence", f'{result.get("confidence", "-")}%' if result.get("confidence") is not None else "-"),
    ]

    # Header band
    header_h = 74
    pdf.setFillColor(colors.HexColor("#0C4A6E"))
    pdf.roundRect(margin, y - header_h, content_w, header_h, 10, stroke=0, fill=1)

    # Brand mark
    logo_size = 38
    logo_x = margin + 14
    logo_y = y - header_h + ((header_h - logo_size) / 2)
    _draw_logo_mark(pdf, logo_x, logo_y, logo_size, color=colors.white)

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(logo_x + logo_size + 12, y - 28, "Medical Vision Suite")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(logo_x + logo_size + 12, y - 46, "AI Clinical Diagnosis Report")
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString(margin + content_w - 16, y - 28, f"Generated: {generated_at}")
    pdf.drawRightString(margin + content_w - 16, y - 44, f"Report ID: {report_id}")
    y -= (header_h + 18)

    # Patient and prediction summary card
    card_h = 170
    pdf.setFillColor(colors.HexColor("#F8FAFC"))
    pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
    pdf.roundRect(margin, y - card_h, content_w, card_h, 10, stroke=1, fill=1)

    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(margin + 14, y - 24, "Clinical Summary")

    col1_x = margin + 14
    col2_x = margin + content_w / 2 + 10
    line_y = y - 46
    for idx, (label, value) in enumerate(summary_lines):
        x = col1_x if idx < 3 else col2_x
        if idx == 3:
            line_y = y - 46
        pdf.setFillColor(colors.HexColor("#334155"))
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(x, line_y, f"{label}:")
        pdf.setFillColor(colors.HexColor("#111827"))
        pdf.setFont("Helvetica", 11)
        pdf.drawString(x + 78, line_y, str(value))
        line_y -= 24

    # Confidence badge
    badge_text = f"Model confidence: {confidence:.2f}%" if isinstance(confidence, (int, float)) else "Model confidence: -"
    badge_w = 176
    badge_h = 22
    badge_x = margin + content_w - badge_w - 14
    badge_y = y - card_h + 14
    pdf.setFillColor(conf_bg)
    pdf.setStrokeColor(conf_text)
    pdf.roundRect(badge_x, badge_y, badge_w, badge_h, 8, stroke=1, fill=1)
    pdf.setFillColor(conf_text)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(badge_x + (badge_w / 2), badge_y + 7, f"{badge_text} ({conf_level})")
    y -= (card_h + 18)

    # Assessment callout
    finding_h = 62
    pdf.setFillColor(colors.HexColor("#F8FAFC"))
    pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
    pdf.roundRect(margin, y - finding_h, content_w, finding_h, 8, stroke=1, fill=1)
    pdf.setFillColor(colors.HexColor("#334155"))
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(margin + 12, y - 20, "KEY FINDING")
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(margin + 12, y - 42, str(result.get("prediction", "-")))
    y -= (finding_h + 14)

    # Short disease interpretation note
    note_h = 56
    pdf.setFillColor(colors.HexColor("#F8FAFC"))
    pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
    pdf.roundRect(margin, y - note_h, content_w, note_h, 8, stroke=1, fill=1)
    pdf.setFillColor(colors.HexColor("#334155"))
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(margin + 12, y - 18, "CLINICAL SUMMARY NOTE")
    pdf.setFillColor(colors.HexColor("#1F2937"))
    pdf.setFont("Helvetica", 10)
    _draw_wrapped_text(pdf, note_text, margin + 12, y - 34, content_w - 24, line_height=11)
    y -= (note_h + 12)

    image_url = payload.get("image_url")
    gradcam_url = payload.get("gradcam")
    image_path = _resolve_local_path(image_url, upload_dir, static_dir)
    gradcam_path = _resolve_local_path(gradcam_url, upload_dir, static_dir)

    if image_path or gradcam_path:
        pdf.setFillColor(colors.HexColor("#0F172A"))
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(margin, y, "Visual Evidence")
        y -= 12

    block_top = y - 10
    panel_w = (content_w - 12) / 2
    panel_h = 230
    img_pad = 10
    cap_h = 20
    img_x1 = margin
    img_x2 = margin + panel_w + 12

    if image_path:
        try:
            pdf.setFillColor(colors.white)
            pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
            pdf.roundRect(img_x1, block_top - panel_h, panel_w, panel_h, 8, stroke=1, fill=1)
            pdf.setFillColor(colors.HexColor("#1E293B"))
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(img_x1 + img_pad, block_top - 16, "Uploaded Scan")

            target_w = panel_w - (2 * img_pad)
            target_h = panel_h - cap_h - (2 * img_pad)
            pdf.drawImage(
                ImageReader(image_path),
                img_x1 + img_pad,
                block_top - panel_h + img_pad,
                width=target_w,
                height=target_h,
                preserveAspectRatio=True,
                anchor="c",
            )
        except Exception:
            pass

    if gradcam_path:
        try:
            pdf.setFillColor(colors.white)
            pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
            pdf.roundRect(img_x2, block_top - panel_h, panel_w, panel_h, 8, stroke=1, fill=1)
            pdf.setFillColor(colors.HexColor("#1E293B"))
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(img_x2 + img_pad, block_top - 16, "Grad-CAM Heatmap")

            target_w = panel_w - (2 * img_pad)
            target_h = panel_h - cap_h - (2 * img_pad)
            pdf.drawImage(
                ImageReader(gradcam_path),
                img_x2 + img_pad,
                block_top - panel_h + img_pad,
                width=target_w,
                height=target_h,
                preserveAspectRatio=True,
                anchor="c",
            )
        except Exception:
            pass

    # Footer note
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 8)
    pdf.drawString(
        margin,
        24,
        "For project demonstration only. This report does not replace clinical diagnosis by a licensed physician.",
    )

    pdf.showPage()
    pdf.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
