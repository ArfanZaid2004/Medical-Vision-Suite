import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./styles.css";
import Navbar from "./Navbar";
import { readAuthUser } from "./auth";

function UploadPage() {
  const [brainImgMissing, setBrainImgMissing] = useState(false);
  const navigate = useNavigate();
  const user = readAuthUser();

  return (
    <div className="page">
      <div className="shell home-shell">
        <Navbar />
        <section className="hero">
          <div className="main-wrap">
            <div className="hero-content">
              <p className="hero-kicker">Radiology Workflow</p>
              <h1>Welcome {user?.username || "User"}!</h1>
              <p className="subtitle">
                Select a scan type to start a new screening and proceed with patient details.
              </p>
              <div className="hero-tags">
                <span className="hero-tag">Chest X-ray</span>
                <span className="hero-tag">Brain MRI</span>
                <span className="hero-tag">Skin Lesion</span>
              </div>
            </div>
          </div>
        </section>

        <section className="workbench">
          <div className="main-wrap">
            <h2 className="panel-title">Select Scan Type</h2>
            <div className="type-container">
              <button
                type="button"
                className="type-card"
                onClick={() => navigate("/details", { state: { type: "chest" } })}
              >
                <div className="scan-visual chest-visual" aria-hidden="true">
                  <svg viewBox="0 0 80 80" className="scan-svg chest-svg">
                    <rect x="8" y="6" width="64" height="68" rx="8" />
                    <line x1="40" y1="22" x2="40" y2="45" />
                    <path d="M22 22c4 3 8 3 12 0" />
                    <path d="M22 30c4 3 8 3 12 0" />
                    <path d="M22 38c4 3 8 3 12 0" />
                    <path d="M22 46c4 3 8 3 12 0" />
                    <path d="M58 22c-4 3-8 3-12 0" />
                    <path d="M58 30c-4 3-8 3-12 0" />
                    <path d="M58 38c-4 3-8 3-12 0" />
                    <path d="M58 46c-4 3-8 3-12 0" />
                    <path d="M34 52l6-7 6 7" />
                    <line x1="18" y1="60" x2="28" y2="60" />
                    <line x1="18" y1="64" x2="30" y2="64" />
                    <rect x="46" y="57" width="14" height="8" rx="2" />
                  </svg>
                </div>
                <span className="type-icon">CXR</span>
                <span className="type-title">Chest X-ray</span>
                <span className="type-text">Pneumonia and opacity analysis</span>
              </button>

              <button
                type="button"
                className="type-card"
                onClick={() => navigate("/details", { state: { type: "brain" } })}
              >
                <div className="scan-visual brain-visual" aria-hidden="true">
                  {!brainImgMissing ? (
                    <img
                      src="/brain.png"
                      alt=""
                      className="scan-image"
                      onError={() => setBrainImgMissing(true)}
                    />
                  ) : (
                    <svg viewBox="0 0 80 80" className="scan-svg brain-svg">
                      <path d="M40 16c4-5 12-6 17 1 6-2 11 3 10 10 5 4 5 12 0 16 1 7-4 12-11 11-4 6-12 7-16 2-4 5-12 4-16-2-7 1-12-4-11-11-5-4-5-12 0-16-1-7 4-12 10-10 5-7 13-6 17-1z" />
                      <line x1="40" y1="18" x2="40" y2="62" />
                      <path d="M32 26c-4 0-6 3-6 6" />
                      <path d="M30 38c-5 0-7 3-7 6" />
                      <path d="M34 50c-4 0-6 3-6 6" />
                      <path d="M48 26c4 0 6 3 6 6" />
                      <path d="M50 38c5 0 7 3 7 6" />
                      <path d="M46 50c4 0 6 3 6 6" />
                    </svg>
                  )}
                </div>
                <span className="type-icon">MRI</span>
                <span className="type-title">Brain MRI</span>
                <span className="type-text">Tumor screening assistance</span>
              </button>

              <button
                type="button"
                className="type-card"
                onClick={() => navigate("/details", { state: { type: "skin" } })}
              >
                <div className="scan-visual skin-visual" aria-hidden="true">
                  <svg viewBox="0 0 80 80" className="scan-svg skin-svg">
                    <rect x="10" y="10" width="60" height="60" rx="10" />
                    <circle cx="28" cy="30" r="5" />
                    <circle cx="49" cy="28" r="4" />
                    <circle cx="43" cy="44" r="7" />
                    <path d="M22 50c3-4 8-4 11 0" />
                    <path d="M52 52c2-3 6-3 9 0" />
                  </svg>
                </div>
                <span className="type-icon">DERM</span>
                <span className="type-title">Skin Lesion</span>
                <span className="type-text">Dermatology screening support</span>
              </button>
            </div>

            <p className="selection-prompt">
              Choose a scan type to continue to patient details.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}

export default UploadPage;
