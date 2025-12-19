export const API_BASE = import.meta.env.VITE_API_BASE || "/api";

export type ApiError = {
  detail?: string;
  message?: string;
};

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  });

  const text = await response.text();
  let data: T | ApiError = {} as T;
  if (text) {
    try {
      data = JSON.parse(text) as T;
    } catch {
      data = { message: text } as ApiError;
    }
  }

  if (!response.ok) {
    const error = data as ApiError;
    let message: unknown = error.detail || error.message || response.statusText;
    if (Array.isArray(message)) {
      message = message
        .map((item) => (typeof item === "string" ? item : item?.msg || JSON.stringify(item)))
        .join(", ");
    } else if (typeof message === "object") {
      message = JSON.stringify(message);
    }
    throw new Error(String(message));
  }

  return data;
}
