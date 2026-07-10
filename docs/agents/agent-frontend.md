# Agent: Frontend

| Metadata | Value |
|----------|-------|
| **Agent ID** | AGENT-FRONTEND |
| **Owns Epics** | EP-014 |
| **Workspace** | `/frontend/` |
| **Reads** | `/docs/epics/EP-014`, `/docs/API-Design.md` |

---

## Responsibilities

1. Scaffold Next.js 15 project with App Router
2. Install and configure shadcn/ui + Tailwind CSS
3. Implement design system (themes, tokens, typography)
4. Build API client library (auto-generated from OpenAPI)
5. Implement Zustand state management stores
6. Build chat interface (primary interaction mode)
7. Build schema browser (database tree explorer)
8. Build query history sidebar
9. Build settings pages
10. Build admin dashboard
11. Build authentication UI

## Workspace Boundaries

```
/frontend/
  /src/
    /app/                   -> Next.js app router pages
      /login/               -> Login page
      /dashboard/           -> Main dashboard
      /chat/                -> Chat page
      /schema/              -> Schema browser page
      /settings/            -> Settings pages
      /admin/               -> Admin dashboard
      layout.tsx            -> Root layout
    /components/
      /ui/                  -> shadcn/ui primitives
      /chat/
        ChatInput.tsx
        ChatMessage.tsx
        ChatHistory.tsx
        ResultTable.tsx
        SqlDisplay.tsx
      /schema/
        DatabaseTree.tsx
        TableView.tsx
        ColumnDetail.tsx
      /history/
        HistoryList.tsx
        HistoryItem.tsx
      /settings/
        DatabaseForm.tsx
        ProfileForm.tsx
        TeamForm.tsx
      /admin/
        UsageChart.tsx
        TeamTable.tsx
        BillingPanel.tsx
    /lib/
      /api-client/
        client.ts           -> API client
        queries.ts          -> Query hooks
        schemas.ts          -> Schema hooks
      /state/
        auth-store.ts       -> Zustand auth store
        query-store.ts      -> Zustand query store
        schema-store.ts     -> Zustand schema store
        history-store.ts    -> Zustand history store
        settings-store.ts   -> Zustand settings store
    /styles/
      globals.css
    /types/
      api.ts                -> API type definitions
```

## DO NOT Touch

- `/backend/`
- `/infra/`
- `/research/`

## Prompts

### Chat Interface Prompt
```
Build the main chat interface component.

Create ChatPage.tsx with:
- Message list (scrollable, auto-scroll to bottom)
- Chat input with submit on Enter
- Message types: user (query), assistant (SQL + results), error, loading
- SQL results rendered in table format with column headers
- Syntax-highlighted SQL display
- Copy SQL button
- Feedback buttons (thumbs up/down) on each assistant message

Use shadcn/ui components: Card, Button, Textarea, ScrollArea, Table
Use Zustand query-store for state management
Reference EP-014 for acceptance criteria.
```

## Definition of Done
- All pages render without errors
- Chat interface functional (type query, see results)
- Schema browser shows database tree
- Auth flow works end-to-end
- Lighthouse score > 90
- Test coverage > 70%
- All task status files updated
