# TASK-114: Scaffold Next.js 15 Project

| Metadata | Value |
|----------|-------|
| **Task ID** | TASK-114 |
| **Epic** | EP-014 |
| **Priority** | P0 |
| **Complexity** | M |
| **Dependencies** | EP-001 |
| **Agent Owner** | Frontend Agent |
| **Status** | backlog |

---

## Description

Scaffold the Next.js 15 frontend project with App Router, TypeScript, ESLint, and Tailwind CSS.

## Inputs

- EP-014 epic definition
- Frontend directory structure from Implementation-Plan.md

## Implementation

1. Initialize Next.js 15 project:
   ```
   npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir
   ```

2. Install dependencies:
   - shadcn/ui: `npx shadcn@latest init`
   - zustand: `npm install zustand`
   - openapi-typescript: `npm install -D openapi-typescript`
   - Additional shadcn components: button, card, input, textarea, table, dialog, scroll-area, select, badge, separator, tabs, sheet, tooltip, dropdown-menu, avatar

3. Configure:
   - `tsconfig.json` path aliases (`@/*`)
   - Tailwind CSS config with design tokens
   - ESLint config for React + TypeScript

4. Create directory structure:
   - `/frontend/src/app/` (page routes)
   - `/frontend/src/components/` (React components)
   - `/frontend/src/lib/` (utilities, API client, state)
   - `/frontend/src/styles/` (global CSS)
   - `/frontend/src/types/` (TypeScript type definitions)

## Outputs

- Full Next.js 15 project scaffold

## Acceptance Criteria

- [ ] `npm run dev` starts the dev server
- [ ] Default Next.js page renders
- [ ] shadcn/ui components render correctly (test with Button)
- [ ] TypeScript compilation passes with no errors
- [ ] Tailwind classes work correctly
- [ ] Path aliases work (`@/components/ui/button`)

## Definition of Done

- Dev server starts and renders
- shadcn/ui initialized
- TypeScript compiles clean
- Task status updated to `done`
