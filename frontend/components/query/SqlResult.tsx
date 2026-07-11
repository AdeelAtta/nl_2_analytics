"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { QueryResult } from "@/stores/query";

interface SqlResultProps {
  result: QueryResult;
}

export function SqlResult({ result }: SqlResultProps) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Generated SQL</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="overflow-x-auto rounded bg-muted p-3 text-sm font-mono">
            {result.sql || "(no SQL generated)"}
          </pre>
        </CardContent>
      </Card>

      {result.stages && result.stages.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Pipeline Stages</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {result.stages.map((s, i) => (
                <div key={i}>
                  {i > 0 && <Separator className="my-2" />}
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <span
                        className={`h-2 w-2 rounded-full ${
                          s.status === "success" || s.status === "dry_run"
                            ? "bg-green-500"
                            : s.status === "skipped"
                              ? "bg-yellow-400"
                              : "bg-red-500"
                        }`}
                      />
                      <span className="font-medium capitalize">{s.name}</span>
                    </div>
                    <span className="text-muted-foreground">{s.duration_ms.toFixed(1)}ms</span>
                  </div>
                  {s.error && <p className="mt-1 text-xs text-red-500">{s.error}</p>}
                </div>
              ))}
            </div>
            <div className="mt-3 flex items-center justify-between text-sm font-medium">
              <span>Total</span>
              <span>{result.total_duration_ms.toFixed(1)}ms</span>
            </div>
          </CardContent>
        </Card>
      )}

      {result.error && (
        <Card className="border-destructive">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-destructive">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-destructive">{result.error}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
