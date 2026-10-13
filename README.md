# Fit my Ride

Self-hosted PWA (up to 5 users) that matches a rider's body measurements against vendor bike geometry and shows the result as a heatmap table.

Stack: Python 3.13+, uv, FastAPI + htmx, SQLite, ruff + pytest, one Docker container. Early stage: the scaffold, the canonical schema and units are in place; evaluators, ingestion and the web app are still to come.

## Commands

| Task | Command |
|------|---------|
| Install dependencies | `uv sync` |
| Run tests | `uv run pytest` |
| Lint | `uv run ruff check .` |
| Check formatting | `uv run ruff format --check .` |
| Apply formatting | `uv run ruff format .` |
| Enable the pre-commit hook (once per clone) | `uv run pre-commit install` |
| Run the hook on everything | `uv run pre-commit run --all-files` |

The gate is the three commands `ruff check`, `ruff format --check` and `pytest`; the pre-commit hook and CI (pull requests, and pushes to `main`) run exactly these.

## Layout

| Path | What it holds |
|------|---------------|
| `src/fit_my_ride/core/` | Pure logic, no I/O: `schema` (parameters, bike id), `units` (conversion to cm) |
| `src/fit_my_ride/{adapters,ingestion,catalog,web,cli}/` | Vendor adapters, PDF ingestion, catalog loader, web app, CLI |
| `tests/` | pytest suite; `test_import_boundaries.py` enforces the layer rules |
| `data/ingested/` | Approved catalog files, changed only through ingest and review |
| `fixtures/` | Committed fixture excerpts for tests |
| `docs/` | Product brief, PRD, `architecture.md` (decisions AD-1 to AD-12), `ux/` |
| `AGENTS.md` | Rules for AI agents working in this repo |
| `_bmad-output/` | BMad planning drafts: `planning-artifacts/epics.md` (stories), `implementation-artifacts/sprint-status.yaml` (status) |
| `.pre-commit-config.yaml`, `.github/workflows/ci.yml` | The quality gate |
