<!-- bmad:context -->
<!-- Verified 2026-09-27 — pre-first-commit (repo has no commits yet; next refresh records the real SHA). Managed by bmad-project-context; edits inside this block are replaced on refresh. Keep anything you want preserved outside the markers. -->

## Fit my Ride

Self-hosted PWA web app (≤5 users) matching a rider's body measurements against vendor bike geometry via a heatmap. Hobby project, built by two people using multiple AI coding agents in parallel. Stack not yet chosen — see `docs/architecture.md` once it exists. Planning lives in `_bmad-output/` (BMad's working drafts); finalized docs are promoted to `docs/`.

## Policy

- Never `git commit` or `git push` — stage changes at most; the user reviews and commits/pushes themselves.
- Parallel AI agents each work in their own git worktree — never have more than one agent edit the shared main checkout directly; merge worktrees back via normal git.
- Build test-first (red, green, refactor): write a failing test per acceptance scenario before the code. Spikes, written decisions, documents and operational runs are exempt; each story's `**Delivery:**` line says which. Rules: "Story Delivery Rules" in `_bmad-output/planning-artifacts/epics.md`.
- Every stack choice ships with CI and a pre-commit hook (lint, format, tests appropriate to the chosen language) — required regardless of which stack architecture picks; currently TODO since no stack is chosen yet.

## Where things are

- Planning drafts and BMad working state: `_bmad-output/` (brainstorming, briefs, PRDs)
- Official finalized docs: `docs/` — currently `docs/product-brief.md`, `docs/prd.md`

## Known pitfalls

- `_bmad-output/` holds BMad's working drafts — commit discipline there is manual/selective; don't assume it's fully tracked or always in sync with `docs/`.

<!-- /bmad:context -->
