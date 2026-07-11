"use client";

import { AdminDashboard } from "@/components/admin/AdminDashboard";

export default function AdminPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Admin</h1>
        <p className="text-sm text-muted-foreground">System monitoring and administration</p>
      </div>
      <AdminDashboard />
    </div>
  );
}
