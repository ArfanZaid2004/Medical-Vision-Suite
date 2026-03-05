import React, { useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import UploadPage from "./UploadPage";
import DetailsPage from "./DetailsPage";
import ResultPage from "./ResultPage";
import LoginPage from "./LoginPage";
import HistoryPage from "./HistoryPage";
import { ToastProvider } from "./ToastContext";
import { clearAuthUser, readAuthUser } from "./auth";

function ProtectedRoute({ children }) {
  const user = readAuthUser();
  if (!user) return <Navigate to="/" replace />;
  return children;
}

function PublicOnlyRoute({ children }) {
  const user = readAuthUser();
  if (user) return <Navigate to="/upload" replace />;
  return children;
}

function AnimatedRoutes() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <PublicOnlyRoute>
            <LoginPage />
          </PublicOnlyRoute>
        }
      />
      <Route
        path="/upload"
        element={
          <ProtectedRoute>
            <UploadPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/details"
        element={
          <ProtectedRoute>
            <DetailsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/result"
        element={
          <ProtectedRoute>
            <ResultPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/history"
        element={
          <ProtectedRoute>
            <HistoryPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  useEffect(() => {
    // Clear any invalid auth state on startup.
    if (!readAuthUser()) {
      clearAuthUser();
    }
  }, []);

  return (
    <ToastProvider>
      <Router>
        <AnimatedRoutes />
      </Router>
    </ToastProvider>
  );
}

export default App;
