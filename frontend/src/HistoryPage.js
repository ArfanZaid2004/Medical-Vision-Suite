import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./styles.css";
import Navbar from "./Navbar";
import { useToast } from "./ToastContext";
import { readAuthUser } from "./auth";
import apiClient, { getApiError } from "./apiClient";

function HistoryPage() {
  const defaultFilters = {
    diseaseFilter: "all",
    scanTypeFilter: "all",
    nameQuery: "",
    dateFrom: "",
    dateTo: "",
    sortBy: "date_desc",
  };

  const navigate = useNavigate();
  const user = readAuthUser();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [entryLimit, setEntryLimit] = useState(10);
  const [diseaseFilter, setDiseaseFilter] = useState("all");
  const [scanTypeFilter, setScanTypeFilter] = useState("all");
  const [nameQuery, setNameQuery] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [sortBy, setSortBy] = useState("date_desc");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedRow, setSelectedRow] = useState(null);
  const [downloadingRowId, setDownloadingRowId] = useState(null);
  const { showToast } = useToast();

  const getScanTypeKey = (scanType) => {
    const value = (scanType || "").toLowerCase();
    if (value.includes("chest")) return "chest";
    if (value.includes("brain") || value.includes("mri")) return "brain";
    if (value.includes("skin") || value.includes("lesion") || value.includes("derm")) return "skin";
    return "other";
  };

  const diseaseOptions = useMemo(
    () => [
      ...new Set(
        rows
          .filter(
            (row) =>
              scanTypeFilter === "all" ||
              getScanTypeKey(row.scan_type) === scanTypeFilter
          )
          .map((row) => row.prediction)
          .filter(Boolean)
      ),
    ],
    [rows, scanTypeFilter]
  );
  const filteredRows = rows.filter((row) => {
    const matchesDisease = diseaseFilter === "all" || row.prediction === diseaseFilter;
    const matchesScanType = scanTypeFilter === "all" || getScanTypeKey(row.scan_type) === scanTypeFilter;
    const matchesName = (row.patient_name || "")
      .toLowerCase()
      .includes(nameQuery.trim().toLowerCase());

    const createdAtMs = new Date(row.created_at).getTime();
    const fromMs = dateFrom ? new Date(`${dateFrom}T00:00:00`).getTime() : null;
    const toMs = dateTo ? new Date(`${dateTo}T23:59:59`).getTime() : null;
    const matchesDateFrom = fromMs === null || createdAtMs >= fromMs;
    const matchesDateTo = toMs === null || createdAtMs <= toMs;

    return matchesDisease && matchesScanType && matchesName && matchesDateFrom && matchesDateTo;
  });

  const sortedRows = [...filteredRows].sort((a, b) => {
    if (sortBy === "date_desc") {
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    }
    if (sortBy === "date_asc") {
      return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
    }
    if (sortBy === "confidence_desc") {
      return Number(b.confidence) - Number(a.confidence);
    }
    if (sortBy === "confidence_asc") {
      return Number(a.confidence) - Number(b.confidence);
    }
    if (sortBy === "name_desc") {
      return (b.patient_name || "").localeCompare(a.patient_name || "");
    }
    return (a.patient_name || "").localeCompare(b.patient_name || "");
  });

  const totalPages = Math.max(1, Math.ceil(sortedRows.length / entryLimit));
  const currentPageSafe = Math.min(currentPage, totalPages);
  const startIndex = (currentPageSafe - 1) * entryLimit;
  const endIndex = startIndex + entryLimit;
  const visibleRows = sortedRows.slice(startIndex, endIndex);

  const resetFilters = () => {
    setDiseaseFilter(defaultFilters.diseaseFilter);
    setScanTypeFilter(defaultFilters.scanTypeFilter);
    setNameQuery(defaultFilters.nameQuery);
    setDateFrom(defaultFilters.dateFrom);
    setDateTo(defaultFilters.dateTo);
    setSortBy(defaultFilters.sortBy);
    setCurrentPage(1);
  };

  useEffect(() => {
    setCurrentPage(1);
  }, [entryLimit, diseaseFilter, scanTypeFilter, nameQuery, dateFrom, dateTo, sortBy]);

  useEffect(() => {
    if (diseaseFilter !== "all" && !diseaseOptions.includes(diseaseFilter)) {
      setDiseaseFilter("all");
    }
  }, [scanTypeFilter, diseaseFilter, diseaseOptions]);

  useEffect(() => {
    const load = async () => {
      if (!user?.id) {
        navigate("/");
        return;
      }
      try {
        const res = await apiClient.get("/history", {
          params: { user_id: user.id },
        });
        setRows(res.data);
      } catch (err) {
        const message = getApiError(err, "Failed to load history");
        setError(message);
        showToast(message, "error");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [navigate, showToast, user?.id]);

  const handleDownloadPdf = async (row) => {
    setDownloadingRowId(row.id);
    try {
      const response = await apiClient.post(
        "/report/pdf",
        {
          patient: {
            name: row.patient_name || "Unknown",
            age: row.patient_age ?? "-",
            sex: row.patient_sex || "-",
          },
          result: {
            type: row.scan_type || "-",
            prediction: row.prediction || "-",
            confidence: Number(row.confidence) || 0,
          },
          image_url: row.image_url || null,
          gradcam: null,
        },
        { responseType: "blob" }
      );

      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      const safeName = (row.patient_name || "patient").replace(/\s+/g, "_").toLowerCase();
      anchor.href = url;
      anchor.download = `report_${safeName}_${row.id}.pdf`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      showToast(getApiError(err, "Unable to generate PDF report"), "error");
    } finally {
      setDownloadingRowId(null);
    }
  };

  return (
    <div className="page">
      <div className="shell history-shell">
        <Navbar />
        <div className="page-content">
          <div className="result-top">
            <div>
              <h1>Prediction History</h1>
              <p className="subtitle">
                Complete scan prediction records including patient details.
              </p>
            </div>
          </div>
          {!loading && !error && (
            <div className="history-summary">
              <span className="summary-chip">Total records: {rows.length}</span>
              <span className="summary-chip">Filtered: {sortedRows.length}</span>
            </div>
          )}

          {!loading && !error && (
            <div
              className="history-top-filters"
            >
              <div className="history-top-filter-item">
                <label className="history-filter" htmlFor="scan-type-filter">
                  Scan Type
                </label>
                <select
                  id="scan-type-filter"
                  value={scanTypeFilter}
                  onChange={(e) => setScanTypeFilter(e.target.value)}
                >
                  <option value="all">All</option>
                  <option value="chest">Chest X-ray</option>
                  <option value="brain">Brain MRI</option>
                  <option value="skin">Skin Lesion</option>
                </select>
              </div>

              <div className="history-top-filter-item">
                <label className="history-filter" htmlFor="disease-filter">
                  Disease
                </label>
                <select
                  id="disease-filter"
                  value={diseaseFilter}
                  onChange={(e) => setDiseaseFilter(e.target.value)}
                >
                  <option value="all">All</option>
                  {diseaseOptions.map((disease) => (
                    <option key={disease} value={disease}>
                      {disease}
                    </option>
                  ))}
                </select>
              </div>

              <div className="history-top-filter-item">
                <label className="history-filter" htmlFor="name-search">
                  Search Name
                </label>
                <input
                  id="name-search"
                  type="text"
                  placeholder="Enter patient name"
                  value={nameQuery}
                  onChange={(e) => setNameQuery(e.target.value)}
                />
              </div>

              <div className="history-top-filter-item">
                <label className="history-filter" htmlFor="date-from">
                  Date From
                </label>
                <input
                  id="date-from"
                  type="date"
                  placeholder="yyyy-mm-dd"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                />
              </div>

              <div className="history-top-filter-item">
                <label className="history-filter" htmlFor="date-to">
                  Date To
                </label>
                <input
                  id="date-to"
                  type="date"
                  placeholder="yyyy-mm-dd"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                />
              </div>

              <div className="history-top-filter-item">
                <label className="history-filter" htmlFor="sort-by">
                  Sort By
                </label>
                <select
                  id="sort-by"
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                >
                  <option value="date_desc">Date: Newest first</option>
                  <option value="date_asc">Date: Oldest first</option>
                  <option value="confidence_desc">Confidence: High to low</option>
                  <option value="confidence_asc">Confidence: Low to high</option>
                  <option value="name_asc">Name: A to Z</option>
                  <option value="name_desc">Name: Z to A</option>
                </select>
              </div>

              <div className="history-top-filter-item history-top-filter-actions">
                <button type="button" className="ghost-btn" onClick={resetFilters}>
                  Reset
                </button>
              </div>
            </div>
          )}
          {loading && <p className="subtitle">Loading history...</p>}
          {error && <p className="subtitle">Unable to load history records.</p>}

          {!loading && !error && (
            <div className="history-area">
              <div className="history-table-wrap">
                <table className="history-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Patient</th>
                      <th>Scan</th>
                      <th>Prediction</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedRows.length === 0 && (
                      <tr>
                        <td colSpan="5">No predictions found for the selected filters.</td>
                      </tr>
                    )}
                    {visibleRows.map((row) => (
                      <tr key={row.id}>
                        <td>{new Date(row.created_at).toLocaleString()}</td>
                        <td>{row.patient_name}</td>
                        <td>{row.scan_type}</td>
                        <td>{row.prediction}</td>
                        <td>
                          <div className="history-action-buttons">
                            <button
                              type="button"
                              className="ghost-btn"
                              onClick={() => setSelectedRow(row)}
                            >
                              View
                            </button>
                            <button
                              type="button"
                              className="ghost-btn"
                              onClick={() => handleDownloadPdf(row)}
                              disabled={downloadingRowId === row.id}
                              title="Download Report"
                              aria-label="Download Report"
                            >
                              {downloadingRowId === row.id ? "... Preparing" : "↓ Download"}
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="history-controls history-controls-bottom">
                <p className="helper-text">
                  Showing {sortedRows.length === 0 ? 0 : startIndex + 1}-{Math.min(endIndex, sortedRows.length)} of {sortedRows.length} filtered entries
                </p>
                <button
                  type="button"
                  className="ghost-btn"
                  onClick={() => navigate("/upload")}
                >
                  Back
                </button>
                <label className="history-filter" htmlFor="entry-limit">
                  Show entries
                </label>
                <select
                  id="entry-limit"
                  value={entryLimit}
                  onChange={(e) => setEntryLimit(Number(e.target.value))}
                >
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
                <button
                  type="button"
                  className="ghost-btn"
                  onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                  disabled={currentPageSafe <= 1}
                >
                  Prev
                </button>
                <span className="history-page-indicator">
                  Page {currentPageSafe} of {totalPages}
                </span>
                <button
                  type="button"
                  className="ghost-btn"
                  onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                  disabled={currentPageSafe >= totalPages}
                >
                  Next
                </button>
              </div>
            </div>
          )}

          {selectedRow && (
            <div className="history-details-overlay" onClick={() => setSelectedRow(null)}>
              <div
                className="history-details-card"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="history-details-head">
                  <h3>Prediction Details</h3>
                  <button
                    type="button"
                    className="ghost-btn"
                    onClick={() => setSelectedRow(null)}
                  >
                    Close
                  </button>
                </div>
                <div className="history-details-grid">
                  <p><strong>Date:</strong> {new Date(selectedRow.created_at).toLocaleString()}</p>
                  <p><strong>Patient:</strong> {selectedRow.patient_name}</p>
                  <p><strong>Age:</strong> {selectedRow.patient_age}</p>
                  <p><strong>Sex:</strong> {selectedRow.patient_sex}</p>
                  <p><strong>Scan:</strong> {selectedRow.scan_type}</p>
                  <p><strong>Prediction:</strong> {selectedRow.prediction}</p>
                  <p><strong>Confidence:</strong> {selectedRow.confidence}%</p>
                  <p><strong>Entered By:</strong> {selectedRow.entered_by_role}</p>
                  <p><strong>Uploaded By:</strong> {selectedRow.uploaded_by}</p>
                </div>
                {selectedRow.image_url && (
                  <div className="history-details-image-wrap">
                    <img src={selectedRow.image_url} alt="Scan detail" className="history-details-image" />
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default HistoryPage;
