---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - docs/prd.md
  - docs/product-brief.md
  - _bmad-output/planning-artifacts/prds/prd-to-choose-2026-09-27/addendum.md
  - _bmad-output/planning-artifacts/architecture/architecture-to-choose-2026-10-11/ARCHITECTURE-SPINE.md
  - docs/ux/DESIGN.md
  - docs/ux/EXPERIENCE.md
  - _bmad-output/specs/spec-to-choose/SPEC.md
  - _bmad-output/specs/spec-to-choose/glossary.md
---

# Fit my Ride - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Fit my Ride, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: A Rider can submit height, cycling inseam and riding style (Usage Taxonomy) and receive the candidate bikes. A bike is excluded only when a Core Parameter value with a defined evaluation method falls outside the Rider's ideal range; a parameter with no evaluation method never excludes a bike; exclusion is decided in the fit engine, never in a template. (PRD FR-1)
FR2: A Rider can view a Heatmap Table: one row per bike model (best-fitting size named), one column per Core Parameter (HTA, STA, BB, S, R), each cell on a continuous diverging scale; values without an evaluation result render as an explicit "unknown" cell, never omitted. (PRD FR-2)
FR3: A Rider can sort the table by any Core Parameter column or by In-Range Count; no weighted or composite score is computed or shown. (PRD FR-3)
FR4: A builder can manually trigger ingestion for one vendor's PDF catalog from the CLI, optionally restricted to a page range; re-running on unchanged inputs produces no duplicate or altered records; max 2 vendors in v1; no scheduled ingestion, no non-PDF sources. (PRD FR-4)
FR5: The system extracts Geometry Parameter values per model and per size through a dedicated per-vendor adapter into the Canonical Schema (Synonym Map, unit conversion: lengths cm, angles degrees) and the Usage Taxonomy; unrecognised names are flagged, never dropped or guessed; all 5 Core Parameters are required from every vendor, 7 Optional Parameters stored when present. (PRD FR-5)
FR6: Every ingested field stores Provenance (source, date); conflicts are resolved before commit: official outranks others, most recent official wins, short-circuiting once an official value is found. (PRD FR-6)
FR7: A builder reviews a summary of everything extracted (field, value, unit, source, matched synonym), including flagged arbitration, unrecognised names and bikes blocked for a missing Core Parameter, and must approve before anything is saved. (PRD FR-7)

### NonFunctional Requirements

(No formal NFR section exists in the PRD; the following are derived from the PRD scope, the architecture spine and the UX spine.)

NFR1: Self-hosted for up to 5 users on a home server in one Docker container with no runtime state; no public-scale concerns. (PRD §6.1, AD-11)
NFR2: No rider data stored server-side; access logs record the request path only, never the query string. (AD-9)
NFR3: WCAG 2.2 AA across the Fit surface; fit meaning never carried by colour alone; palette colourblind-safe. (EXPERIENCE.md Accessibility Floor)
NFR4: Ingestion is idempotent: same PDF, adapter, LLM provider, model and prompt yield zero changes. (FR4, AD-7)
NFR5: One quality gate: ruff (lint + format) and pytest via pre-commit locally and identical commands in GitHub Actions on every change. (AGENTS.md, AD-10)
NFR6: Installable PWA usable on desktop (primary) and phone; offline loads the app shell and last remembered entry but never shows stale results as current. (EXPERIENCE.md)
NFR7: LLM API keys exist only on the builder's machine, never in the repo or the image; access control and TLS are provided by the reverse proxy and Authentik, not by the app. (AD-6, AD-12)
NFR8: Core logic is testable without a database, network, browser or LLM; adapter tests use committed fixture excerpts, never the live LLM. (AD-1, AD-10)

### Additional Requirements

AR1: Greenfield: no starter template. Scaffold a uv-managed Python project (Python 3.13+, FastAPI, htmx 2.x, SQLite, ruff, pytest, pdfplumber) with the package layout `core/ adapters/ ingestion/ catalog/ web/ cli/` and `data/ingested/<vendor>/`. This is Epic 1 Story 1. (Architecture: Stack, Structural Seed)
AR2: Dependency direction is fixed: `core` depends on nothing; `web` never imports `ingestion` or `adapters`; `ingestion` never imports `web`; adapters depend only on `core`. (AD-1)
AR3: All shared types live in `core/schema` (canonical record, Usage Taxonomy, RiderInput, CellState, approved-file format: one JSON file per model holding all sizes); unit conversion only in `core/units`. (AD-3)
AR4: Bike identity is `<vendor>:<model_slug>[:<model_year>]` with the slug derived by one core function; sizes carry the vendor label plus an explicit sort order. (AD-3, Conventions)
AR5: Each vendor adapter has a pure two-phase contract: `plan(pdf_info, page_range)` then `map(raw_fields)`; `ingestion/` executes the plan with pdfplumber, OCR or LLM. (AD-4)
AR6: LLM access only through one `ingestion/llm` helper with a provider-neutral interface (Claude or OpenAI), retries, structured-JSON validation, caching and refusal to return unvalidated output. (AD-6)
AR7: Pipeline stages: extract, map/convert, arbitrate, stage, review, commit. Staged output never goes to `data/ingested/` before approval; approved files carry an approval marker and `catalog load` rejects files without one; records never take a wall-clock value. (AD-2, AD-7)
AR8: Idempotency key is a hash of (vendor, PDF content, page range, adapter version, LLM provider, model, prompt hash). (AD-7)
AR9: A bike missing any Core Parameter in any size is blocked from ingestion and listed in the review; other bikes in the batch may commit. (AD-7)
AR10: The SQLite catalog is derived from `data/ingested/` by `catalog load` at image build or container start and opened read-only by the web app. (AD-2, AD-11)
AR11: `core/fit` holds one evaluator per Core Parameter returning `unknown` or a signed deviation; exclusion and best-size selection (fewest out-of-range, then smallest total deviation, then vendor size order) are decided there. (AD-5, AD-8)
AR12: The Dockerfile, `.pre-commit-config.yaml` and `.github/workflows/` ship with the scaffold. (AD-10, AGENTS.md)
AR13: The existing reverse proxy and Authentik forward-auth must let the manifest, icons and service-worker script through unauthenticated; the app ignores and never logs identity headers. (AD-12)
AR14: Official vendor PDFs only for KTM and Van Rysel; no scraping, vendor APIs or aggregators. Each vendor's extraction pattern is validated by hand on one representative page, then reused. (PRD addendum)
AR15: Pick the default LLM provider by a spike comparing Claude and OpenAI on real KTM and Van Rysel pages. (Spine Deferred)
AR16: Work is parallel across AI agents, each in its own git worktree; stories must be completable by one agent without another story's in-flight changes; agents never commit or push. (AGENTS.md, PRD addendum)
AR17: Missing values are represented explicitly (`null` + reason), never omitted, never zero; staged and approved JSON has sorted keys and `schema_version`; dates are ISO 8601. (Conventions)

### UX Design Requirements

UX-DR1: Implement the design tokens from `DESIGN.md` as CSS custom properties: dark-first colours (background, surface, surface-raised, border, text, text-muted, primary, neon, focus-ring, error, diagram-card), the five heat tiers with text pairs, unknown-cell border, Inter + JetBrains Mono bundled locally (no CDN), spacing, radii.
UX-DR2: Rider form with three required fields (height, cycling inseam, riding style); Submit disabled until valid with per-field messages; accepted ranges height 120-230 cm, inseam 50-120 cm; numeric keypads on phone.
UX-DR3: Unit toggle `cm` / `ft·in` that converts entered values immediately; height as feet + inches, inseam as inches with one decimal; the server always receives centimetres.
UX-DR4: Riding style select loaded from the database (Usage Taxonomy), never hard-coded; Submit disabled with a named reason if it cannot load.
UX-DR5: Summary bar replaces the form after submit with Edit retaining values; unit and last values remembered in browser storage only; "clear" action resets them; returning visitors go straight to Results.
UX-DR6: Heat cell: tier glyph (▼ ▽ ● △ ▲) at the same size as the value, value at 0.1 precision (degrees for angles, cm otherwise), fill and text from the tier pair; angle parameters' accessible label says "below range / above range".
UX-DR7: Cell detail popover on desktop (hover, click, keyboard) and bottom sheet on phone: value, rider's range, distance from range, tier name.
UX-DR8: Unknown cell (dashed outline, muted `—`, popover "No data for this bike") and not-evaluated column (header range line "not evaluated", popover "No evaluation method for this parameter yet").
UX-DR9: Column header shows short code, full name and unit, plus a sticky line with the rider's range; sorting: default In-Range Count most-first; parameter column by distance from range, second tap reverses, third returns to default; unknown cells always sort last; stable ties (vendor, then model); sort never changes which bikes are shown.
UX-DR10: In-Range Count cell in neon, shown `n / 5` (or `n / evaluated`, or `—` with none evaluated).
UX-DR11: Legend of five swatches with glyph and label plus "unknown", always visible; collapses to a tap-to-open strip on phone.
UX-DR12: Static Geometry Diagram above the table using the supplied SVG on its light diagram card, `role="img"` with an aria-label naming the 12 codes (5 shown in the table), collapsing to a tap-to-open strip on phone; no interaction with the table in v1.
UX-DR13: Count line ("31 of 47 bikes fit · 16 excluded") and Show-excluded toggle (off by default); excluded rows appear at the bottom with a text badge "Excluded — outside your range", never dimming alone.
UX-DR14: State patterns: first run copy "Three measurements. Then the table.", computing skeleton with the same column count, no fitting bikes, offline ("Offline. Reconnect to compute fit."), load failure with retry, long-catalog scroll with pinned header.
UX-DR15: Table as ARIA grid with roving tabindex, arrow-key cell navigation, `aria-sort`, cell accessible names including distance from range, two-tone focus halo on heat cells, single focus ring elsewhere, reduced motion respected.
UX-DR16: Responsive: at 1200 px and above the whole table (Size, In-Range Count, 5 Core Parameter columns, pinned Bike column) fits without horizontal scroll; 768-1199 px scrolls horizontally with Bike column and headers pinned; phone is one column with a narrower pinned Bike column.
UX-DR17: PWA: manifest in standalone display mode with dark theme colour from `background`, service worker caching the app shell and last remembered entry.
UX-DR18: CLI builder review: header counts (fields, conflicts, unrecognised, blocked bikes), one row per field (field, value, unit, source, matched synonym), words `CONFLICT` / `UNRECOGNIZED` / `MISSING CORE` not colour alone, honours `NO_COLOR`, explicit approve or abort prompt, reports "0 changes" on an unchanged re-run; a report file with the same content is written alongside.

### FR Coverage Map

FR1: Epic 1 (exclusion rules and best-size selection in the fit engine) and Epic 4 (rider submits inputs and sees the filtered set)
FR2: Epic 1 (cell states, unknown semantics) and Epic 4 (Heatmap Table rendering)
FR3: Epic 1 (In-Range Count and ordering rules) and Epic 4 (sortable table)
FR4: Epic 2 - idempotent manual ingestion CLI with page range
FR5: Epic 2 (first vendor adapter, canonical mapping) and Epic 3 (second vendor through the same contract)
FR6: Epic 2 - provenance arbitration
FR7: Epic 2 - pre-commit review gate and blocked bikes

## Epic List

### Epic 1: Fit judgment you can trust
The builders can ask "does this bike's geometry fit this rider?" and get a deterministic, tested answer for each of the 5 Core Parameters, before any real data or UI exists. Delivers the project scaffold, the canonical schema and the evaluators (the first piece of work you decided), plus a small CLI that runs a rider against fixture bikes.
**FRs covered:** FR1, FR2, FR3 (engine side)

### Epic 2: First vendor catalog, reviewed and approved
A builder can ingest Van Rysel's full PDF catalog, review every extracted value, approve it, and have a read-only catalog database built from the approved files. Delivers the adapter contract, LLM helper (with the provider spike), arbitration, review gate, approved-file format and catalog loader on the baseline vendor.
**FRs covered:** FR4, FR5, FR6, FR7

### Epic 3: Second vendor added through the same contract
A builder can add KTM's catalog by writing one adapter, with no changes to the fit engine, web app or shared pipeline. This stress-tests the contract against a contrasting PDF layout and larger catalog, and is the point where the adapter contract may need correction.
**FRs covered:** FR5 (second vendor)

### Epic 4: Rider checks which bikes fit
A rider can enter height, inseam and style and read a sortable Heatmap Table of both vendors' bikes, with honest unknown states, a detail popover, the legend and the excluded-bikes toggle.
**FRs covered:** FR1, FR2, FR3 (rider-facing side)

### Epic 5: Remembered, explained and accessible
A rider's last entry is remembered on their device, a labelled geometry diagram explains the codes, the table works by keyboard and screen reader, and every wait or failure is stated plainly.
**FRs covered:** none new; delivers NFR3 and UX-DR5, UX-DR12, UX-DR14, UX-DR15

### Epic 6: Runs on the home server and installs on a phone
A rider can open the self-hosted app over HTTPS behind the existing Authentik front door, install it on a phone, and use it in the shop. Delivers the Docker image, deployment, PWA manifest and service worker, responsive phone layout and offline behaviour.
**FRs covered:** none new; delivers NFR1, NFR6, NFR7 and UX-DR16, UX-DR17

## Epic 1: Fit judgment you can trust

The builders can ask "does this bike's geometry fit this rider?" and get a deterministic, tested answer for each of the 5 Core Parameters, before any real data or UI exists.

### Story 1.1: Project scaffold with one quality gate

As a builder,
I want a runnable Python project with pre-commit and CI wired in,
So that every later story, from any agent, passes the same checks.

**Acceptance Criteria:**

**Given** a fresh clone
**When** I run `uv sync` and `uv run pytest`
**Then** the install succeeds and the smoke test passes
**And** the package has `core/ adapters/ ingestion/ catalog/ web/ cli/` and a `data/ingested/` folder

**Given** a staged change
**When** I commit
**Then** the `pre-commit` hook runs `ruff` (lint + format) and `pytest` and rejects the commit on failure

**Given** a push to GitHub
**When** Actions runs
**Then** it executes the same `ruff` and `pytest` commands as the hook
**And** a test fails if `core/` imports anything outside itself, or `web/` imports `ingestion/` or `adapters/`
**And** the "currently TODO" CI and pre-commit line in `AGENTS.md` is replaced by the chosen stack's actual commands

### Story 1.2: Canonical schema and units

As a builder,
I want one definition of the parameters, units and record shapes,
So that the web app and ingestion can never disagree on what a value means.

**Acceptance Criteria:**

**Given** `core/schema`
**When** I list parameters
**Then** I get 5 Core (HTA deg, S cm, R cm, STA deg, BB cm) and 7 Optional (all cm), each with unit and short code

**Given** a value in mm or inches
**When** I convert via `core/units`
**Then** I get cm to 0.1 precision
**And** an unknown unit raises a typed error rather than guessing

**Given** a vendor and model name
**When** I derive the bike id
**Then** I get `<vendor>:<model_slug>[:<model_year>]`, identical for identical input
**And** a missing value is `null` plus a reason, never omitted and never zero

### Story 1.3: Rider input and the evaluator seam

As a builder,
I want a registry with one evaluator per Core Parameter that returns "unknown" when none exists,
So that a parameter nobody has defined a rule for never gets a guessed colour.

**Acceptance Criteria:**

**Given** `RiderInput` (height_cm, inseam_cm, style)
**When** height is outside 120-230 or inseam outside 50-120
**Then** validation fails with a message naming the accepted range

**Given** a Core Parameter with no registered evaluator
**When** I evaluate any value
**Then** the result is `unknown`

**Given** a registered evaluator
**When** I evaluate a value
**Then** I get a signed deviation from the ideal range in the parameter's unit (0 in range, negative too short, positive too long)
**And** replacing one parameter's evaluator changes no other parameter's result

### Story 1.4: Stack and Reach evaluators

As a rider,
I want stack and reach judged against my height and inseam,
So that the two most telling cells carry a real answer.

**Acceptance Criteria:**

**Given** a fit rule for S and R written down and approved by Baptiste in `docs/fit-rules.md`
**When** the evaluators run
**Then** they implement exactly that rule and cite the document

**Given** a rider and a stack or reach value
**When** it is inside the rule's range
**Then** the deviation is 0
**And** outside the range it is the signed distance to the nearest edge

**Given** a rule that varies by riding style
**When** evaluated
**Then** the style comes from the Usage Taxonomy
**And** tests cover in-range, both edges, and each side outside, using values from the rule document

### Story 1.5: Decide HTA, STA and BB

As the product owner,
I want an explicit decision for each remaining Core Parameter,
So that "unknown" is a recorded choice and not an accident.

**Acceptance Criteria:**

**Given** HTA, STA and BB
**When** the decision is recorded in `docs/fit-rules.md`
**Then** each is either "rule defined" (the rule and any new rider input it needs) or "not evaluated in v1"

**Given** a parameter marked "rule defined"
**When** the story completes
**Then** its evaluator is implemented and tested like Story 1.4

**Given** a parameter marked "not evaluated"
**When** the story completes
**Then** a test asserts it yields `unknown` for every bike
**And** a decision that needs a new rider input adds a story to Epic 4 instead of expanding this one

### Story 1.6: Fit results, exclusion and ordering

As a rider,
I want each bike to get an excluded flag, a best size, an In-Range Count and a sort order,
So that the table is computed the same way everywhere.

**Acceptance Criteria:**

**Given** a bike with several sizes
**When** results are computed
**Then** the size with the fewest out-of-range parameters wins, then the smallest total absolute deviation, then vendor size order

**Given** a Core Parameter with a defined evaluator and an out-of-range value
**When** results are computed
**Then** the bike is marked `excluded`
**And** an `unknown` parameter never excludes a bike

**Given** results
**When** sorted by In-Range Count
**Then** most in-range is first
**And** by a parameter column, closest to range first, unknown last, ties by vendor then model
**And** In-Range Count is computed only over evaluated parameters and no composite score exists

### Story 1.7: Try a rider against fixture bikes from the CLI

As a builder,
I want a command that prints the fit table for a rider against sample bikes,
So that I can see the fit logic working before any real data or UI exists.

**Acceptance Criteria:**

**Given** a fixture file of bikes
**When** I run `fit-check --height 178 --inseam 82 --style road`
**Then** I get one row per model with chosen size, five parameter cells with tier and deviation, and In-Range Count
**And** unknown cells print `—` and excluded bikes are counted, not silently dropped

**Given** invalid input
**When** I run it
**Then** it exits non-zero naming the accepted range
**And** output is readable without colour and honours `NO_COLOR`

## Epic 2: First vendor catalog, reviewed and approved

A builder can ingest Van Rysel's full PDF catalog, review every extracted value, approve it, and have a read-only catalog database built from the approved files.

### Story 2.1: Adapter contract and approved-file format

As a builder,
I want one adapter interface and one approved-file format,
So that every vendor produces records the pipeline and loader handle identically.

**Acceptance Criteria:**

**Given** the adapter interface
**When** a test adapter implements `plan(pdf_info, page_range)` and `map(raw_fields)`
**Then** it returns typed results `ok` / `unrecognized` / `missing` with value, unit, source page and the vendor's original field name

**Given** a model with several sizes
**When** serialized
**Then** one JSON file per model holds all sizes, with sorted keys, `schema_version`, provenance per value, and no wall-clock timestamps
**And** a file whose approval marker is missing or whose content hash doesn't match is rejected

### Story 2.2: LLM helper behind one provider-neutral interface

As a builder,
I want one helper that calls an LLM and returns only validated structured output,
So that no adapter handles provider errors differently.

**Acceptance Criteria:**

**Given** a plan's prompt, pages and output schema
**When** the helper runs
**Then** it returns schema-valid JSON or a typed failure, never unvalidated text

**Given** a provider error
**When** the call fails
**Then** it retries with backoff and then fails with the reason

**Given** an identical request
**When** repeated
**Then** the cached result is used and no second call is made
**And** Claude and OpenAI are selectable by configuration, keys come only from the environment, and tests use a fake provider with no network

### Story 2.3: Provider spike on Van Rysel pages

As the product owner,
I want Claude and OpenAI compared on real Van Rysel geometry pages,
So that the default provider is chosen on evidence.

**Acceptance Criteria:**

**Given** one representative page and one difficult page
**When** both providers extract them
**Then** a short comparison records accuracy against a hand-checked answer, cost and failures

**Given** the comparison
**When** I decide
**Then** the default provider is recorded in the architecture spine's Deferred list and in config
**And** no API key or full PDF is committed

### Story 2.4: Van Rysel adapter

As a builder,
I want an adapter that reads Van Rysel's geometry tables per model and size,
So that the baseline vendor lands in the canonical schema.

**Acceptance Criteria:**

**Given** the validated extraction pattern for one representative page
**When** `plan` runs
**Then** it names the pages and strategy and the pattern is reused for the rest of the catalog

**Given** committed fixture excerpts
**When** `map` runs
**Then** all 5 Core Parameters are produced per size, lengths in cm and angles in degrees, with Optional Parameters when present

**Given** a field name the synonym map doesn't know
**When** mapped
**Then** it is returned as `unrecognized`, never dropped or guessed
**And** vendor categories map onto the Usage Taxonomy

### Story 2.5: Provenance arbitration

As a builder,
I want conflicting values settled by fixed rules,
So that no source silently overrides another.

**Acceptance Criteria:**

**Given** two sources for a field
**When** one is official
**Then** the official one wins and lower-precedence sources aren't consulted

**Given** several official sources
**When** arbitrated
**Then** the most recently dated wins
**And** the result records that arbitration happened and what lost, as a pure function in `core` with no I/O

### Story 2.6: Idempotent staged ingestion command

As a builder,
I want one command that ingests a vendor PDF into a staging area,
So that I can re-run it safely and restrict it to a page range.

**Acceptance Criteria:**

**Given** `ingest van_rysel --pages 12-40`
**When** it runs
**Then** it executes extract, map, arbitrate and stage, writing only to staging

**Given** an unchanged PDF, adapter version, provider, model and prompt
**When** re-run
**Then** it reports "0 changes"
**And** changing any one of those inputs invalidates the idempotency key and re-extracts

### Story 2.7: Review gate and report

As a builder,
I want to see everything extracted and approve or abort,
So that nothing unreviewed reaches the catalog.

**Acceptance Criteria:**

**Given** staged output
**When** review runs
**Then** it prints header counts (fields, conflicts, unrecognised, blocked bikes) and one row per field (field, value, unit, source, matched synonym)

**Given** conflicts, unknown names or a bike missing any Core Parameter in any size
**When** shown
**Then** they are flagged `CONFLICT`, `UNRECOGNIZED`, `MISSING CORE` and blocked bikes are listed, not committed

**Given** approval
**When** confirmed
**Then** approved files are written with the approval marker
**And** abort writes nothing, a report file with the same content is written alongside, and output honours `NO_COLOR`

### Story 2.8: Catalog loader

As a builder,
I want the read-only database rebuilt from approved files,
So that the files in git stay the single source of truth.

**Acceptance Criteria:**

**Given** `data/ingested/`
**When** I run `catalog load`
**Then** a SQLite file is built containing every approved model, size, value and provenance

**Given** a file without a valid approval marker
**When** loaded
**Then** the loader refuses it and names the file
**And** the Usage Taxonomy is queryable and read queries open the database read-only

### Story 2.9: Ingest the full Van Rysel catalog

As the product owner,
I want Van Rysel's full catalog ingested and approved,
So that there is real data for the rest of the project.

**Acceptance Criteria:**

**Given** the real PDF
**When** I run the pipeline
**Then** every model is either approved or listed as blocked with the reason

**Given** the approved files
**When** I run the loader
**Then** the catalog opens read-only with all approved bikes
**And** no manual database edits were needed

## Epic 3: Second vendor added through the same contract

A builder can add KTM's catalog by writing one adapter, with no changes to the fit engine, web app or shared pipeline, stress-testing the contract against a contrasting PDF layout and a larger catalog.

### Story 3.1: Probe KTM's PDFs against the contract

As a builder,
I want KTM's layouts and naming compared with the contract,
So that any contract gap is found before an adapter is written.

**Acceptance Criteria:**

**Given** the KTM PDFs
**When** I sample representative and difficult pages
**Then** a short note lists layout variants, field names, units and category names versus Van Rysel

**Given** the note
**When** the contract can't express something
**Then** the gap is recorded with a proposed contract change, applied to `core` and the Van Rysel adapter in this story with all existing tests still passing
**And** if no gap exists, the note says so

### Story 3.2: KTM synonym map, units and taxonomy mapping

As a builder,
I want KTM's vocabulary mapped onto the canonical schema as data,
So that mapping is reviewable without reading code.

**Acceptance Criteria:**

**Given** KTM's field names
**When** mapped
**Then** each Core and Optional Parameter resolves to its canonical name or is explicitly unmapped

**Given** KTM's units
**When** converted
**Then** the result is cm or degrees via `core/units`, not a KTM-specific conversion
**And** KTM's categories map onto the Usage Taxonomy, with unmapped categories listed

### Story 3.3: KTM adapter

As a builder,
I want an adapter that reads KTM's tables per model and size,
So that KTM lands in the same canonical shape.

**Acceptance Criteria:**

**Given** committed fixture excerpts for each layout variant
**When** `map` runs
**Then** all 5 Core Parameters are produced per size, or the bike is reported `missing`

**Given** KTM's many model references
**When** `plan` runs
**Then** it covers each layout variant with a pattern validated by hand on one representative page
**And** adding this adapter changes no file under `core/`, `web/`, `catalog/` or the shared pipeline except where Story 3.1 recorded a contract change

### Story 3.4: Ingest the full KTM catalog

As the product owner,
I want KTM's full catalog ingested and approved,
So that both vendors appear in the same catalog.

**Acceptance Criteria:**

**Given** the real PDFs
**When** I run the pipeline
**Then** every model is approved or listed as blocked with the reason

**Given** the approved files of both vendors
**When** I run the loader
**Then** one catalog contains both, comparable in the same units
**And** no manual database edits were needed

### Story 3.5: Document how to add a vendor

As a builder,
I want a checklist for adding a vendor,
So that a third vendor doesn't need rediscovery.

**Acceptance Criteria:**

**Given** the two adapters
**When** I write `docs/adding-a-vendor.md`
**Then** it lists the files to add (adapter, mapping data, fixtures, tests) and the files that must not change

**Given** the checklist
**When** it is followed literally by the co-builder and by an AI agent that did not write either adapter
**Then** any step they couldn't follow is fixed in the document

## Epic 4: Rider checks which bikes fit

A rider can enter height, inseam and style and read a sortable Heatmap Table of both vendors' bikes, with honest unknown states, a detail popover, the legend and the excluded-bikes toggle.

### Story 4.1: Web shell serving the fit page from the catalog

As a rider,
I want a page that loads in the app's look,
So that everything else has a place to land.

**Acceptance Criteria:**

**Given** a built catalog
**When** I open the app
**Then** the page renders with the `DESIGN.md` tokens as CSS custom properties and Inter plus JetBrains Mono served from the app, with no CDN

**Given** a request with measurements in the query string
**When** the server logs it
**Then** the log records the path only
**And** the web app opens the catalog read-only and a test fails if it imports `ingestion/` or `adapters/`

### Story 4.2: Rider form with unit toggle and style select

As a rider,
I want to enter height, inseam and style in cm or ft·in,
So that I can use the units I think in.

**Acceptance Criteria:**

**Given** the form
**When** a field is empty or out of range (height 120-230 cm, inseam 50-120 cm)
**Then** Submit is disabled and each field says what is missing or the accepted range

**Given** values entered
**When** I switch `cm` / `ft·in`
**Then** they convert immediately and are kept, and the server always receives cm

**Given** the riding-style list
**When** loaded
**Then** options come from the catalog's Usage Taxonomy, and if it can't load Submit is disabled with the reason named
**And** submitting puts the measurements in the page URL

### Story 4.3: Heatmap Table with heat cells and unknown states

As a rider,
I want one row per bike with five coloured parameter cells,
So that I can see how each bike fits me at a glance.

**Acceptance Criteria:**

**Given** a submitted rider
**When** results render
**Then** each row shows Bike, the chosen Size and In-Range Count, then HTA, STA, BB, S, R

**Given** an evaluated cell
**When** rendered
**Then** it shows the tier glyph and the value at 0.1 precision (degrees for angles, cm otherwise) on its tier fill

**Given** a parameter with no evaluator
**When** rendered
**Then** every cell is unknown (dashed outline, `—`) and the header says "not evaluated"
**And** no cell is omitted and no composite score is displayed

### Story 4.4: Cell detail popover and bottom sheet

As a rider,
I want to see a cell's value, my range and the distance from it,
So that I know how far off a borderline bike is.

**Acceptance Criteria:**

**Given** a cell
**When** I hover, click or focus it
**Then** a popover shows value, rider's range, distance from range and tier name

**Given** a phone-width screen
**When** I tap a cell
**Then** it opens as a bottom sheet instead

**Given** an unknown cell
**When** opened
**Then** it says "No data for this bike" or "No evaluation method for this parameter yet", as applicable
**And** Esc closes it and angle cells say "below range" / "above range"

### Story 4.5: Sorting and column headers

As a rider,
I want to sort by any parameter or by In-Range Count,
So that I can find the closest bikes for what I care about.

**Acceptance Criteria:**

**Given** results
**When** first shown
**Then** they are sorted by In-Range Count, most first

**Given** a parameter header
**When** I activate it
**Then** it sorts by distance from range, a second activation reverses and a third returns to the default

**Given** any sort
**When** applied
**Then** unknown cells sort last, ties keep vendor then model, and the set of bikes shown doesn't change
**And** each header shows its code, full name, unit and the rider's range (or "not evaluated"), and the sort state is carried in the URL

### Story 4.6: Legend, count line and show-excluded toggle

As a rider,
I want to know how many bikes fit and see the ones that were excluded,
So that no suitable bike is hidden from me without a reason.

**Acceptance Criteria:**

**Given** results
**When** shown
**Then** the count line reads like "31 of 47 bikes fit · 16 excluded" and the legend shows five swatches with glyph and label plus "unknown"

**Given** Show-excluded off (default)
**When** I switch it on
**Then** excluded bikes appear at the bottom, each with the badge "Excluded — outside your range"
**And** no excluded row is marked by dimming alone

## Epic 5: Remembered, explained and accessible

A rider's last entry is remembered on their device, a labelled geometry diagram explains the codes, the table works by keyboard and screen reader, and every wait or failure is stated plainly.

### Story 5.1: Summary bar, remembered values and clear

As a rider,
I want my last entry remembered on this device,
So that I don't retype it every visit.

**Acceptance Criteria:**

**Given** a submit
**When** results show
**Then** the form collapses into a summary bar with my values in the active unit and an Edit action that reopens the form with values kept

**Given** a returning visit
**When** the app opens
**Then** my remembered unit and values restore and Results shows directly

**Given** the Clear action
**When** used
**Then** remembered values are removed
**And** nothing about the rider is sent to or stored on the server beyond computing the fit

### Story 5.2: Geometry Diagram

As a rider,
I want a labelled bike diagram above the table,
So that I can tell what each code measures.

**Acceptance Criteria:**

**Given** Results
**When** shown
**Then** the supplied SVG, moved into the app's static files, appears above the table on its light diagram card with all 12 codes labelled

**Given** a phone-width screen
**When** shown
**Then** it collapses to a tap-to-open strip
**And** it has `role="img"` and an aria-label naming the 12 codes and the five shown in the table, and has no interaction with the table

### Story 5.3: Keyboard and screen-reader support for the table

As a rider using a keyboard or screen reader,
I want to move through and understand the table,
So that the fit answer is available to me too.

**Acceptance Criteria:**

**Given** the table
**When** I use Tab and arrow keys
**Then** it follows the ARIA grid pattern with roving tabindex and Enter opens the popover

**Given** a cell
**When** focused
**Then** its accessible name states parameter, value, tier and distance from range, or why it is unknown

**Given** a heat cell
**When** focused
**Then** the two-tone focus halo is visible on all five tiers
**And** sorted headers expose `aria-sort`, reduced motion is respected, and contrast checks pass at WCAG 2.2 AA

### Story 5.4: Computing, empty and failure states

As a rider,
I want the page to tell me what is happening,
So that a wait or a failure never looks like a result.

**Acceptance Criteria:**

**Given** a submit
**When** results are computing
**Then** a skeleton with the same column count appears and the summary bar shows at once

**Given** no bike fits
**When** shown
**Then** it says "No bikes fit these measurements.", the excluded count, the toggle and an Edit action

**Given** the server is unreachable
**When** loading
**Then** an error with a retry appears and no stale table is shown
**And** first run shows "Three measurements. Then the table."

**Given** a catalog longer than the screen
**When** I scroll the table
**Then** the header stays pinned and the count line still shows the total

## Epic 6: Runs on the home server and installs on a phone

A rider can open the self-hosted app over HTTPS behind the existing Authentik front door, install it on a phone, and use it in the shop.

### Story 6.1: Container image with the catalog built in

As the product owner,
I want one Docker image that contains the app and its catalog,
So that the server needs nothing else to run it.

**Acceptance Criteria:**

**Given** the repo
**When** I build the image
**Then** `catalog load` runs from `data/ingested/` and the app starts with the catalog read-only

**Given** the image
**When** inspected
**Then** it contains no API keys, no PDFs and no ingestion credentials
**And** a `docker compose` file runs it with no persistent volume

### Story 6.2: Deploy behind the existing proxy and Authentik

As the product owner,
I want the app reachable over HTTPS with sign-in handled in front of it,
So that it is private without adding accounts to the app.

**Acceptance Criteria:**

**Given** the existing reverse proxy and Authentik
**When** the app is routed through it
**Then** a rider reaches it over HTTPS after signing in

**Given** the manifest, icons and service-worker script
**When** requested unauthenticated
**Then** they are served, so the PWA is installable
**And** the app ignores and never logs identity headers, and a health check endpoint reports ready

### Story 6.3: Installable PWA manifest

As a rider,
I want to install the app on my phone,
So that it opens like an app in the shop.

**Acceptance Criteria:**

**Given** the app over HTTPS
**When** I open it on a phone
**Then** the browser offers install and the installed app opens in standalone mode
**And** the manifest sets the dark theme colour from `{colors.background}` and includes icons for phone and desktop

### Story 6.4: Offline shell without stale results

As a rider,
I want the app to open without a connection and say so,
So that I'm never shown old results as current.

**Acceptance Criteria:**

**Given** a previous visit
**When** I open the app offline
**Then** the shell and my last remembered entry load

**Given** offline
**When** I submit
**Then** it says "Offline. Reconnect to compute fit." and no results are shown
**And** a stale table is never shown as current after reconnecting without recomputing

### Story 6.5: Phone and tablet layouts

As a rider in a shop,
I want the table readable on my phone,
So that I can check a bike in front of me.

**Acceptance Criteria:**

**Given** a width of 1200px or more
**When** results show
**Then** all columns fit without horizontal scroll

**Given** 768-1199px
**When** results show
**Then** the table scrolls horizontally with the Bike column and header rows pinned

**Given** a phone width
**When** results show
**Then** the form is one column, the Bike column is narrower with vendor and model on two lines, and the legend collapses to a tap-to-open strip

### Story 6.6: Rebuild from a clean machine

As the product owner,
I want to prove the server holds nothing that isn't in git,
So that losing it costs nothing.

**Acceptance Criteria:**

**Given** a clean machine with Docker
**When** I clone the repo, build and run
**Then** the app serves the same catalog as the live one
**And** the steps are written down in the repo and following them literally works
