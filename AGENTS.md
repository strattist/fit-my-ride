<!-- bmad:context -->
<!-- Verified 2026-10-13 against 98dac70. Managed by bmad-project-context; edits inside this block are replaced on refresh. Keep anything you want preserved outside the markers. -->

## Fit my Ride

Self-hosted PWA web app (≤5 users) matching a rider's body measurements against vendor bike geometry via a heatmap. Hobby project, built by two people using multiple AI coding agents in parallel. Stack decided, not scaffolded yet: Python 3.13+, uv, FastAPI + htmx, SQLite, ruff + pytest, one Docker container. Planning lives in `_bmad-output/` (BMad's working drafts); finalized docs are promoted to `docs/`.

## Policy

- Never `git commit` or `git push` — stage changes at most; the user reviews and commits/pushes themselves.
- Parallel AI agents each work in their own git worktree — never have more than one agent edit the shared main checkout directly; merge worktrees back via normal git.
- Build test-first (red, green, refactor): write a failing test per acceptance scenario before the code. Spikes, written decisions, documents and operational runs are exempt; each story's `**Delivery:**` line says which. Rules: "Story Delivery Rules" in `_bmad-output/planning-artifacts/epics.md`.
- Every stack choice ships with CI and a pre-commit hook (lint, format, tests appropriate to the chosen language). Here: `.pre-commit-config.yaml` runs `ruff check`, `ruff format --check` and `pytest` via `uv run`, and `.github/workflows/ci.yml` runs the same three commands. Enable the hook once per clone with `uv run pre-commit install`.

## Where things are

- Planning drafts and BMad working state: `_bmad-output/` (brainstorming, briefs, PRDs)
- Official finalized docs: `docs/` — `product-brief.md`, `prd.md`, `architecture.md` (decisions AD-1…AD-12), `ux/` (DESIGN.md, EXPERIENCE.md, mockups)
- Stories and acceptance criteria: `_bmad-output/planning-artifacts/epics.md`; status: `_bmad-output/implementation-artifacts/sprint-status.yaml`
- Spec and glossary (domain terms: Core/Optional Parameter, Heatmap Table, Provenance): `_bmad-output/specs/spec-to-choose/`

## Running and verifying

- Setup: `uv sync` (Python 3.13+, dev tools included).
- Gate, run before handing work over (identical in hook and CI): `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest`. Apply formatting with `uv run ruff format .`.
- `tests/test_import_boundaries.py` enforces the layer boundaries below; `_bmad/` and `_bmad-output/` are excluded from ruff.

## Conventions that differ from defaults

- `core/` does no I/O (no file, network, database, clock, env); `web/` never imports `ingestion/` or `adapters/`, and `ingestion/` never imports `web/`.
- Catalog changes only via ingest → review/approve → `data/ingested/` files in git → `catalog load`; never hand-edit approved files, never write SQLite from `web/`.
- LLM calls only through `ingestion/llm`; API keys never in the repo or image.
- Unit conversion lives only in `core/units`, exclusion and best-size choice only in `core/fit`; adapters and templates never decide them.
- Never store or log rider measurements; access logs record the request path, not the query string.

## Known pitfalls

- `_bmad-output/` holds BMad's working drafts — commit discipline there is manual/selective; don't assume it's fully tracked or always in sync with `docs/`.

<!-- /bmad:context -->
