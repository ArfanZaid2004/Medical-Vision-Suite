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
                Start a new clinical screening by selecting a scan type and entering patient details.
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
            <div className="section-shell">
              <div className="section-head">
                <h2 className="panel-title">Select Scan Type</h2>
                <span className="section-head-chip">Step 1 of 3</span>
              </div>
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
                  <span className="type-text">Pneumonia, pneumothorax, TB and other thoracic findings.</span>
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
                  <span className="type-text">Glioma, meningioma, pituitary and no-tumor classification.</span>
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
                  <span className="type-text">Melanoma and benign lesion risk screening support.</span>
                </button>
              </div>

              <p className="selection-prompt">
                Choose a scan type to continue to patient details.
              </p>
            </div>
          </div>
        </section>

        <section className="disease-info">
          <div className="main-wrap">
            <div className="section-shell">
              <div className="section-head">
                <h2 className="panel-title">Disease Information</h2>
                <span className="section-head-chip">Clinical reference</span>
              </div>
              <div className="disease-grid">
              <article className="disease-card">
                <p className="disease-chip">Brain MRI</p>
                <div className="disease-visual">
                  <div className="disease-icon" aria-hidden="true">MRI</div>
                  <div className="disease-meters">
                    <div className="disease-meter-row">
                      <span>Urgency</span>
                      <div className="disease-meter"><i style={{ width: "74%" }} /></div>
                    </div>
                    <div className="disease-meter-row">
                      <span>Complexity</span>
                      <div className="disease-meter"><i style={{ width: "82%" }} /></div>
                    </div>
                  </div>
                </div>
                <h3>Brain Tumor Screening</h3>
                <p>
                  Classifies MRI scans into common brain tumor categories.
                </p>
                <ul className="disease-list">
                  <li><strong>Glioma:</strong> Gliomas arise from glial support cells in the brain and can appear as irregular infiltrative lesions on MRI. Depending on grade and location, they may affect speech, motor function, memory, or behavior and usually require specialist follow-up.</li>
                  <li><strong>Meningioma:</strong> Meningiomas develop from the meninges, the protective membranes around the brain and spinal cord. They are often slow-growing and may remain asymptomatic for long periods, but larger tumors can cause pressure-related symptoms and need clinical monitoring or treatment.</li>
                  <li><strong>Pituitary:</strong> Pituitary tumors occur near the pituitary gland at the base of the brain and may alter hormone production. Patients can present with endocrine symptoms, headaches, or visual field changes due to compression of nearby structures.</li>
                  <li><strong>No Tumor:</strong> This class indicates that no clear tumor-like MRI pattern was identified by the model in the submitted image. It does not replace radiologist review and should be interpreted alongside clinical history and full imaging context.</li>
                </ul>
                <div className="disease-signs">
                  <span>Headache</span>
                  <span>Seizures</span>
                  <span>Vision changes</span>
                  <span>Neurologic deficit</span>
                </div>
                <div className="disease-alert">
                  Refer urgently if acute neurologic symptoms are progressive or new onset.
                </div>
                <p className="disease-note">Typical symptoms: headache, seizures, vision changes.</p>
              </article>

              <article className="disease-card">
                <p className="disease-chip">Skin Lesion</p>
                <div className="disease-visual">
                  <div className="disease-icon" aria-hidden="true">DERM</div>
                  <div className="disease-meters">
                    <div className="disease-meter-row">
                      <span>Urgency</span>
                      <div className="disease-meter"><i style={{ width: "66%" }} /></div>
                    </div>
                    <div className="disease-meter-row">
                      <span>Complexity</span>
                      <div className="disease-meter"><i style={{ width: "70%" }} /></div>
                    </div>
                  </div>
                </div>
                <h3>Skin Disease Detection</h3>
                <p>
                  Evaluates lesion images for malignant and benign skin patterns.
                </p>
                <ul className="disease-list">
                  <li><strong>Melanoma:</strong> Melanoma is a high-risk skin cancer that can spread quickly if not diagnosed early. Suspicious lesions often show asymmetry, irregular border, color variation, and progressive size or texture change over time.</li>
                  <li><strong>Melanocytic Nevi (NV):</strong> Melanocytic nevi are common pigmented moles and are usually benign. Stable shape and color are reassuring, but rapid evolution or atypical features should still be evaluated by a dermatologist.</li>
                  <li><strong>Basal Cell Carcinoma:</strong> Basal cell carcinoma is the most frequent skin cancer and generally grows slowly with low metastatic risk. It can appear as pearly, ulcerated, or non-healing lesions and typically requires local treatment.</li>
                  <li><strong>Benign Keratosis:</strong> Benign keratosis includes non-cancerous keratotic lesions, often related to age or chronic sun exposure. Although typically harmless, visual similarity with malignant lesions means uncertain cases should be clinically confirmed.</li>
                </ul>
                <div className="disease-signs">
                  <span>Asymmetry</span>
                  <span>Border irregularity</span>
                  <span>Color variation</span>
                  <span>Diameter growth</span>
                </div>
                <div className="disease-alert">
                  Refer if the lesion evolves rapidly, bleeds, or has multiple atypical features.
                </div>
                <p className="disease-note">Check changes in color, border, size, or texture.</p>
              </article>

              <article className="disease-card">
                <p className="disease-chip">Chest X-ray</p>
                <div className="disease-visual">
                  <div className="disease-icon" aria-hidden="true">CXR</div>
                  <div className="disease-meters">
                    <div className="disease-meter-row">
                      <span>Urgency</span>
                      <div className="disease-meter"><i style={{ width: "78%" }} /></div>
                    </div>
                    <div className="disease-meter-row">
                      <span>Complexity</span>
                      <div className="disease-meter"><i style={{ width: "64%" }} /></div>
                    </div>
                  </div>
                </div>
                <h3>Thoracic Disease Analysis</h3>
                <p>
                  Detects key chest X-ray classes used in respiratory screening.
                </p>
                <ul className="disease-list">
                  <li><strong>Pneumonia:</strong> Pneumonia represents infection-related inflammation in the lungs and commonly appears as focal or diffuse opacities on chest X-ray. Clinical correlation with fever, cough, and oxygen status is important for severity assessment.</li>
                  <li><strong>Pneumothorax:</strong> Pneumothorax occurs when air enters the pleural space, causing partial or complete lung collapse. It may present suddenly with chest pain and breathlessness and can require urgent intervention depending on extent.</li>
                  <li><strong>Tuberculosis:</strong> Pulmonary tuberculosis is a chronic infectious disease that can produce upper-zone infiltrates, fibrosis, or cavitary changes. Imaging findings should be interpreted with microbiology tests and clinical history.</li>
                  <li><strong>COVID:</strong> COVID-related chest findings often overlap with viral pneumonia patterns, including bilateral patchy or interstitial opacities. Radiographic appearance alone is not definitive and should be combined with lab and symptom data.</li>
                  <li><strong>Normal:</strong> The normal class suggests no major visible abnormal pattern in the uploaded X-ray according to the model. Subtle findings may still be present, so formal medical interpretation remains necessary.</li>
                </ul>
                <div className="disease-signs">
                  <span>Cough</span>
                  <span>Fever</span>
                  <span>Chest pain</span>
                  <span>Breathlessness</span>
                </div>
                <div className="disease-alert">
                  Refer immediately if respiratory distress or low oxygen saturation is present.
                </div>
                <p className="disease-note">Look for cough, fever, chest pain, and breathing difficulty.</p>
              </article>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default UploadPage;
