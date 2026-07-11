import { describe, it, expect, beforeEach } from "vitest";

// Mock fetch globally
const mockFetch = async (url: string, _opts?: RequestInit) => {
  if (url.includes("demo-login")) {
    return {
      ok: true,
      json: async () => ({
        access_token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.demo-token",
        token_type: "bearer",
        tenant_id: "test-tenant",
        user_id: "test-user",
      }),
    };
  }
  return { ok: true, json: async () => ({ data: [] }) };
};
vi.stubGlobal("fetch", mockFetch);

// Set env
process.env.NEXT_PUBLIC_API_URL = "http://localhost:8100/api/v1";

describe("Auth Store", () => {
  beforeEach(async () => {
    // Reset store
    const { useAuthStore } = await import("@/stores/auth");
    useAuthStore.getState().logout();
    localStorage.clear();
  });

  it("starts unauthenticated", async () => {
    const { useAuthStore } = await import("@/stores/auth");
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.token).toBeNull();
  });

  it("login sets token and marks authenticated", async () => {
    const { useAuthStore } = await import("@/stores/auth");
    await useAuthStore.getState().login("test-tenant", "test-user");
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.token).toContain("demo-token");
    expect(state.tenantId).toBe("test-tenant");
  });

  it("logout clears auth state", async () => {
    const { useAuthStore } = await import("@/stores/auth");
    await useAuthStore.getState().login();
    useAuthStore.getState().logout();
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.token).toBeNull();
  });
});
