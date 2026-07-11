import { create } from "zustand";

export interface Toast {
  id: string;
  message: string;
  type: "success" | "error" | "info" | "warning";
  duration?: number;
}

interface UIState {
  toasts: Toast[];
  addToast: (message: string, type?: Toast["type"], duration?: number) => void;
  removeToast: (id: string) => void;
}

export const useUIStore = create<UIState>()((set, get) => ({
  toasts: [],
  addToast: (message, type = "info", duration = 4000) => {
    const id = Math.random().toString(36).slice(2);
    set({ toasts: [...get().toasts, { id, message, type, duration }] });
    if (duration > 0) {
      setTimeout(() => get().removeToast(id), duration);
    }
  },
  removeToast: (id) => set({ toasts: get().toasts.filter((t) => t.id !== id) }),
}));
