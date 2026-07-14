import { create } from "zustand";

export interface StageResult {
  name: string;
  status: string;
  duration_ms: number;
  error?: string;
}

export interface ColumnInfo {
  name: string;
  type: string;
  table: string;
}

export interface QueryResult {
  success: boolean;
  query: string;
  sql: string;
  status: string;
  error?: string;
  explanation?: string;
  columns?: ColumnInfo[];
  stages: StageResult[];
  total_duration_ms: number;
  session_id?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  result?: QueryResult | null;
  loading?: boolean;
  error?: string | null;
}

interface SessionInfo {
  session_id: string;
  started_at: string;
  query_count: number;
}

interface QueryState {
  messages: ChatMessage[];
  loading: boolean;
  activeDb: string;
  sessionId: string;
  activeSessionId: string;
  databases: { name: string; database: string; table_count: number }[];
  sessions: SessionInfo[];
  addMessage: (msg: ChatMessage) => void;
  updateLastAssistant: (update: Partial<ChatMessage>) => void;
  execute: (query: string, token: string, db?: string, dryRun?: boolean) => Promise<void>;
  loadHistory: (token: string, db?: string, sessionId?: string) => Promise<void>;
  loadDatabases: (token: string) => Promise<void>;
  loadSessions: (token: string, db?: string) => Promise<void>;
  setActiveDb: (db: string) => void;
  setActiveSessionId: (sid: string) => void;
  clearConversation: () => void;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100/api/v1";

let msgId = 0;
const nextId = () => `msg_${Date.now()}_${++msgId}`;

export const useQueryStore = create<QueryState>()((set, get) => ({
  messages: [],
  loading: false,
  activeDb: "",
  sessionId: "",
  activeSessionId: "",
  databases: [],
  sessions: [],

  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),

  updateLastAssistant: (update) =>
    set((s) => {
      const msgs = [...s.messages];
      for (let i = msgs.length - 1; i >= 0; i--) {
        if (msgs[i].role === "assistant") {
          msgs[i] = { ...msgs[i], ...update };
          break;
        }
      }
      return { messages: msgs };
    }),

  execute: async (query: string, token: string, db?: string, dryRun?: boolean) => {
    if (!query.trim()) return;

    const userMsg: ChatMessage = { id: nextId(), role: "user", content: query };
    const assistantMsg: ChatMessage = {
      id: nextId(),
      role: "assistant",
      content: "",
      loading: true,
      error: null,
      result: null,
    };

    set((s) => ({ messages: [...s.messages, userMsg, assistantMsg], loading: true }));

    try {
      const body: Record<string, unknown> = {
        query,
        dry_run: dryRun ?? true,
        database: db || get().activeDb,
      };
      const sid = get().sessionId;
      if (sid) body.session_id = sid;

      const res = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`API Error [${res.status}]: ${text}`);
      }
      const data: QueryResult = await res.json();
      if (data.session_id) set({ sessionId: data.session_id, activeSessionId: data.session_id });
      get().updateLastAssistant({ result: data, loading: false, error: null });
      set({ loading: false });
      get().loadHistory(token, get().activeDb, get().activeSessionId);
    } catch (e) {
      get().updateLastAssistant({
        loading: false,
        error: (e as Error).message,
        result: null,
      });
      set({ loading: false });
    }
  },

  loadHistory: async (token: string, db?: string, sessionId?: string) => {
    try {
      const params = new URLSearchParams();
      params.set("page_size", "50");
      const activeDatabase = db || get().activeDb;
      if (activeDatabase) params.set("database", activeDatabase);
      const activeSession = sessionId || get().activeSessionId;
      if (activeSession) params.set("session_id", activeSession);
      const res = await fetch(`${API_URL}/history?${params.toString()}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        const historyItems = data.data ?? [];
        const messages: ChatMessage[] = [];
        for (let i = historyItems.length - 1; i >= 0; i--) {
          const item = historyItems[i];
          messages.push({
            id: `hist-user-${item.id}`,
            role: "user",
            content: item.query,
          });
          messages.push({
            id: `hist-asst-${item.id}`,
            role: "assistant",
            content: item.sql || "",
            result: {
              success: item.status === "success",
              query: item.query,
              sql: item.sql || "",
              status: item.status,
              stages: [],
              total_duration_ms: item.duration_ms || 0,
            },
            loading: false,
            error: item.status !== "success" ? "Query failed" : null,
          });
        }
        set({ messages });
      }
    } catch (e) {
      console.error("Failed to load history:", e);
    }
  },

  clearConversation: () => set({ messages: [], loading: false, sessionId: "" }),

  resetStore: () => set({
    messages: [], loading: false, activeDb: "", sessionId: "",
    activeSessionId: "", databases: [], sessions: [],
  }),

  loadSessions: async (token: string, db?: string) => {
    try {
      const activeDatabase = db || get().activeDb;
      const url = activeDatabase ? `${API_URL}/history/sessions?database=${encodeURIComponent(activeDatabase)}` : `${API_URL}/history/sessions`;
      const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) {
        const data = await res.json();
        set({ sessions: data.data ?? [] });
      }
    } catch (e) { console.error("Failed to load sessions:", e); }
  },

  setActiveSessionId: (sid: string) => set({ activeSessionId: sid }),

  loadDatabases: async (token: string) => {
    try {
      const res = await fetch(`${API_URL}/schema/databases`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        set({ databases: data.data ?? [] });
      }
    } catch (e) {
      console.error("Failed to load databases:", e);
    }
  },

  setActiveDb: (db: string) => set({ activeDb: db }),
}));
