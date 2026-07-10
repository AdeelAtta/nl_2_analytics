import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function SchemaPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Schema Browser</h1>
        <p className="text-muted-foreground">Browse database schemas, tables, and columns</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Coming in Sprint 2</CardTitle>
          <CardDescription>
            The schema browser with tree view, column details, and relationship diagrams will be
            available in Sprint 2.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-64 items-center justify-center rounded-lg border-2 border-dashed border-muted-foreground/25">
            <p className="text-lg text-muted-foreground">Schema Browser — Coming in Sprint 2</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
