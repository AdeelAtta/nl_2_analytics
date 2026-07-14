"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuthStore } from "@/stores/auth";
import { Database } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100/api/v1";

interface Column {
  id: string; name: string; data_type: string;
  is_nullable: boolean; is_primary_key: boolean; description?: string;
}

interface TableInfo {
  id: string; name: string; description?: string; schema_name?: string;
  columns?: Column[];
  sample_rows?: Record<string, unknown>[];
}

interface DbInfo {
  name: string; database: string; table_count: number;
}

export function SchemaBrowser() {
  const token = useAuthStore((s) => s.token);
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<TableInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [databases, setDatabases] = useState<DbInfo[]>([]);
  const [activeDb, setActiveDb] = useState("");

  const loadTables = (db: string) => {
    if (!token) return;
    setLoading(true);
    setError("");
    const url = db ? `${API_URL}/schema/tables?database=${encodeURIComponent(db)}` : `${API_URL}/schema/tables`;
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then((d) => {
        if (d.data) setTables(d.data);
        else setError("No tables found");
      })
      .catch(() => setError("Could not load schema"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (!token) return;
    fetch(`${API_URL}/schema/databases`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then((d) => {
        if (d.data && d.data.length > 0) {
          setDatabases(d.data);
          const first = d.data[0].database;
          setActiveDb(first);
          loadTables(first);
        } else {
          loadTables("");
        }
      })
      .catch(() => loadTables(""));
  }, [token]);

  const loadTable = async (t: TableInfo) => {
    setSelected(t);
    if (t.columns) return;
    try {
      const url = activeDb !== "" ? `${API_URL}/schema/tables/${t.id}?database=${encodeURIComponent(activeDb)}` : `${API_URL}/schema/tables/${t.id}`;
      const r = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const d = await r.json();
      if (d.data) setSelected(d.data);
    } catch {
      setError("Could not load table details");
    }
  };

  const filtered = tables.filter((t) =>
    !search || t.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-4">
      {databases.length > 0 && (
        <div className="flex items-center gap-2">
          <Database className="h-4 w-4 text-muted-foreground" />
          <select
            value={activeDb}
            onChange={(e) => { setActiveDb(e.target.value); setSelected(null); loadTables(e.target.value); }}
            className="rounded-md border bg-background px-2 py-1 text-xs font-medium outline-none"
          >
            {databases.map((db) => (
              <option key={db.database} value={db.database}>
                {db.name} ({db.table_count} tables)
              </option>
            ))}
          </select>
          <span className="text-xs text-muted-foreground">Database</span>
        </div>
      )}

    <div className="flex flex-col gap-4 lg:flex-row">
      <div className="w-full shrink-0 space-y-3 lg:w-72">
        <Input
          placeholder="Search tables..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="space-y-1">
          {loading && (
            <div className="flex items-center gap-2 py-4 text-sm text-muted-foreground">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
              Loading tables...
            </div>
          )}
          {error && !loading && (
            <p className="py-4 text-sm text-destructive">{error}</p>
          )}
          {filtered.map((t) => (
            <button
              key={t.id}
              onClick={() => loadTable(t)}
              className={`w-full rounded-lg border px-3 py-2.5 text-left text-sm transition-colors hover:bg-accent ${
                selected?.id === t.id ? "border-primary bg-accent/50 font-medium" : ""
              }`}
            >
              <span>{t.name}</span>
              {t.description && (
                <span className="ml-2 text-xs text-muted-foreground">
                  {t.description}
                </span>
              )}
            </button>
          ))}
          {!loading && !error && filtered.length === 0 && (
            <p className="py-4 text-sm text-muted-foreground">
              {search ? "No matching tables" : "No tables synced yet. Connect a database in Settings."}
            </p>
          )}
        </div>
      </div>

      <div className="flex-1">
        {selected ? (
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <CardTitle className="text-lg">{selected.name}</CardTitle>
                {selected.description && (
                  <span className="text-sm text-muted-foreground">
                    — {selected.description}
                  </span>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {selected.columns && selected.columns.length > 0 ? (
                <div className="overflow-x-auto rounded-lg border">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50 text-left">
                        <th className="px-3 py-2.5 font-medium text-muted-foreground">Column</th>
                        <th className="px-3 py-2.5 font-medium text-muted-foreground">Type</th>
                        <th className="px-3 py-2.5 font-medium text-muted-foreground">Nullable</th>
                        <th className="px-3 py-2.5 font-medium text-muted-foreground">Key</th>
                        <th className="px-3 py-2.5 font-medium text-muted-foreground">Description</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selected.columns.map((c) => (
                        <tr key={c.id} className="border-b last:border-0 hover:bg-muted/30">
                          <td className="px-3 py-2.5 font-mono text-xs font-medium">{c.name}</td>
                          <td className="px-3 py-2.5 font-mono text-xs text-muted-foreground">{c.data_type}</td>
                          <td className="px-3 py-2.5 text-xs">
                            {c.is_nullable
                              ? <span className="text-muted-foreground">YES</span>
                              : <span className="font-medium text-amber-600">NO</span>}
                          </td>
                          <td className="px-3 py-2.5">
                            {c.is_primary_key
                              ? <span className="rounded bg-primary/10 px-1.5 py-0.5 text-xs font-medium text-primary">PK</span>
                              : <span className="text-muted-foreground text-xs">—</span>}
                          </td>
                          <td className="px-3 py-2.5 text-xs text-muted-foreground">{c.description ?? ""}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="flex h-24 items-center justify-center rounded-lg border-2 border-dashed text-sm text-muted-foreground">
                  No column data available
                </div>
              )}

              {(selected as TableInfo).sample_rows && (selected as TableInfo).sample_rows!.length > 0 && (
                <div className="mt-4">
                  <p className="mb-2 text-xs font-medium text-muted-foreground uppercase tracking-wider">Sample Rows</p>
                  <div className="overflow-x-auto rounded-lg border">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b bg-muted/50 text-left">
                          {Object.keys((selected as TableInfo).sample_rows![0]).map((k) => (
                            <th key={k} className="px-2 py-1.5 font-medium text-muted-foreground">{k}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {(selected as TableInfo).sample_rows!.map((row, i) => (
                          <tr key={i} className="border-b last:border-0 hover:bg-muted/30">
                            {Object.values(row).map((v, j) => (
                              <td key={j} className="px-2 py-1 font-mono text-muted-foreground">
                                {v === null ? <span className="italic">NULL</span> : String(v).slice(0, 30)}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="flex h-48 items-center justify-center rounded-lg border-2 border-dashed text-sm text-muted-foreground">
            {tables.length > 0
              ? "Select a table to view its columns"
              : "No schema data available"}
          </div>
        )}
      </div>
    </div>
    </div>
  );
}
