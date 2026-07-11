"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { QueryResult, StageResult } from "@/stores/query";

interface ChatMessageProps {
  query: string;
  result?: QueryResult | null;
  loading?: boolean;
  error?: string | null;
}

export function ChatMessage({ query, result, loading, error }: ChatMessageProps) {
  return (
    <div className="space-y-3">
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-2xl bg-primary px-4 py-2 text-sm text-primary-foreground">
          {query}
        </div>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <div className="h-3 w-3 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          Processing...
        </div>
      )}

      {result && (
        <div className="max-w-[90%] space-y-3">
          {result.sql && (
            <Card>
              <CardContent className="p-3">
                <pre className="overflow-x-auto text-sm font-mono">{result.sql}</pre>
              </CardContent>
            </Card>
          )}

          {result.stages && result.stages.length > 0 && (
            <div className="rounded-lg border p-3">
              <p className="mb-2 text-xs font-medium text-muted-foreground">Pipeline</p>
              <div className="space-y-1.5">
                {result.stages.map((s: StageResult, i: number) => (
                  <div key={i}>
                    {i > 0 && <Separator className="my-1" />}
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-1.5">
                        <span className={`h-1.5 w-1.5 rounded-full ${
                          s.status === "success" || s.status === "dry_run"
                            ? "bg-green-500"
                            : s.status === "skipped"
                              ? "bg-yellow-400"
                              : "bg-red-500"
                        }`} />
                        <span className="font-medium capitalize">{s.name}</span>
                      </div>
                      <span className="text-muted-foreground">{s.duration_ms.toFixed(0)}ms</span>
                    </div>
                  </div>
                ))}
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                Total: {result.total_duration_ms.toFixed(0)}ms
              </p>
            </div>
          )}

          {result.error && (
            <div className="rounded-lg border border-destructive bg-destructive/10 p-3">
              <p className="text-xs text-destructive">{result.error}</p>
            </div>
          )}
        </div>
      )}

      {error && !loading && (
        <div className="max-w-[90%] rounded-lg border border-destructive bg-destructive/10 p-3">
          <p className="text-xs text-destructive">{error}</p>
        </div>
      )}
    </div>
  );
}
