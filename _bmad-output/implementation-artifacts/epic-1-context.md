# Epic 1 Context: Fit judgment you can trust

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Builders can ask "does this bike's geometry fit this rider?" and get a deterministic, tested answer for each of the 5 Core Parameters before any real data or UI exists. The epic delivers the project scaffold, the canonical schema and units, the per-parameter fit evaluators and fit results, plus a small CLI that runs a rider against fixture bikes.

## Stories

- Story 1.1: Project scaffold with one quality gate
- Story 1.2: Canonical schema and units
- Story 1.3: Rider input and the evaluator seam
- Story 1.4: Stack and Reach evaluators
- Story 1.5: Decide HTA, STA and BB
- Story 1.6: Fit results, exclusion and ordering
- Story 1.7: Try a rider against fixture bikes from the CLI

## Requirements & Constraints

- Greenfield: no starter template. uv-managed Python 3.13+ project (FastAPI, htmx 2.x, SQLite, ruff, pytest, pdfplumber).
- Everything is built test-first (red, green, refactor), one failing scenario test at a time, through public interfaces; no mocking of `core`.
- One quality gate: `ruff` (lint + format) and `pytest`, run by a single pre-commit config and by identical GitHub Actions commands.
- Core logic must be testable without a database, network, browser or LLM.
- A bike is excluded only when a Core Parameter with a defined evaluator is out of range; a parameter without an evaluator is `unknown` and never excludes. No weighted or composite score; In-Range Count is the only aggregate and counts only evaluated parameters.
- Missing values are explicit (`null` + reason), never omitted, never zero.
- Agents never commit or push; each works in its own git worktree.

## Technical Decisions

- Functional core / imperative shell. Package layout under `src/fit_my_ride/`: `core/ adapters/ ingestion/ catalog/ web/ cli/`; approved data in `data/ingested/<vendor>/`; `tests/` and `fixtures/` at the root; Dockerfile, `.pre-commit-config.yaml`, `.github/workflows/` ship with the scaffold.
- Dependency direction is fixed: `core` imports nothing outside itself; `web` never imports `ingestion` or `adapters`; `ingestion` never imports `web`; adapters depend only on `core`. A test enforces this.
- `core/` has no file, network, database, clock or environment access.
- All shared types live in `core/schema`: canonical record, Usage Taxonomy (road, gravel, MTB, city/commute, touring, e-bike), `RiderInput` (`height_cm`, `inseam_cm`, `style`), `CellState`, approved-file format.
- Core Parameters: HTA (deg), S (cm), R (cm), STA (deg), BB (cm). Optional (all cm): seat tube length, head tube length, top tube length, chainstay length, fork length, fork rake, wheel base. Lengths stored in cm, angles in degrees.
- Unit conversion only in `core/units` (cm to 0.1 precision; unknown unit raises a typed error).
- Bike id is `<vendor_slug>:<model_slug>[:<model_year>]`, slug from one core function; sizes carry the vendor label plus an explicit sort order. Vendor slugs are lowercase (`ktm`, `van_rysel`).
- `core/fit`: one evaluator per Core Parameter returning `unknown` or a signed deviation from the ideal range (0 in range, negative too short, positive too long). Exclusion and best-size choice (fewest out-of-range, then smallest total absolute deviation, then vendor size order) are decided only there; replacing one evaluator changes no other parameter.
- Rider input ranges: height 120-230 cm, inseam 50-120 cm.
- CLI output: words not colour alone, honour `NO_COLOR`; shells raise or exit non-zero, core returns typed results.
- Never store or log rider measurements.

## Cross-Story Dependencies

- 1.1 must land first: every later story (and every agent) relies on its quality gate and package layout.
- 1.2 (schema, units) underpins 1.3-1.7; 1.3 provides the evaluator seam used by 1.4 and 1.5, which feed 1.6; 1.7 composes 1.6 over fixture bikes.
- 1.4 requires `docs/fit-rules.md` approved by Baptiste before its evaluators are written; 1.5 records HTA/STA/BB decisions in the same document.
- A 1.5 decision needing a new rider input adds a story to Epic 4 rather than expanding Epic 1.
- Epic 2 consumes the schema and approved-file shapes; Epic 4 reuses `core/fit` unchanged.
