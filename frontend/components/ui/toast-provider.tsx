"use client";

import { useUIStore } from "@/stores/ui";
import { X } from "lucide-react";

export function ToastContainer() {
  const toasts = useUIStore((s) => s.toasts);
  const removeToast = useUIStore((s) => s.removeToast);

  if (toasts.length === 0) return null;

  const colors = {
    success: "bg-green-600 border-green-700",
    error: "bg-red-600 border-red-700",
    info: "bg-blue-600 border-blue-700",
    warning: "bg-yellow-500 border-yellow-600",
  };

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`flex items-center gap-3 rounded-lg border px-4 py-3 text-sm text-white shadow-lg ${colors[t.type]}`}
        >
          <span className="flex-1">{t.message}</span>
          <button onClick={() => removeToast(t.id)} className="shrink-0 opacity-70 hover:opacity-100">
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  );
}
