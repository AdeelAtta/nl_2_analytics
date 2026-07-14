import { create } from "zustand";

import { useQueryStore } from "@/stores/query";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100/api/v1";

const EMAIL_RE = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

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
  setToken: (token: string) => void;
  tryRestoreSession: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  (set) => ({
    token: null,
    tenantId: "",
    userId: "",
    email: "",
    name: "",
    role: "user",
    isAuthenticated: false,

    setToken: (token: string) => set({ token, isAuthenticated: true }),

    tryRestoreSession: async () => {
      try {
        const res = await fetch(`${API_URL}/auth/refresh`, {
          method: "POST",
          credentials: "include",
        });
        if (res.ok) {
          const data = await res.json();
          set({
            token: data.access_token, tenantId: data.tenant_id, userId: data.user_id,
            email: data.email, name: data.name, role: data.role, isAuthenticated: true,
          });
        }
      } catch {
        // Silent — user not logged in
      }
    },

    login: async (tenantId = "demo", userId = "demo-user") => {
      const res = await fetch(`${API_URL}/auth/demo-login`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ tenant_id: tenantId, user_id: userId }),
      });
      if (!res.ok) throw new Error("Demo login failed");
      const data = await res.json();
      set({ token: data.access_token, tenantId: data.tenant_id, userId: data.user_id, isAuthenticated: true });
    },

    loginWithEmail: async (email: string, password: string) => {
      if (!email || !EMAIL_RE.test(email)) throw new Error("Please enter a valid email address");
      if (!password || password.length < 8) throw new Error("Password must be at least 8 characters");
      if (!/[A-Z]/.test(password)) throw new Error("Password must contain an uppercase letter");
      if (!/[a-z]/.test(password)) throw new Error("Password must contain a lowercase letter");
      if (!/\d/.test(password)) throw new Error("Password must contain a digit");
      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email: email.trim().toLowerCase(), password }),
      });
      if (res.status === 401) throw new Error("Invalid email or password");
      if (!res.ok) throw new Error("Login failed. Please try again.");
      const data = await res.json();
      set({
        token: data.access_token, tenantId: data.tenant_id, userId: data.user_id,
        email: data.email, name: data.name, role: data.role, isAuthenticated: true,
      });
    },

    register: async (email: string, password: string, name = "", tenantName = "") => {
      if (!email || !EMAIL_RE.test(email)) throw new Error("Please enter a valid email address");
      if (!password || password.length < 8) throw new Error("Password must be at least 8 characters");
      if (!/[A-Z]/.test(password)) throw new Error("Password must contain an uppercase letter");
      if (!/[a-z]/.test(password)) throw new Error("Password must contain a lowercase letter");
      if (!/\d/.test(password)) throw new Error("Password must contain a digit");
      const res = await fetch(`${API_URL}/auth/register`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email: email.trim().toLowerCase(), password, name, tenant_name: tenantName }),
      });
      if (res.status === 409) throw new Error("An account with this email already exists");
      if (res.status === 422) {
        const err = await res.json();
        throw new Error(err.detail?.[0]?.msg || "Invalid input");
      }
      if (!res.ok) throw new Error("Registration failed. Please try again.");
      const data = await res.json();
      set({
        token: data.access_token, tenantId: data.tenant_id, userId: data.user_id,
        email: data.email, name: data.name, role: data.role, isAuthenticated: true,
      });
    },

    logout: async () => {
      try {
        await fetch(`${API_URL}/auth/logout`, {
          method: "POST", credentials: "include",
        });
      } catch { /* ignore */ }
      useQueryStore.getState().resetStore();
      set({
        token: null, isAuthenticated: false, email: "", name: "", role: "",
        tenantId: "", userId: "",
      });
    },
  }),
);
