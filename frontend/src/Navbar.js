import React, { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { clearAuthUser, readAuthUser, writeAuthUser } from "./auth";
import { useToast } from "./ToastContext";
import apiClient, { getApiError } from "./apiClient";

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const user = readAuthUser();
  const role = user?.role || "user";
  const displayName = user?.username || user?.email || "Account";
  const avatarSeed = (displayName || "A").trim().charAt(0).toUpperCase();
  const roleLabel = role.charAt(0).toUpperCase() + role.slice(1);
  const menuRef = useRef(null);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [profileForm, setProfileForm] = useState({
    username: user?.username || "",
    email: user?.email || "",
    role: user?.role || "",
  });
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });
  const { showToast } = useToast();

  const logout = () => {
    clearAuthUser();
    navigate("/");
  };

  const closeMenu = () => {
    if (menuRef.current) {
      menuRef.current.removeAttribute("open");
    }
  };

  useEffect(() => {
    const onDocumentClick = (event) => {
      if (!menuRef.current) return;
      if (!menuRef.current.open) return;
      if (menuRef.current.contains(event.target)) return;
      closeMenu();
    };

    const onEscape = (event) => {
      if (event.key === "Escape") {
        closeMenu();
      }
    };

    document.addEventListener("click", onDocumentClick);
    document.addEventListener("keydown", onEscape);
    return () => {
      document.removeEventListener("click", onDocumentClick);
      document.removeEventListener("keydown", onEscape);
    };
  }, []);

  const openProfile = async () => {
    closeMenu();
    try {
      const res = await apiClient.get("/auth/profile", {
        params: { user_id: user?.id },
      });
      setProfileForm({
        username: res.data.username || "",
        email: res.data.email || "",
        role: res.data.role || "",
      });
      setShowProfileModal(true);
    } catch (err) {
      showToast(getApiError(err, "Failed to load profile"), "error");
    }
  };

  const saveProfile = async () => {
    const username = profileForm.username.trim();
    if (username.length < 3) {
      showToast("Username must be at least 3 characters", "warning");
      return;
    }
    try {
      const res = await apiClient.put("/auth/profile", {
        user_id: user?.id,
        username,
      });
      writeAuthUser(res.data.user);
      setProfileForm((prev) => ({ ...prev, username: res.data?.user?.username || username }));
      setShowProfileModal(false);
      showToast("Profile updated", "success");
    } catch (err) {
      showToast(getApiError(err, "Failed to update profile"), "error");
    }
  };

  const openPassword = () => {
    closeMenu();
    setPasswordForm({
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
    });
    setShowPasswordModal(true);
  };

  const changePassword = async () => {
    if (!passwordForm.currentPassword || !passwordForm.newPassword) {
      showToast("Please fill all password fields", "warning");
      return;
    }
    if (passwordForm.newPassword.length < 6) {
      showToast("New password must be at least 6 characters", "warning");
      return;
    }
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      showToast("New passwords do not match", "warning");
      return;
    }
    try {
      await apiClient.post("/auth/change-password", {
        user_id: user?.id,
        current_password: passwordForm.currentPassword,
        new_password: passwordForm.newPassword,
      });
      setShowPasswordModal(false);
      showToast("Password changed successfully", "success");
    } catch (err) {
      showToast(getApiError(err, "Failed to change password"), "error");
    }
  };

  const isActive = (path) => location.pathname === path;
  const isHistoryActive = isActive("/history");
  const navStateClass = isHistoryActive ? "nav-active-history" : "nav-active-home";

  return (
    <>
      <header className="app-header">
        <div className="app-header-left">
          <button type="button" className="brand brand-button" onClick={() => navigate("/upload")}>
            <img src="/medical-vision-mark.svg" alt="Medical Vision Suite" className="brand-logo" />
            <div>
              <p className="eyebrow">Medical Vision Suite</p>
              <p className="brand-subtitle">Clinical AI Screening Workspace</p>
            </div>
          </button>
        </div>
        <nav className={`app-nav ${navStateClass}`}>
          <button
            type="button"
            className={`nav-link ${isActive("/upload") || isActive("/details") ? "active" : ""}`}
            onClick={() => navigate("/upload")}
          >
            Home
          </button>
          <button
            type="button"
            className={`nav-link ${isActive("/history") ? "active" : ""}`}
            onClick={() => navigate("/history")}
          >
            Prediction History
          </button>
        </nav>
        <div className="app-header-right">
          <details className="profile-menu" ref={menuRef}>
            <summary className="profile-trigger">
              <span className="avatar-chip" aria-hidden="true">
                {avatarSeed}
              </span>
              <span className="profile-email">{displayName}</span>
              <span className="profile-role-inline">{roleLabel}</span>
            </summary>
            <div className="profile-dropdown">
              <div className="profile-head">
                <span className="avatar-chip profile-head-avatar" aria-hidden="true">
                  {avatarSeed}
                </span>
                <div className="profile-name-row">
                  <p className="profile-value">{displayName}</p>
                  <div className="profile-role-card">
                    <span className="role-pill">{roleLabel}</span>
                  </div>
                </div>
              </div>
              <div className="profile-menu-actions">
                <button type="button" className="menu-item" onClick={openProfile}>
                  View Profile
                </button>
                <button type="button" className="menu-item" onClick={openPassword}>
                  Change Password
                </button>
                <button type="button" className="menu-item menu-danger" onClick={logout}>
                  Log Out
                </button>
              </div>
            </div>
          </details>
        </div>
      </header>

      {showProfileModal && (
        <div className="account-overlay" onClick={() => setShowProfileModal(false)}>
          <div className="account-card" onClick={(e) => e.stopPropagation()}>
            <h3>Profile</h3>
            <label className="file-label" htmlFor="profile-name">
              Username
            </label>
            <input
              id="profile-name"
              type="text"
              value={profileForm.username}
              onChange={(e) => setProfileForm((prev) => ({ ...prev, username: e.target.value }))}
            />
            <label className="file-label" htmlFor="profile-email">
              Email
            </label>
            <input id="profile-email" type="text" value={profileForm.email} readOnly />
            <label className="file-label" htmlFor="profile-role">
              Role
            </label>
            <input id="profile-role" type="text" value={profileForm.role} readOnly />
            <div className="form-actions">
              <button type="button" className="ghost-btn" onClick={() => setShowProfileModal(false)}>
                Cancel
              </button>
              <button type="button" onClick={saveProfile}>
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {showPasswordModal && (
        <div className="account-overlay" onClick={() => setShowPasswordModal(false)}>
          <div className="account-card" onClick={(e) => e.stopPropagation()}>
            <h3>Change Password</h3>
            <label className="file-label" htmlFor="current-password">
              Current Password
            </label>
            <input
              id="current-password"
              type="password"
              value={passwordForm.currentPassword}
              onChange={(e) =>
                setPasswordForm((prev) => ({ ...prev, currentPassword: e.target.value }))
              }
            />
            <label className="file-label" htmlFor="new-password">
              New Password
            </label>
            <input
              id="new-password"
              type="password"
              value={passwordForm.newPassword}
              onChange={(e) =>
                setPasswordForm((prev) => ({ ...prev, newPassword: e.target.value }))
              }
            />
            <label className="file-label" htmlFor="confirm-new-password">
              Confirm New Password
            </label>
            <input
              id="confirm-new-password"
              type="password"
              value={passwordForm.confirmPassword}
              onChange={(e) =>
                setPasswordForm((prev) => ({ ...prev, confirmPassword: e.target.value }))
              }
            />
            <div className="form-actions">
              <button type="button" className="ghost-btn" onClick={() => setShowPasswordModal(false)}>
                Cancel
              </button>
              <button type="button" onClick={changePassword}>
                Update Password
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default Navbar;
