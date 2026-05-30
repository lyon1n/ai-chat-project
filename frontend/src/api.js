const API =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? "http://127.0.0.1:8000" : "");

export function getToken() {
  return localStorage.getItem("token");
}

export function setToken(token) {
  localStorage.setItem("token", token);
}

export function clearToken() {
  localStorage.removeItem("token");
}

export function authHeaders(extra = {}) {
  const token = getToken();
  return {
    ...extra,
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function apiFetch(path, options = {}) {
  const headers = authHeaders(options.headers || {});
  if (options.body instanceof FormData) {
    delete headers["Content-Type"];
    delete headers["content-type"];
  }
  const response = await fetch(`${API}${path}`, { ...options, headers });

  if (response.status === 401) {
    clearToken();
    window.location.reload();
    throw new Error("登录已过期，请重新登录");
  }

  return response;
}

export async function errorMessage(response, fallback = "操作失败") {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) return data.detail.map((item) => item.msg).join("; ");
    if (data.error) return data.error;
  } catch {
    /* ignore */
  }
  return fallback;
}

export { API };
