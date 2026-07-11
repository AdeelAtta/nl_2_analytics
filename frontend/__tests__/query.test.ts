import { describe, it, expect, beforeEach } from "vitest";

process.env.NEXT_PUBLIC_API_URL = "http://localhost:8100/api/v1";

describe("Query Store", () => {
  beforeEach(async () => {
    const { useQueryStore } = await import("@/stores/query");
    useQueryStore.getState().clearResult();
    useQueryStore.getState().setQuery("");
  });

  it("starts with empty state", async () => {
    const { useQueryStore } = await import("@/stores/query");
    const state = useQueryStore.getState();
    expect(state.currentQuery).toBe("");
    expect(state.currentResult).toBeNull();
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
    expect(state.history).toEqual([]);
  });

  it("setQuery updates the query string", async () => {
    const { useQueryStore } = await import("@/stores/query");
    useQueryStore.getState().setQuery("show me users");
    expect(useQueryStore.getState().currentQuery).toBe("show me users");
  });

  it("clearResult resets result and error", async () => {
    const { useQueryStore } = await import("@/stores/query");
    // Simulate setting a result
    useQueryStore.setState({ currentResult: { success: true, query: "test", sql: "SELECT 1", status: "success", stages: [], total_duration_ms: 10 } });
    useQueryStore.getState().clearResult();
    expect(useQueryStore.getState().currentResult).toBeNull();
    expect(useQueryStore.getState().error).toBeNull();
  });
});
