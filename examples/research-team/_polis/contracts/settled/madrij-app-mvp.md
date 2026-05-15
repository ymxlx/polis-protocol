---
contract_id: madrij-app-mvp
title: Companion web app — assign reading order per janij group
opened_by: codex-frontend-pesaj
opened_at: 2026-04-28 09:40:00
owner: codex-frontend-pesaj
status: settled
stakes: high
required_tags: [react-component-design, css-responsive-layout, typescript]
deadline: 2026-04-30
cost_ceiling: low
acceptance_criteria:
  - Madrij can log in, create a janij group, drag-reorder readings.
  - Mobile-first; works on a phone in shul lighting.
  - axe-core a11y pass (no violations above "moderate").
routing:
  recommended_by_router: codex-frontend-pesaj
  recommendation_score: 0.520
  exploration: false
  override: null
review:
  required: true
  reviewer: claude-research-pesaj
  status: signed_off
settled_at: 2026-04-30 22:15:00
quality_score: 4
actual_minutes: 480
---

# Companion web app: assign reading order per janij group

## Intent

### Goal
Madrijim need a way to assign which sources their janij group reads, in what
order, without printing 1,200 customized packets. Web app, mobile-first.

### Acceptance criteria
- Login, group creation, drag-to-reorder readings, share via link.
- Mobile-first; functional on a phone in shul lighting (high contrast).
- axe-core a11y check passes with no moderate-or-higher violations.

### Stakes rationale
This ships to production and parents/madrijim use it during peulot. A bug means
groups read the wrong material on the wrong week. High stakes; chavruta review
required.

## Assignment

### Plan
- Vite + React 19 + Tailwind. Supabase for auth + storage.
- Drag-reorder via dnd-kit (lighter than react-beautiful-dnd).
- One-day implementation, half-day a11y pass, half-day on the deploy + smoke.

## Settlement

### Outcome
Shipped to staging on time. Claude's review caught two a11y issues (focus ring
contrast in dark mode, drag-handle missing aria-label) that I fixed before the
prod cut. The drag-reorder works on iOS Safari, which was the risky case.

### What worked
- Chavruta review caught the a11y misses I would have shipped.
- dnd-kit was the right call; one less dependency than the alternative.

### What bit
- Spent 30 minutes on Supabase RLS policy I should have copied from the
  template repo. Lesson filed.

### Lesson reference
[[lessons/long-context-reading/2026-03-02-citation-graph-pattern]] (unrelated;
no new lesson filed — RLS-policy mistake is well-covered in the Supabase docs
already).
