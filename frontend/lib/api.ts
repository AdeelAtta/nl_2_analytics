import { useAuthStore } from "@/stores/auth";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status = 0) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100/api/v1";
const REFRESH_URL = `${BASE_URL}/auth/refresh`;

function getToken(): string | null {
  return useAuthStore.getState().token;
}

let isRefreshing = false;
let pendingRequests: Array<(token: string) => void> = [];

async function refreshAccessToken(): Promise<string> {
  const res = await fetch(REFRESH_URL, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) throw new ApiError("Refresh failed", res.status);
  const data = await res.json();
  useAuthStore.getState().setToken(data.access_token);
  return data.access_token;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });

  if (res.status === 401) {
    // Try to refresh and retry
    if (!isRefreshing) {
      isRefreshing = true;
      try {
        const newToken = await refreshAccessToken();
        isRefreshing = false;
        pendingRequests.forEach((cb) => cb(newToken));
        pendingRequests = [];
        headers["Authorization"] = `Bearer ${newToken}`;
        const retry = await fetch(`${BASE_URL}${path}`, { ...init, headers, credentials: "include" });
        if (!retry.ok) throw new ApiError("Request failed", retry.status);
        return retry.json() as Promise<T>;
      } catch {
        isRefreshing = false;
        pendingRequests = [];
        useAuthStore.getState().logout();
        if (typeof window !== "undefined") window.location.href = "/auth/login";
        throw new ApiError("Session expired");
      }
    } else {
      return new Promise((resolve, reject) => {
        pendingRequests.push(async (newToken) => {
          headers["Authorization"] = `Bearer ${newToken}`;
          const retry = await fetch(`${BASE_URL}${path}`, { ...init, headers, credentials: "include" });
          if (!retry.ok) reject(new ApiError("Request failed", retry.status));
          else resolve(retry.json() as Promise<T>);
        });
      });
    }
  }

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(text || `Request failed [${res.status}]`, res.status);
  }

  return res.json() as Promise<T>;
}

export function apiGet<T>(path: string): Promise<T> {
  return request<T>(path);
}

export function apiPost<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(path, {
    method: "POST",
    body: body ? JSON.stringify(body) : undefined,
  });
}
