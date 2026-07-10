import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const stats = [
  { title: "Total Queries", value: "—", description: "Coming in Sprint 1" },
  { title: "Active Connections", value: "—", description: "Coming in Sprint 1" },
  { title: "Schema Objects", value: "—", description: "Coming in Sprint 2" },
  { title: "Team Members", value: "—", description: "Coming in Sprint 3" },
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Welcome to OpenQuery</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stat.value}</div>
              <CardDescription>{stat.description}</CardDescription>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Coming in Sprint 1</CardTitle>
          <CardDescription>
            Query execution, result visualization, and connection management will be available in the
            first development sprint.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            The Enterprise Data Intelligence Platform is currently under active development.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
