const API_BASE = "/api";

let isRefreshing = false;
let refreshPromise = null;

async function refreshToken() {
  if (isRefreshing) return refreshPromise;
  isRefreshing = true;
  refreshPromise = fetch(`${API_BASE}/auth/refresh`, {
    method: "POST",
    credentials: "same-origin",
  }).then((res) => {
    isRefreshing = false;
    return res.ok;
  }).catch(() => {
    isRefreshing = false;
    return false;
  });
  return refreshPromise;
}

export async function fetchAPI(path, options = {}) {
  const { body, headers: customHeaders, ...rest } = options;

  const headers = { ...customHeaders };
  if (body && typeof body === "string") {
    headers["Content-Type"] = "application/json";
  }

  let response = await fetch(`${API_BASE}${path}`, {
    headers,
    body,
    credentials: "same-origin",
    ...rest,
  });

  // Auto-refresh on 401 (except for auth endpoints)
  if (response.status === 401 && !path.startsWith("/auth/")) {
    const refreshed = await refreshToken();
    if (refreshed) {
      response = await fetch(`${API_BASE}${path}`, {
        headers,
        body,
        credentials: "same-origin",
        ...rest,
      });
    }
  }

  if (!response.ok) {
    let errorMessage = "Request failed";
    try {
      const error = await response.json();
      errorMessage = error.error || errorMessage;
    } catch {}
    const err = new Error(errorMessage);
    err.status = response.status;
    throw err;
  }

  return response.json();
}

export function uploadFile(path, formData) {
  return fetch(`${API_BASE}${path}`, {
    method: "POST",
    body: formData,
    credentials: "same-origin",
  }).then(async (res) => {
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.error || "Upload failed");
    }
    return res.json();
  });
}
