const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getToken() {
  return localStorage.getItem("reptrack_token");
}

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let detail = "Error de red";
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch (_) {}
    throw new Error(detail);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  register: (payload) => request("/auth/register", { method: "POST", body: payload, auth: false }),
  login: (payload) => request("/auth/login", { method: "POST", body: payload, auth: false }),
  me: () => request("/auth/me"),

  listExercises: () => request("/exercises"),
  createExercise: (payload) => request("/exercises", { method: "POST", body: payload }),
  deleteExercise: (id) => request(`/exercises/${id}`, { method: "DELETE" }),

  listSessions: () => request("/workouts"),
  createSession: (payload) => request("/workouts", { method: "POST", body: payload }),
  deleteSession: (id) => request(`/workouts/${id}`, { method: "DELETE" }),

  getProgress: (exerciseId) => request(`/progress/${exerciseId}`),
};

export function saveToken(token) {
  localStorage.setItem("reptrack_token", token);
}

export function clearToken() {
  localStorage.removeItem("reptrack_token");
}

export function isLoggedIn() {
  return !!getToken();
}
