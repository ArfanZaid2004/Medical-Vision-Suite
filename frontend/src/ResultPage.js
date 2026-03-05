import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./styles.css";
import Navbar from "./Navbar";

function ResultPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const goHome = () => navigate("/upload");
  const safeConfidence = location.state
    ? Math.max(0, Math.min(100, Number(location.state.result.confidence) || 0))
    : 0;

  if (!location.state) {
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

  const { result, image } = location.state;
  const severity = safeConfidence >= 75 ? "High Confidence" : safeConfidence >= 45 ? "Moderate Confidence" : "Low Confidence";

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
              <img src={image} alt="uploaded" className="preview" />
            </div>

            <div className="result-summary result-summary-center result-panel">
              <div className="result-meta-row">
                <div className="result-title">{result.type} scan</div>
                <span className="result-chip">AI output</span>
              </div>
              <h2 className="result-prediction">{result.prediction}</h2>
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
