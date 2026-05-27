const API = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? "http://127.0.0.1:8000" : "");

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
    ...(token ? { Authorization: token } : {}),
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

export { API };
