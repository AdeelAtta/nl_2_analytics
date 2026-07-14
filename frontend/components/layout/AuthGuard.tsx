"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth";
import { type ReactNode } from "react";

export function AuthGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const tryRestoreSession = useAuthStore((s) => s.tryRestoreSession);

  useEffect(() => {
    if (!isAuthenticated) {
      tryRestoreSession().then(() => {
        if (!useAuthStore.getState().isAuthenticated) {
          router.replace("/auth/login");
        }
      });
    }
  }, [isAuthenticated, router, tryRestoreSession]);

  if (!isAuthenticated) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return <>{children}</>;
}
