const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080/api/v1";

interface ApiOptions extends RequestInit {
  params?: Record<string, string>;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("auth-token");
  }

  private buildUrl(path: string, params?: Record<string, string>): string {
    const url = new URL(`${this.baseUrl}${path}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => url.searchParams.append(key, value));
    }
    return url.toString();
  }

  private getHeaders(): HeadersInit {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  async request<T>(path: string, options: ApiOptions = {}): Promise<T> {
    const { params, ...fetchOptions } = options;
    const url = this.buildUrl(path, params);

    const response = await fetch(url, {
      ...fetchOptions,
      headers: { ...this.getHeaders(), ...fetchOptions.headers },
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error [${response.status}]: ${error}`);
    }

    return response.json() as Promise<T>;
  }

  get<T>(path: string, options?: ApiOptions) {
    return this.request<T>(path, { ...options, method: "GET" });
  }

  post<T>(path: string, body?: unknown, options?: ApiOptions) {
    return this.request<T>(path, { ...options, method: "POST", body: body ? JSON.stringify(body) : undefined });
  }

  put<T>(path: string, body?: unknown, options?: ApiOptions) {
    return this.request<T>(path, { ...options, method: "PUT", body: body ? JSON.stringify(body) : undefined });
  }

  delete<T>(path: string, options?: ApiOptions) {
    return this.request<T>(path, { ...options, method: "DELETE" });
  }
}

export const api = new ApiClient(BASE_URL);
