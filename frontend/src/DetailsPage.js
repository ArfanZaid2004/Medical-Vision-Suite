import React, { useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Navbar from "./Navbar";
import "./styles.css";
import { useToast } from "./ToastContext";
import { readAuthUser } from "./auth";
import apiClient, { getApiError } from "./apiClient";

function DetailsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const user = readAuthUser();
  const selectedType = location.state?.type;
  const { showToast } = useToast();
  const typeLabels = {
    chest: "Chest X-ray",
    brain: "Brain MRI",
    skin: "Skin Lesion",
  };

  const [file, setFile] = useState(null);
  const [patientName, setPatientName] = useState("");
  const [patientAge, setPatientAge] = useState("");
  const [patientSex, setPatientSex] = useState("");
  const fileInputRef = useRef(null);

  if (!selectedType) {
    navigate("/upload");
    return null;
  }

  const handlePredict = async () => {
    if (!file) {
      showToast("Please upload an image", "warning");
      return;
    }
    if (!patientName || !patientAge || !patientSex) {
      showToast("Please enter patient name, age, and sex", "warning");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("type", selectedType);
    formData.append("user_id", user?.id);
    formData.append("patient_name", patientName);
    formData.append("patient_age", patientAge);
    formData.append("patient_sex", patientSex);

    try {
      const res = await apiClient.post("/predict", formData);
      const nextState = {
        result: res.data,
        image: res.data.image_url || URL.createObjectURL(file),
        patient: {
          name: patientName,
          age: patientAge,
          sex: patientSex,
        },
      };
      sessionStorage.setItem("latest_result_state", JSON.stringify(nextState));
      navigate("/result", {
        state: nextState,
      });
    } catch (err) {
      showToast(getApiError(err, "Prediction failed"), "error");
    }
  };

  const handleReset = () => {
    setFile(null);
    setPatientName("");
    setPatientAge("");
    setPatientSex("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    showToast("Form reset", "info");
  };

  return (
    <div className="page">
      <div className="shell result-shell">
        <Navbar />
        <div className="page-content">
          <div className="result-top">
            <div>
              <h1>Patient Details</h1>
              <p className="subtitle">
                Selected type: {typeLabels[selectedType] || "Unknown"}
              </p>
            </div>
          </div>
          <div className="step-strip">
            <span className="step-pill step-active">1. Patient & Scan</span>
            <span className="step-pill">2. Run Prediction</span>
            <span className="step-pill">3. Review Result</span>
          </div>

          <div className="upload-section">
            <div className="details-grid">
              <div className="details-panel">
                <h3 className="subsection-title">Patient Details</h3>
                <label className="file-label" htmlFor="patient-name">
                  Patient Name
                </label>
                <input
                  id="patient-name"
                  type="text"
                  value={patientName}
                  onChange={(e) => setPatientName(e.target.value)}
                  placeholder="Enter full name"
                />

                <label className="file-label" htmlFor="patient-age">
                  Age
                </label>
                <input
                  id="patient-age"
                  type="number"
                  min="0"
                  value={patientAge}
                  onChange={(e) => setPatientAge(e.target.value)}
                  placeholder="Enter age"
                />

                <label className="file-label" htmlFor="patient-sex">
                  Sex
                </label>
                <select
                  id="patient-sex"
                  value={patientSex}
                  onChange={(e) => setPatientSex(e.target.value)}
                >
                  <option value="">Select sex</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="details-panel">
                <h3 className="subsection-title">Scan Upload</h3>
                <label className="file-label" htmlFor="file-upload">
                  Upload Image
                </label>
                <input
                  ref={fileInputRef}
                  id="file-upload"
                  type="file"
                  accept="image/*"
                  onChange={(e) => setFile(e.target.files[0])}
                />
                <p className="helper-text">
                  {file ? `Selected: ${file.name}` : "No file selected yet"}
                </p>
                <p className="helper-text">
                  Supported: PNG, JPG, JPEG and other image formats.
                </p>
              </div>
            </div>

            <div className="form-actions">
              <button
                type="button"
                className="ghost-btn"
                onClick={() => navigate("/upload")}
              >
                Back
              </button>
              <button type="button" className="ghost-btn" onClick={handleReset}>
                Reset
              </button>
              <button type="button" onClick={handlePredict}>
                Run Prediction
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DetailsPage;
