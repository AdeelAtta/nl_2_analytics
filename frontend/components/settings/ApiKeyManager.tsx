"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuthStore } from "@/stores/auth";
import { useUIStore } from "@/stores/ui";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100/api/v1";

interface ApiKey {
  id: string; name: string; prefix: string; created_at: string;
}

export function ApiKeyManager() {
  const token = useAuthStore((s) => s.token);
  const addToast = useUIStore((s) => s.addToast);
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [newName, setNewName] = useState("");
  const [creating, setCreating] = useState(false);
  const [newKeyValue, setNewKeyValue] = useState("");

  const load = async () => {
    if (!token) return;
    try {
      const r = await fetch(`${API_URL}/auth/api-keys`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (r.ok) {
        const d = await r.json();
        setKeys(d.data ?? []);
      }
    } catch { /* ignore */ }
    setLoading(false);
  };

  useEffect(() => { load(); }, [token]);

  const handleCreate = async () => {
    if (!token || !newName.trim()) return;
    setCreating(true);
    setNewKeyValue("");
    try {
      const r = await fetch(`${API_URL}/auth/api-keys`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ name: newName.trim() }),
      });
      if (r.ok) {
        const d = await r.json();
        setNewKeyValue(d.data.key);
        setNewName("");
        load();
      } else {
        addToast("Failed to create API key", "error");
      }
    } catch {
      addToast("Failed to create API key", "error");
    }
    setCreating(false);
  };

  const handleRevoke = async (id: string, name: string) => {
    if (!token) return;
    if (!confirm(`Revoke key "${name}"? This cannot be undone.`)) return;
    try {
      const r = await fetch(`${API_URL}/auth/api-keys/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (r.ok) {
        addToast(`Key "${name}" revoked`, "success");
        load();
      }
    } catch { /* ignore */ }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>API Keys</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {newKeyValue && (
          <div className="rounded-lg border border-green-500 bg-green-50 p-3 text-sm dark:bg-green-950">
            <p className="mb-1 font-medium text-green-800 dark:text-green-200">Key created — copy it now</p>
            <code className="block break-all rounded bg-green-100 p-2 font-mono text-xs dark:bg-green-900">
              {newKeyValue}
            </code>
            <p className="mt-1 text-xs text-green-600 dark:text-green-400">
              You won&apos;t be able to see it again
            </p>
          </div>
        )}
        <div className="flex gap-2">
          <Input
            placeholder="e.g., Production API Key"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            aria-label="New API key name"
          />
          <Button onClick={handleCreate} disabled={creating || !newName.trim()}>
            {creating ? "Creating..." : "Create Key"}
          </Button>
        </div>
        {loading ? (
          <p className="text-sm text-muted-foreground">Loading...</p>
        ) : keys.length === 0 ? (
          <p className="text-sm text-muted-foreground">No API keys yet</p>
        ) : (
          <div className="space-y-2">
            {keys.map((k) => (
              <div key={k.id} className="flex items-center justify-between rounded-lg border p-3">
                <div>
                  <p className="text-sm font-medium">{k.name}</p>
                  <p className="font-mono text-xs text-muted-foreground">{k.prefix}</p>
                </div>
                <Button variant="destructive" size="sm" onClick={() => handleRevoke(k.id, k.name)}>
                  Revoke
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
