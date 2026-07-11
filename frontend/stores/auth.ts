import { create } from "zustand";
import { persist } from "zustand/middleware";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100/api/v1";

interface AuthState {
  token: string | null;
  tenantId: string;
  userId: string;
  email: string;
  name: string;
  role: string;
  isAuthenticated: boolean;
  login: (tenantId?: string, userId?: string) => Promise<void>;
  loginWithEmail: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string, tenantName?: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      tenantId: "demo",
      userId: "demo-user",
      email: "",
      name: "",
      role: "user",
      isAuthenticated: false,
      login: async (tenantId = "demo", userId = "demo-user") => {
        const res = await fetch(`${API_URL}/auth/demo-login`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ tenant_id: tenantId, user_id: userId }),
        });
        if (!res.ok) throw new Error("Login failed");
        const data = await res.json();
        set({ token: data.access_token, tenantId: data.tenant_id, userId: data.user_id, isAuthenticated: true });
      },
      loginWithEmail: async (email: string, password: string) => {
        const res = await fetch(`${API_URL}/auth/login`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        if (!res.ok) throw new Error("Invalid email or password");
        const data = await res.json();
        set({
          token: data.access_token, tenantId: data.tenant_id, userId: data.user_id,
          email: data.email, name: data.name, role: data.role, isAuthenticated: true,
        });
      },
      register: async (email: string, password: string, name = "", tenantName = "") => {
        const res = await fetch(`${API_URL}/auth/register`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, name, tenant_name: tenantName }),
        });
        if (!res.ok) {
          const text = await res.text();
          throw new Error(text.includes("already") ? "Email already registered" : "Registration failed");
        }
        const data = await res.json();
        set({
          token: data.access_token, tenantId: data.tenant_id, userId: data.user_id,
          email: data.email, name: data.name, role: data.role, isAuthenticated: true,
        });
      },
      logout: () => set({
        token: null, isAuthenticated: false, email: "", name: "", role: "user",
      }),
    }),
    {
      name: "openquery-auth",
      partialize: (state) => ({
        token: state.token, tenantId: state.tenantId, userId: state.userId,
        email: state.email, name: state.name, role: state.role, isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
);
