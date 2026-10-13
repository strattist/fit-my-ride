---
title: 'Story 1.1: Project scaffold with one quality gate'
type: 'feature'
created: '2026-10-13'
status: 'in-review'
baseline_commit: 'd5cd3d84ec615dc55e97e2d727dec20d69ae8e77'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/docs/architecture.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** There is no runnable project, hook or CI yet, so parallel agents have no shared definition of "green" and nothing enforces the layer boundaries.

**Approach:** Scaffold the uv-managed `fit_my_ride` package with the six layers and `data/ingested/`, one smoke test and one import-boundary test (written first), a pre-commit config and a GitHub Actions workflow running the same three commands, and replace the TODO lines in `AGENTS.md` with the real commands.

## Boundaries & Constraints

**Always:**
- Test-first: write the smoke test and the import-boundary test, watch them fail for the right reason, then scaffold until green.
- Python `>=3.13`, src layout `src/fit_my_ride/{core,adapters,ingestion,catalog,web,cli}`, committed `uv.lock`.
- The gate is exactly: `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest`; hook and CI use these same commands.
- Boundary rules (AD-1): `core` imports only the standard library and itself; `web` never imports `ingestion` or `adapters`; `ingestion` never imports `web`.

**Never:**
- No `git commit` or `git push`; leave changes in the working tree.
- No domain code (schema, units, fit, routes, adapters): packages stay empty beyond `__init__.py`.
- No Dockerfile, no htmx or font assets, no CLI entry points (later stories).
- No edits to `docs/`, `epics.md` or `sprint-status.yaml`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Fresh clone | `uv sync` then `uv run pytest` | install succeeds; smoke test and boundary test pass | N/A |
| Layout | scaffold present | all six packages importable; `data/ingested/` exists (tracked via `.gitkeep`) | N/A |
| Core violation | a `core` module imports `fastapi` or `fit_my_ride.web` | boundary test fails naming file and import | test red |
| Web violation | a `web` module imports `fit_my_ride.ingestion` or `.adapters` | boundary test fails naming file and import | test red |
| Ingestion violation | an `ingestion` module imports `fit_my_ride.web` | boundary test fails naming file and import | test red |
| Hook | staged change fails ruff or pytest | `pre-commit` rejects the commit | non-zero exit |

</frozen-after-approval>

## Code Map

- `AGENTS.md` -- two TODO lines (Policy bullet "TODO until story 1.1 lands", section "Running and verifying") to replace with the real commands and hook/CI description.
- `.gitignore` -- already ignores `.venv/`, `__pycache__/`; add `.pytest_cache/`, `.ruff_cache/`.
- `docs/architecture.md` "Structural Seed" -- target layout; `src/fit_my_ride/` with `tests/` and `fixtures/` at root.
- Nothing else exists: greenfield, no `pyproject.toml`, hook or workflow. System has uv 0.12 and Python 3.12/3.14 only (uv fetches 3.13+ per `requires-python`); `pre-commit` is not installed, so make it a dev dependency.

## Tasks & Acceptance

**Execution:**
- [x] `tests/test_smoke.py` -- test that `fit_my_ride` and its six subpackages import -- first red test
- [x] `tests/test_import_boundaries.py` -- AST-scan `src/fit_my_ride/**` and assert the three boundary rules, failing with file and import named; include a small self-test using temp files proving each rule detects a violation -- guards AD-1
- [x] `pyproject.toml` -- project metadata, `requires-python >=3.13`, runtime deps `fastapi`, `pdfplumber`, dev group `pytest`, `ruff`, `pre-commit`, ruff and pytest config (`testpaths = tests`), build backend so the package imports -- one definition of tooling
- [x] `src/fit_my_ride/{__init__,core,adapters,ingestion,catalog,web,cli}/__init__.py` -- empty package skeleton
- [x] `data/ingested/.gitkeep`, `fixtures/.gitkeep` -- tracked empty folders
- [x] `.pre-commit-config.yaml` -- local hooks running the three gate commands via `uv run`
- [x] `.github/workflows/ci.yml` -- on push and pull request: setup-uv, `uv sync --locked`, the same three commands
- [x] `.gitignore` -- add tool caches
- [x] `AGENTS.md` -- replace both TODOs with the actual commands (`uv sync`, `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`), the hook and CI

**Acceptance Criteria:**
- Given a fresh clone, when I run `uv sync` and `uv run pytest`, then install succeeds and all tests pass.
- Given the scaffold, when I list `src/fit_my_ride` and `data/ingested`, then the six packages and the folder exist.
- Given `pre-commit run --all-files`, when the tree is clean, then ruff and pytest hooks pass; a failing change makes it exit non-zero.
- Given the workflow file, when read, then it runs the same commands as the hook.
- Given `AGENTS.md`, when read, then no TODO about hook, CI or run commands remains.

## Implementation Notes

- Implemented directly (no subagent). Red run: 7 smoke tests failed (`ModuleNotFoundError: fit_my_ride`); boundary tests were vacuously green on empty layers, so each rule has a self-test proving a violation is detected, and manual probes (`import fastapi` in `core`, `adapters` import in `web`) turned the guard red.
- `ruff` is configured with `extend-exclude = ["_bmad", "_bmad-output"]`: BMad installer scripts in `_bmad/` otherwise fail the gate.
- `.pre-commit-config.yaml` not installed into `.git/hooks`; AGENTS.md tells each clone to run `uv run pre-commit install`. `uv run pre-commit run --all-files` passes.
- Also touched `_bmad-output/implementation-artifacts/sprint-status.yaml` (story and epic set to in-progress) per the build workflow.

## Spec Change Log

## Review Triage Log

## Design Notes

Boundary test sketch: parse each `.py` with `ast`, collect `Import`/`ImportFrom` top-level modules; for `core`, allowed = `sys.stdlib_module_names` plus `fit_my_ride.core`; for `web`, forbidden prefixes `fit_my_ride.ingestion`, `fit_my_ride.adapters`; for `ingestion`, forbidden `fit_my_ride.web`. Relative imports resolve against the file's package first. Adapters-depend-only-on-core is not enforced here (spine lists it, story AC does not); note for a later story.

## Verification

**Commands:**
- `uv sync && uv run pytest` -- expected: all tests pass
- `uv run ruff check . && uv run ruff format --check .` -- expected: no findings
- `uv run pre-commit run --all-files` -- expected: all hooks pass
