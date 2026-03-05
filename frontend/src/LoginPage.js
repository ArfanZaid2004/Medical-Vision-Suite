import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import API_BASE_URL from "./api";
import "./styles.css";
import { useToast } from "./ToastContext";
import { writeAuthUser } from "./auth";

function LoginPage() {
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState("technician");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { showToast } = useToast();

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (mode === "register") {
        if (password !== confirmPassword) {
          showToast("Passwords do not match", "warning");
          return;
        }

        await axios.post(`${API_BASE_URL}/auth/register`, {
          username,
          email,
          password,
          role,
        });
        showToast("Account created. You can now log in.", "success");
        setConfirmPassword("");
        setMode("login");
      } else {
        const res = await axios.post(`${API_BASE_URL}/auth/login`, {
          email,
          password,
        });
        writeAuthUser(res.data.user);
        navigate("/upload");
      }
    } catch (err) {
      showToast(err?.response?.data?.error || "Request failed", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page auth-page">
      <div className="shell auth-shell">
        <div className="auth-card auth-simple">
          <div className="auth-login-brand">
            <p className="auth-login-title">Medical Vision Suite</p>
          </div>
          <h1>{mode === "login" ? "Sign in" : "Create account"}</h1>
          <p className="subtitle">
            {mode === "login"
              ? "Access the screening workspace."
              : "Create an account to continue."}
          </p>
          <div className="auth-points">
            <span>Multi-model screening</span>
            <span>Role-based access</span>
            <span>Prediction history</span>
          </div>

          <form onSubmit={submit} className="auth-form">
            <label className="file-label" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            {mode === "register" && (
              <>
                <label className="file-label" htmlFor="username">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  minLength={3}
                />

                <label className="file-label" htmlFor="role">
                  Role
                </label>
                <select
                  id="role"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                >
                  <option value="technician">Technician</option>
                    <option value="doctor">Doctor</option>
                  </select>
              </>
            )}

            <label className="file-label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />

            {mode === "register" && (
              <>

                <label className="file-label" htmlFor="confirm-password">
                  Confirm Password
                </label>
                <input
                  id="confirm-password"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  minLength={6}
                />
              </>
            )}

            <button type="submit" disabled={loading}>
              {loading
                ? "Please wait..."
                : mode === "login"
                  ? "Sign in"
                  : "Create account"}
            </button>
          </form>

          <button
            type="button"
            className="ghost-btn auth-toggle"
            onClick={() => {
              setConfirmPassword("");
              setUsername("");
              setRole("technician");
              setMode(mode === "login" ? "register" : "login");
            }}
          >
            {mode === "login"
              ? "Need an account? Register"
              : "Already have an account? Sign in"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
