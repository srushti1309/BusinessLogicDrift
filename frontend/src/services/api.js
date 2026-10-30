
const API_BASE_URL = "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error("The server returned an invalid response.");
  }

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : `Request failed (${response.status})`
    );
  }

  return data;
}

export const dashboardAPI = {
  getDashboard: () => request("/api/dashboard"),

  runAnalysis: () =>
    request("/api/analyze", { method: "POST" }),

  localize: () =>
    request("/api/localize", { method: "POST" }),

  repair: () =>
    request("/api/repair", { method: "POST" }),
};
