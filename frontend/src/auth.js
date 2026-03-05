export function readAuthUser() {
  try {
    const raw = sessionStorage.getItem("auth_user");
    if (!raw) return null;
    const user = JSON.parse(raw);
    if (!user || typeof user !== "object") return null;
    if (!Number.isInteger(user.id)) return null;
    if (typeof user.email !== "string" || !user.email.trim()) return null;
    if (!["doctor", "technician"].includes(user.role)) return null;
    return user;
  } catch {
    return null;
  }
}

export function writeAuthUser(user) {
  sessionStorage.setItem("auth_user", JSON.stringify(user));
  // remove any legacy persisted auth so closed-browser sessions don't stay logged in
  localStorage.removeItem("auth_user");
}

export function clearAuthUser() {
  sessionStorage.removeItem("auth_user");
  localStorage.removeItem("auth_user");
}

