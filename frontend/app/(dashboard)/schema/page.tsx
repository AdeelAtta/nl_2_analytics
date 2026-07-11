"use client";

import { SchemaBrowser } from "@/components/schema/SchemaBrowser";

export default function SchemaPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Schema Browser</h1>
        <p className="text-sm text-muted-foreground">
          Browse database tables and columns
        </p>
      </div>
      <SchemaBrowser />
    </div>
  );
}
