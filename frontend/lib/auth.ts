export interface SessionUser {
  id: string;
  name: string;
  email: string;
  role: "admin" | "analyst" | "viewer";
  avatar?: string;
}

export interface Session {
  user: SessionUser;
  expires: string;
}

export function useSession(): { data: Session | null; status: "loading" | "authenticated" | "unauthenticated" } {
  return {
    data: {
      user: {
        id: "1",
        name: "Demo User",
        email: "demo@example.com",
        role: "admin",
      },
      expires: "2099-12-31T23:59:59Z",
    },
    status: "authenticated",
  };
}

export function signIn(): void {
  console.log("[Auth] signIn stub called");
}

export function signOut(): void {
  console.log("[Auth] signOut stub called");
}
