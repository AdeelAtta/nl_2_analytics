"use client";

import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuthStore } from "@/stores/auth";

const DB_TYPES = [
  { value: "postgresql", label: "PostgreSQL" },
  { value: "mysql", label: "MySQL" },
  { value: "snowflake", label: "Snowflake" },
  { value: "bigquery", label: "BigQuery" },
  { value: "duckdb", label: "DuckDB" },
];

interface Connection {
  id: string;
  name: string;
  db_type: string;
  host: string;
  port: number;
  database_name: string;
  sync_status: string;
  table_count: number;
  last_synced_at: string | null;
  created_at: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100/api/v1";

export function ConnectDatabase() {
  const token = useAuthStore((s) => s.token);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [name, setName] = useState("");
  const [dbType, setDbType] = useState("postgresql");
  const [host, setHost] = useState("localhost");
  const [port, setPort] = useState("5432");
  const [dbName, setDbName] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const loadConnections = async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_URL}/connections`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setConnections(data.data ?? []);
      }
    } catch { /* ignore */ }
    setLoaded(true);
  };

  if (!loaded) loadConnections();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/connections`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ name, db_type: dbType, host, port: parseInt(port), database_name: dbName, username, password }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text);
      }
      setName("");
      setHost("localhost");
      setPort("5432");
      setDbName("");
      setUsername("");
      setPassword("");
      loadConnections();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Add Database Connection</CardTitle>
          <CardDescription>Connect to your database to start querying</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="name">Connection Name</Label>
                <Input id="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="My Production DB" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="db-type">Database Type</Label>
                <Select value={dbType} onValueChange={setDbType}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {DB_TYPES.map((t) => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="host">Host</Label>
                <Input id="host" value={host} onChange={(e) => setHost(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="port">Port</Label>
                <Input id="port" type="number" value={port} onChange={(e) => setPort(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="dbname">Database Name</Label>
                <Input id="dbname" value={dbName} onChange={(e) => setDbName(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input id="username" value={username} onChange={(e) => setUsername(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
              </div>
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button type="submit" disabled={loading || !name}>
              {loading ? "Connecting..." : "Connect Database"}
            </Button>
          </form>
        </CardContent>
      </Card>

      {connections.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Connected Databases</CardTitle>
            <CardDescription>{connections.length} connection{connections.length !== 1 ? "s" : ""}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {connections.map((c) => (
                <div key={c.id} className="flex items-center justify-between rounded-lg border p-3">
                  <div>
                    <p className="font-medium">{c.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {c.db_type} — {c.host}:{c.port}/{c.database_name}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <span className={`h-2 w-2 rounded-full ${
                      c.sync_status === "synced" ? "bg-green-500" :
                      c.sync_status === "syncing" ? "bg-yellow-400" :
                      c.sync_status === "error" ? "bg-red-500" : "bg-gray-300"
                    }`} />
                    <span className="capitalize text-muted-foreground">{c.sync_status}</span>
                    {c.table_count > 0 && <span className="text-muted-foreground">({c.table_count} tables)</span>}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
