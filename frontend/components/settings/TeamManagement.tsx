"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuthStore } from "@/stores/auth";
import { useUIStore } from "@/stores/ui";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100/api/v1";

interface Member {
  id: string; email: string; name: string; role: string;
}

export function TeamManagement() {
  const token = useAuthStore((s) => s.token);
  const addToast = useUIStore((s) => s.addToast);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviting, setInviting] = useState(false);

  const load = async () => {
    if (!token) return;
    try {
      const r = await fetch(`${API_URL}/tenants/members`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (r.ok) {
        const d = await r.json();
        setMembers(d.data ?? []);
      }
    } catch { /* ignore */ }
    setLoading(false);
  };

  useEffect(() => { load(); }, [token]);

  const handleInvite = async () => {
    if (!token || !inviteEmail.trim()) return;
    setInviting(true);
    try {
      const r = await fetch(`${API_URL}/tenants/members/invite`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ email: inviteEmail.trim() }),
      });
      if (r.ok) {
        addToast(`Invitation sent to ${inviteEmail}`, "success");
        setInviteEmail("");
        load();
      } else {
        addToast("Failed to send invitation", "error");
      }
    } catch {
      addToast("Failed to send invitation", "error");
    }
    setInviting(false);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Team Members</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <Input
            placeholder="colleague@company.com"
            value={inviteEmail}
            onChange={(e) => setInviteEmail(e.target.value)}
            aria-label="Email to invite"
          />
          <Button onClick={handleInvite} disabled={inviting || !inviteEmail.trim()}>
            {inviting ? "Sending..." : "Invite"}
          </Button>
        </div>
        {loading ? (
          <p className="text-sm text-muted-foreground">Loading...</p>
        ) : members.length === 0 ? (
          <p className="text-sm text-muted-foreground">No team members yet</p>
        ) : (
          <div className="space-y-2">
            {members.map((m) => (
              <div key={m.id} className="flex items-center justify-between rounded-lg border p-3">
                <div>
                  <p className="text-sm font-medium">{m.name || m.email}</p>
                  <p className="text-xs text-muted-foreground">{m.email}</p>
                </div>
                <span className="rounded bg-muted px-2 py-0.5 text-xs capitalize">{m.role}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
