"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuthStore } from "@/stores/auth";
import { useUIStore } from "@/stores/ui";

interface SyncTable { name: string; columns: unknown[] }
interface SyncData { tables: SyncTable[]; added: number; changed: number; removed: number }

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100/api/v1";
const DB_TYPES = [
  { value: "postgresql", label: "PostgreSQL" },
  { value: "mysql", label: "MySQL" },
  { value: "snowflake", label: "Snowflake" },
  { value: "bigquery", label: "BigQuery" },
  { value: "duckdb", label: "DuckDB" },
];

export function ConnectDatabase() {
  const token = useAuthStore((s) => s.token);
  const addToast = useUIStore((s) => s.addToast);

  const [dbType, setDbType] = useState("postgresql");
  const [host, setHost] = useState("localhost");
  const [port, setPort] = useState("5432");
  const [dbName, setDbName] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [testing, setTesting] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [testResult, setTestResult] = useState<"success" | "error" | null>(null);
  const [syncResult, setSyncResult] = useState<SyncData | null>(null);

  const getConfig = () => ({
    db_type: dbType, host, port: parseInt(port), database: dbName, username, password,
  });

  const handleTest = async () => {
    if (!token) return;
    setTesting(true); setTestResult(null);
    try {
      const r = await fetch(`${API_URL}/sync/test`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(getConfig()),
      });
      const d = await r.json();
      if (d.success) {
        setTestResult("success");
        addToast("Connection successful!", "success");
      } else {
        setTestResult("error");
        addToast(d.error || "Connection failed", "error");
      }
    } catch {
      setTestResult("error");
      addToast("Connection failed", "error");
    }
    setTesting(false);
  };

  const handleSync = async () => {
    if (!token) return;
    setSyncing(true); setSyncResult(null);
    try {
      const r = await fetch(`${API_URL}/sync/extract`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(getConfig()),
      });
      const d = await r.json();
      if (d.success) {
        setSyncResult(d.data as SyncData);
        addToast(`Synced ${d.data.tables.length} tables!`, "success");
      } else {
        addToast(d.error || "Sync failed", "error");
      }
    } catch {
      addToast("Sync failed", "error");
    }
    setSyncing(false);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Connect Database</CardTitle>
          <CardDescription>Connect to your database to query your real schema</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2">
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
              <Input id="host" value={host} onChange={(e) => setHost(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="port">Port</Label>
              <Input id="port" type="number" value={port} onChange={(e) => setPort(e.target.value)} />
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

          {testResult === "success" && <p className="mt-2 text-sm text-green-600">Connected successfully</p>}
          {testResult === "error" && <p className="mt-2 text-sm text-destructive">Connection failed — check your credentials</p>}

          <div className="mt-4 flex gap-2">
            <Button variant="outline" onClick={handleTest} disabled={testing || !token}>
              {testing ? "Testing..." : "Test Connection"}
            </Button>
            <Button onClick={handleSync} disabled={syncing || !token || testResult !== "success"}>
              {syncing ? "Syncing..." : "Sync Schema"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {syncResult && syncResult.tables && syncResult.tables.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Synced Tables ({syncResult.tables.length})</CardTitle>
            <CardDescription>
              {syncResult.added} added, {syncResult.changed} changed, {syncResult.removed} removed
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {syncResult.tables.map((t: SyncTable, i: number) => (
                <div key={i} className="rounded-lg border p-3">
                  <p className="text-sm font-medium">{t.name}</p>
                  <p className="text-xs text-muted-foreground">{t.columns.length} columns</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
