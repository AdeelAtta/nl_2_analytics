"use client";

import { useEffect, useState } from "react";
import { useQueryStore } from "@/stores/query";
import { apiGet } from "@/lib/api";

interface HistoryItem {
  id: string; query: string; sql: string; status: string;
  duration_ms: number; has_feedback: boolean; created_at: string;
}

export function HistorySidebar() {
  const setQuery = useQueryStore((s) => s.setQuery);
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    apiGet<{ data: HistoryItem[] }>("/history?page_size=20").then((d) => {
      if (d) setItems(d.data ?? []);
    });
  }, []);

  return (
    <>
      <button
        onClick={() => setOpen(!open)}
        className="fixed right-4 top-4 z-50 rounded-full bg-primary p-2 text-primary-foreground shadow-lg text-xs"
      >
        {open ? "Close" : "History"}
      </button>
      {open && (
        <div className="fixed right-0 top-14 z-40 h-[calc(100vh-3.5rem)] w-80 border-l bg-background p-4 shadow-lg overflow-y-auto">
          <h3 className="mb-3 text-sm font-semibold">Query History</h3>
          {items.length === 0 && (
            <p className="text-sm text-muted-foreground">No queries yet</p>
          )}
          <div className="space-y-2">
            {items.map((item) => (
              <button
                key={item.id}
                onClick={() => { setQuery(item.query); setOpen(false); }}
                className="w-full rounded-lg border p-3 text-left transition-colors hover:bg-accent"
              >
                <p className="line-clamp-1 text-sm font-medium">{item.query}</p>
                <p className="mt-0.5 line-clamp-1 text-xs text-muted-foreground font-mono">{item.sql}</p>
                <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                  <span className={`h-1.5 w-1.5 rounded-full ${
                    item.status === "success" ? "bg-green-500" : "bg-red-500"
                  }`} />
                  <span>{item.duration_ms.toFixed(0)}ms</span>
                  {item.has_feedback && <span> &bull; feedback</span>}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
