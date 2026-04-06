const API_BASE = "/api";

export async function fetchAPI(path, options = {}) {
  const { body, headers: customHeaders, ...rest } = options;

  const headers = { ...customHeaders };
  if (body && typeof body === "string") {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_BASE}${path}`, {
    headers,
    body,
    ...rest,
  });

  if (!response.ok) {
    let errorMessage = "Request failed";
    try {
      const error = await response.json();
      errorMessage = error.error || errorMessage;
    } catch {}
    throw new Error(errorMessage);
  }

  return response.json();
}

export function uploadFile(path, formData) {
  return fetch(`${API_BASE}${path}`, {
    method: "POST",
    body: formData,
  }).then(async (res) => {
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.error || "Upload failed");
    }
    return res.json();
  });
}
