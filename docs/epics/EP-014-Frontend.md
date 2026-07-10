# EP-014: Frontend Application

Epic ID: **EP-014** | Priority: **P1** | Dependencies: **EP-013** | Complexity: **XL** | Agent: **Frontend Agent**

---

Build the web application — a modern React 19 + Next.js 15 interface that provides the primary user experience for the platform.

## Goals
- Next.js 15 app with App Router
- shadcn/ui component library + Tailwind CSS
- Chat interface (primary interaction mode)
- Schema browser (explore connected databases)
- Query history sidebar
- Settings pages (user, team, database connections)
- Admin dashboard (team management, usage metrics, billing)
- Design system with consistent tokens
- Zustand for state management
- Dark/light theme support

## Out of Scope
- Backend API logic
- Real-time collaboration
- Mobile native app

## Tasks

| ID | Name | P | Deps | Est |
|----|------|---|---|-----|
| TASK-114 | Scaffold Next.js 15 project | P0 | EP-001 | M |
| TASK-115 | Install and configure shadcn/ui + Tailwind | P0 | TASK-114 | M |
| TASK-116 | Implement design system (themes, tokens, typography) | P0 | TASK-115 | L |
| TASK-117 | Build API client library | P0 | TASK-114, EP-013 | L |
| TASK-118 | Implement Zustand state management stores | P0 | TASK-114 | L |
| TASK-119 | Build chat interface | P0 | TASK-117 | XL |
| TASK-120 | Build schema browser | P1 | TASK-117 | L |
| TASK-121 | Build query history sidebar | P1 | TASK-117 | M |
| TASK-122 | Build settings pages | P1 | TASK-117 | L |
| TASK-123 | Build admin dashboard | P2 | TASK-117 | XL |
| TASK-124 | Build authentication UI | P0 | TASK-117 | M |
| TASK-125 | Write unit and integration tests | P0 | TASK-119 | XL |

## Acceptance Criteria
- Chat interface renders with message list and input
- SQL query results displayed in tabular format
- Schema browser shows database tree (DB -> schema -> table -> columns)
- Query history shows past queries with status indicators
- User can configure database connections
- Admin dashboard shows usage metrics and team members
- Auth flow: login -> redirect -> session persistence
- Dark/light theme works across all pages

## Definition of Done
- All pages render without errors
- E2E test: user types query -> sees results
- Lighthouse score > 90
- Test coverage > 70%
