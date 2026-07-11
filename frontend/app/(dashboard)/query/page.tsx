"use client";

import { useEffect, useRef } from "react";
import { useAuthStore } from "@/stores/auth";
import { useQueryStore } from "@/stores/query";
import { useUIStore } from "@/stores/ui";
import { ChatInput } from "@/components/query/ChatInput";
import { ChatMessage } from "@/components/query/ChatMessage";

export default function QueryPage() {
  const token = useAuthStore((s) => s.token);
  const isAuth = useAuthStore((s) => s.isAuthenticated);
  const addToast = useUIStore((s) => s.addToast);
  const { currentResult, loading, error, history, pastQueries, execute, loadHistory } = useQueryStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (token && isAuth) loadHistory(token);
  }, [token, isAuth, loadHistory]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history.length, currentResult, loading, pastQueries.length]);

  const handleSend = (q: string) => {
    if (!token) { addToast("Please log in first", "warning"); return; }
    useQueryStore.getState().setQuery(q);
    execute(token).catch(() => addToast("Query failed", "error"));
  };

  const allItems = [
    ...pastQueries.map((pq) => ({
      type: "past" as const,
      query: pq.query,
      sql: pq.sql,
      duration_ms: pq.duration_ms,
      id: pq.id,
    })),
    ...history.map((h) => ({
      type: "current" as const,
      query: h.query,
      sql: h.sql,
      duration_ms: 0,
      id: String(h.timestamp),
    })),
  ];

  const showEmpty = allItems.length === 0 && !loading && !error;

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Ask a Question</h1>
        <p className="text-sm text-muted-foreground">
          Ask a natural language question about your data
        </p>
      </div>

      <div className="flex flex-col gap-6">
        {showEmpty && (
          <div className="flex flex-col items-center gap-2 py-16 text-center">
            <div className="text-5xl">&#x1F50D;</div>
            <p className="text-lg font-medium">Ask anything about your data</p>
            <p className="text-sm text-muted-foreground max-w-md">
              Try asking questions like &quot;show me active users&quot;,
              &quot;total revenue by quarter&quot;, or
              &quot;list products out of stock&quot;
            </p>
          </div>
        )}

        {pastQueries.length > 0 && (
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              Recent Queries
            </p>
            {pastQueries.slice(0, 5).map((pq) => (
              <button
                key={pq.id}
                onClick={() => handleSend(pq.query)}
                className="w-full rounded-lg border p-3 text-left text-sm transition-colors hover:bg-accent"
              >
                <span className="font-medium">{pq.query}</span>
                <span className="ml-2 text-xs text-muted-foreground">
                  {pq.duration_ms.toFixed(0)}ms
                </span>
                {pq.sql && (
                  <p className="mt-0.5 line-clamp-1 font-mono text-xs text-muted-foreground">
                    {pq.sql}
                  </p>
                )}
              </button>
            ))}
          </div>
        )}

        {history.map((h, i) => (
          <ChatMessage
            key={`h-${i}`}
            query={h.query}
            result={{ success: true, query: h.query, sql: h.sql, status: "success", stages: [], total_duration_ms: 0 }}
          />
        ))}

        {loading && (
          <ChatMessage
            query={history[0]?.query ?? ""}
            loading={true}
          />
        )}

        {currentResult && !loading && (
          <ChatMessage
            query={history[0]?.query ?? ""}
            result={currentResult}
            error={error}
          />
        )}

        {error && !loading && !currentResult && (
          <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-sm text-destructive">
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="sticky bottom-0 bg-background pb-4 pt-2">
        <ChatInput onSend={handleSend} disabled={loading || !token} />
      </div>
    </div>
  );
}
