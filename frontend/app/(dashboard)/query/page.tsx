import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function QueryPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Query Editor</h1>
        <p className="text-muted-foreground">Write and execute SQL queries</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Coming in Sprint 1</CardTitle>
          <CardDescription>
            The SQL query editor with syntax highlighting, auto-complete, and result grids will be
            available in Sprint 1.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-64 items-center justify-center rounded-lg border-2 border-dashed border-muted-foreground/25">
            <p className="text-lg text-muted-foreground">Query Editor — Coming in Sprint 1</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
