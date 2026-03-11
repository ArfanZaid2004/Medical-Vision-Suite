import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./styles.css";
import Navbar from "./Navbar";
import API_BASE_URL from "./api";
import apiClient, { getApiError } from "./apiClient";
import { useToast } from "./ToastContext";

function ResultPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [downloading, setDownloading] = useState(false);
  const { showToast } = useToast();
  const goHome = () => navigate("/upload");
  const storedState = (() => {
    try {
      const raw = sessionStorage.getItem("latest_result_state");
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  })();
  const resolvedState = location.state || storedState;
  const safeConfidence = resolvedState
    ? Math.max(0, Math.min(100, Number(resolvedState.result.confidence) || 0))
    : 0;

  if (!resolvedState) {
    return (
      <div className="page">
        <div className="shell result-shell result-empty">
          <Navbar />
          <div className="page-content">
            <h1>Prediction Result</h1>
            <p className="subtitle">No result is available right now.</p>
            <button onClick={goHome}>Back to Upload</button>
          </div>
        </div>
      </div>
    );
  }

  const { result, image, patient } = resolvedState;
  const previewImage = image || result?.image_url;
  const gradcamImage = result?.gradcam_url
    ? result.gradcam_url
    : result?.gradcam
    ? result.gradcam.startsWith("http")
      ? result.gradcam
      : `${API_BASE_URL}${result.gradcam}`
    : null;
  const severity = safeConfidence >= 75 ? "High Confidence" : safeConfidence >= 45 ? "Moderate Confidence" : "Low Confidence";

  const getDiseaseSummary = (scanType, prediction) => {
    const scan = (scanType || "").toLowerCase();
    const pred = (prediction || "").toLowerCase();
    const notes = {
      brain: [
        ["glioma", "Glioma-like MRI pattern detected. Correlate with neurological findings and specialist review."],
        ["meningioma", "Meningioma-like pattern detected. Recommend radiologist confirmation and clinical correlation."],
        ["pituitary", "Pituitary-region tumor pattern detected. Endocrine and vision-related assessment may be needed."],
        ["no tumor", "No tumor-like pattern detected by the model in this MRI image."],
      ],
      skin: [
        ["melanoma", "Lesion appears suspicious for melanoma-like features. Prompt dermatology review is advised."],
        ["melanocytic nevi", "Lesion appears closer to nevus-like benign pattern. Monitor for visible changes over time."],
        ["basal cell carcinoma", "Pattern resembles basal cell carcinoma-like features. Clinical confirmation is recommended."],
        ["benign keratosis", "Pattern is consistent with benign keratosis-like lesion characteristics."],
      ],
      chest: [
        ["pneumonia", "Chest X-ray suggests pneumonia-like opacity. Correlate with symptoms and infection markers."],
        ["pneumothorax", "Possible pneumothorax-like pattern detected. Assess urgency with immediate clinical context."],
        ["tuberculosis", "Pattern may indicate tuberculosis-related lung changes. Confirm with clinical testing."],
        ["covid", "Image shows COVID-like pulmonary involvement pattern; correlate with laboratory and clinical data."],
        ["normal", "No major thoracic abnormality pattern is detected by the model in this scan."],
      ],
    };

    const group = scan.includes("brain")
      ? notes.brain
      : scan.includes("skin")
      ? notes.skin
      : notes.chest;
    const found = group.find(([key]) => pred.includes(key));
    return found ? found[1] : "Model output should be interpreted with full clinical context and specialist review.";
  };
  const summaryNote = getDiseaseSummary(result.type, result.prediction);

  const handleDownloadPdf = async () => {
    setDownloading(true);
    try {
      const response = await apiClient.post(
        "/report/pdf",
        {
          patient: {
            name: patient?.name || "Unknown",
            age: patient?.age || "-",
            sex: patient?.sex || "-",
          },
          result: {
            type: result?.type,
            prediction: result?.prediction,
            confidence: safeConfidence,
          },
          image_url: result?.image_url || image,
          gradcam: result?.gradcam || null,
        },
        { responseType: "blob" }
      );

      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "medical_report.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      showToast(getApiError(err, "Unable to generate PDF report"), "error");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="page">
      <div className="shell result-shell">
        <Navbar />
        <div className="page-content">
          <div className="result-top">
            <div>
              <h1>Prediction Result</h1>
              <p className="subtitle">
                Review model output for the uploaded scan.
              </p>
            </div>
            <button className="ghost-btn" onClick={goHome}>
              New Scan
            </button>
          </div>

          <div className="result-grid result-grid-refined">
            <div className="result-image-wrap result-image-top result-panel">
              <div className={`preview-pair ${gradcamImage ? "with-gradcam" : ""}`}>
                <div className="preview-tile">
                  <p className="preview-label">Uploaded Image</p>
                  <img src={previewImage} alt="uploaded" className="preview" />
                </div>
                {gradcamImage && (
                  <div className="preview-tile">
                    <p className="preview-label">Grad-CAM Heatmap</p>
                    <img src={gradcamImage} alt="gradcam heatmap" className="preview" />
                  </div>
                )}
              </div>
              {!gradcamImage && (
                <p className="helper-text" style={{ marginTop: 10 }}>
                  Grad-CAM not available for this result.
                  {result?.gradcam_error ? ` (${result.gradcam_error})` : ""}
                </p>
              )}
            </div>

            <div className="result-summary result-summary-center result-panel">
              <div className="result-meta-row">
                <div className="result-title">{result.type} scan</div>
                <span className="result-chip">AI output</span>
              </div>
              <h2 className="result-prediction">{result.prediction}</h2>
              <p className="helper-text" style={{ marginTop: 6 }}>
                {summaryNote}
              </p>
              <p className="result-severity">{severity}</p>
              <div className="result-facts">
                <span className="fact-chip">{result.type}</span>
                <span className="fact-chip">{severity}</span>
              </div>
              <div className="confidence-row">
                <span className="confidence-label">Confidence</span>
                <span className="confidence">{safeConfidence}%</span>
              </div>
              <div
                className="meter"
                style={{ "--confidence": `${safeConfidence}%` }}
              >
                <span className="meter-fill" />
                <span className="meter-indicator" />
              </div>
              <div className="result-actions">
                <button className="ghost-btn" onClick={() => navigate(-1)}>
                  Back
                </button>
                <button
                  className="ghost-btn"
                  onClick={handleDownloadPdf}
                  disabled={downloading}
                >
                  {downloading ? "Preparing PDF..." : "Download PDF"}
                </button>
                <button className="result-btn" onClick={goHome}>
                  Try Another Image
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResultPage;
