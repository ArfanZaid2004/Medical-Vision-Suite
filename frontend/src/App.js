import React, { useEffect, useLayoutEffect, useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useLocation,
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
  const location = useLocation();
  const [displayLocation, setDisplayLocation] = useState(location);
  const [transitionStage, setTransitionStage] = useState("fade-in");

  useEffect(() => {
    if (location.pathname !== displayLocation.pathname) {
      setTransitionStage("fade-out");
      const timeout = setTimeout(() => {
        setDisplayLocation(location);
        setTransitionStage("fade-in");
      }, 120);
      return () => clearTimeout(timeout);
    }
    return undefined;
  }, [location, displayLocation]);

  useLayoutEffect(() => {
    window.scrollTo(0, 0);
  }, [displayLocation.pathname]);

  return (
    <div className={`route-stage route-${transitionStage}`}>
      <Routes location={displayLocation}>
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
    </div>
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
