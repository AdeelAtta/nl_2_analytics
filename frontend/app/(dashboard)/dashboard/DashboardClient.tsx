"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuthStore } from "@/stores/auth";
import { useUIStore } from "@/stores/ui";
import { CardSkeleton } from "@/components/ui/skeleton";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100/api/v1";

export function DashboardClient() {
  const token = useAuthStore((s) => s.token);
  const addToast = useUIStore((s) => s.addToast);
  const [queries, setQueries] = useState<number | null>(null);
  const [connections, setConnections] = useState<number | null>(null);
  const [tables, setTables] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    Promise.allSettled([
      fetch(`${API_URL}/history?page_size=1`, { headers: { Authorization: `Bearer ${token}` } })
        .then((r) => r.ok ? r.json() : null)
        .then((d) => setQueries(d?.meta?.total ?? 0)),
      fetch(`${API_URL}/connections`, { headers: { Authorization: `Bearer ${token}` } })
        .then((r) => r.ok ? r.json() : null)
        .then((d) => setConnections(d?.data?.length ?? 0)),
      fetch(`${API_URL}/schema/tables?page_size=1`, { headers: { Authorization: `Bearer ${token}` } })
        .then((r) => r.ok ? r.json() : null)
        .then((d) => setTables(d?.meta?.total ?? 0)),
    ])
      .catch(() => addToast("Could not load dashboard data", "warning"))
      .finally(() => setLoading(false));
  }, [token, addToast]);

  const stats = [
    { title: "Total Queries", value: queries, link: "/query", color: "text-blue-600 dark:text-blue-400", desc: "Queries executed" },
    { title: "Connections", value: connections, link: "/settings", color: "text-green-600 dark:text-green-400", desc: "Databases connected" },
    { title: "Schema Tables", value: tables, link: "/schema", color: "text-purple-600 dark:text-purple-400", desc: "Tables discovered" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Welcome to OpenQuery</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3" role="list" aria-label="Statistics">
        {stats.map((stat) => (
          <Link key={stat.title} href={stat.link} aria-label={`View ${stat.title}`} role="listitem">
            <Card className="transition-colors hover:bg-accent cursor-pointer h-full">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <CardSkeleton />
                ) : (
                  <>
                    <div className={`text-3xl font-bold ${stat.color}`}>
                      {stat.value ?? "—"}
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">{stat.desc}</p>
                  </>
                )}
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
