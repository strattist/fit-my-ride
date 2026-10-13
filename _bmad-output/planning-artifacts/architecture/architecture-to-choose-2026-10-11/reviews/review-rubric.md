# Rubric review: Architecture Spine, Fit my Ride

Reviewed: ARCHITECTURE-SPINE.md (draft, 2026-10-11) against docs/prd.md (final).
Date of review: 2026-10-11.

## Verdict

**Revise before handoff.** The spine is strong on structure (layering, one adapter per vendor, files as source of truth, one container). But it has one PRD contradiction (columns), one unspecified core behaviour that every downstream unit touches (ideal range / exclusion / size choice), one rule that conflicts with its own default tooling (rider data in URL vs access logs), and a PWA deployment gap (HTTPS). All are cheap to fix.

## Findings, ranked

### F1 (High). The fit-evaluation contract is the biggest unfixed divergence point
- AD-8 fixes the registry seam but not what crosses it. Undefined: the shape of "rider inputs" (height, inseam, Usage Taxonomy value), what "ideal range" is as a data type, and what a "diverging cell state" is. The PRD requires a continuous scale (FR-2), but "cell state" reads as an enum. Whoever builds `core/fit` and whoever builds the template will each pick differently.
- FR-1 hard exclusion ("excluded only when known geometry is outside ideal range") is not owned by any AD. AD-5 says "size never filters rows" and AD-8 only mentions cell states. Say which function excludes, and that unknown never excludes.
- AD-5 makes the core "pick the best-fitting size" but gives no selection criterion. With every evaluator `unknown` (the stated v1 default per PRD OQ1) the choice is undefined, and In-Range Count (per chosen size) depends on it. Fix: define a deterministic tie-break (e.g. size sort order) and the criterion when all cells are unknown.
- Deferring the evaluation *method* is fine. Deferring the *interface and result type* is not.

### F2 (High). Spine contradicts PRD on table columns
- PRD FR-2, section 4.1 and the Glossary: one column per Geometry Parameter, all 12. AD-3: only 5 Core Parameters are table columns in v1; 7 are stored but not shown.
- The spine also redefines "Required Tier" (PRD: rider inputs; spine agrees, but adds a Core/Optional bike-side split the PRD does not have).
- Either the PRD must be amended (promoting the 5/7 split) or the spine flagged as a deliberate narrowing. As written, the "Binds FR-2" claim is false. The PRD's SM-C1 (12 parameters v1) also reads against it.
- Related: AD-7 blocks a bike missing any of 5 Core in any size. PRD FR-1/UJ-1 say a bike with missing Required Tier geometry still appears as "unknown". The spine blocks it from the catalog entirely, so the UJ-1 edge case can never occur for Core parameters. Reconcile (it can only occur for Optional ones, which are not shown).

### F3 (High). "No rider data on server" conflicts with default URL logging; security/exposure not decided
- AD-9 puts rider inputs in the URL query, and says the server "logs no rider measurements". Default uvicorn/FastAPI access logs and any reverse proxy log the full query string. The rule is not enforceable as written; add an explicit rule (disable/strip access-log query strings, or use fragment/POST). Observability is deferred, but this log decision is not safe to defer.
- PWA: service workers and installability require HTTPS (localhost excepted). The spine says only "docker compose up" on a home server, with no TLS/reverse-proxy decision and no statement of network exposure (LAN-only vs internet). PRD says public traffic is out of scope. This needs one line: LAN/VPN only, and who terminates TLS.
- Security dimension otherwise undeclared: no auth (consistent with PRD), no statement on prompt/PDF content trust, or API-key handling beyond "local env". Flag as decided-by-PRD or deferred.

### F4 (Medium). Adapter / LLM / PDF-reader boundary is internally inconsistent
- AD-4: adapter, given a PDF, "returns canonical records" and "reads the vendor PDF only". AD-6: only `ingestion/llm` calls the LLM, adapters supply prompt, page selection, schema. The dependency graph has no `adapters -> llm` edge and `ingestion -> adapters`. So who runs extraction? Two units will implement it two ways (adapter pulls from a callable; or adapter is two functions: `plan()` and `parse()`).
- Undecided: does the LLM receive PDF pages directly (Claude and OpenAI both accept PDF input) or pdfplumber text? The Stack lists pdfplumber as a "first-pass reader where clean", which makes the extraction route per-vendor and ad hoc. State the contract: input type to the helper, and who owns fallback.
- Shared-code leak risk: pdfplumber use is not placed in any namespace.

### F5 (Medium). Data-model gaps that cause drift
- Usage Taxonomy (FR-5, riding-style input) is not in AD-3, the ER diagram, or the Identity convention. Its six values must be defined once in `core/schema` since both the rider form and adapters use it (PRD: "one taxonomy, not two").
- Bike identity `<vendor>:<model_slug>` ignores model year / catalog edition; vendor PDFs change yearly, and `source_date` alone will not disambiguate. Say whether year is part of identity or the newest wins.
- Slug generation rule is not defined (two adapters will slug differently).
- Arbitration (FR-6) needs a source-class field (official / other) and a ranking. Provenance fields list `source` and `source_date` but not class; with only vendor PDFs in v1 the rule is vacuous, so say so explicitly.
- Idempotency key includes "adapter version", so an adapter bump legitimately re-writes records. This is fine but should be stated against FR-4's "no altered records" wording. LLM nondeterminism is covered only by "result caching"; cache location and invalidation are not decided.
- Staging area location and the review report format are unspecified (path, git-ignored or not).
- `schema_version` migrations: nothing on what happens when the schema changes and approved files are old. Deferred or flagged is needed.

### F6 (Low/Medium). Technology currency and fit (web checked 2026-10-11)
| Item | Finding |
| --- | --- |
| htmx | 4.0.0 shipped about 2026-08-28; npm `latest` and the project's stance keep 2.x supported indefinitely. "2.x, 4.x not adopted" is current and defensible. Pin exact 2.x at scaffold; revisit later. |
| FastAPI | Latest seen 0.136.x (May 2026). "0.13x-0.14x line verified" is a range, not a pin, and 0.14x could not be confirmed. Still 0.x (minor releases can break); pin exact. Fit is fine, though a read-only server-rendered app with SQLite is simple enough that this is a modest-fit choice. |
| uv | "0.11.x verified" could not be confirmed by search (a March snapshot showed 0.10.9; 0.11 is plausible by October). Pin from `uv.lock`; low risk. |
| pdfplumber | Latest seen 0.11.9/0.11.10 (Jan 2026). Python 3.13/3.14 support not confirmed. Verify at scaffold; spine says only "pinned at scaffold". |
| Python | "3.13 or newer" is too loose for agents in parallel worktrees; pick one minor (3.13 or 3.14) and pin in `.python-version` and Dockerfile. |
| Claude API | PDF input and structured outputs (`output_config.format`, strict tool use) are documented and GA on current models. Fit is good. Note per-request page and size limits (32 MB request) which affect "page range" handling in FR-4. |
| OpenAI API | PDF file inputs and Structured Outputs are supported (not re-verified by search in this review; confirm against current docs when the spike runs). |
| Unnamed | Template engine (Jinja2 presumably), SQLite access layer, CSS approach, base image. Small, but they are cross-unit divergence points for `web/`. |

### F7 (Low). Deferred items that can cause divergence
- "Table sort mechanics (server round-trip vs client script)": affects the service worker, URL state, and tests. Both options satisfy AD-9, but two UI units may choose differently; decide before the first web story.
- "Default LLM provider": acceptable because the helper makes it config, provided the helper's output schema is provider-neutral (AD-6 says so).
- "Observability/logging format": see F3; at least the no-rider-data logging rule must be decided now.
- Backups beyond git: fine, nothing runtime to back up (AD-2, AD-11).

## Checklist result

| Criterion | Result |
| --- | --- |
| Fixes the real divergence points, misses none | Partial. Misses fit-evaluation contract, adapter/LLM seam, taxonomy, identity/year (F1, F4, F5). |
| Every AD's Rule enforceable and prevents its divergence | Mostly. AD-1, 2, 3, 7, 10, 11 enforceable (lint/import rules suggested: add an import-linter or ruff banned-api check to AD-1 and the dependency graph, which is currently only prose). AD-9 unenforceable as written (F3). AD-4/6 inconsistent (F4). AD-5/8 under-specified (F1). |
| Nothing under Deferred lets two units diverge | Mostly. Sort mechanics and logging do (F7). |
| Technologies current and fit | Yes in direction; versions unverified or loose (F6). |
| Covers FR-1..FR-7 | Mapped in the Capability table, but FR-1 exclusion has no owner and FR-2 contradicts the 5-column choice (F1, F2). FR-3..FR-7 covered. |
| Dimensions decided/deferred/flagged | Deployment: partial (TLS/exposure missing). Operations: deferred (logging needs a decision). Security: not declared (F3). Data: gaps in F5. |

## Suggested fixes (smallest set)
1. Add AD-8 detail: input type, `IdealRange`, result type, exclusion function, and size-selection criterion with unknown fallback.
2. Resolve 5 vs 12 columns in the PRD or the spine, and the Core-missing-blocks vs UJ-1 edge case.
3. Amend AD-9: access logs must not record the query string; state TLS/exposure assumptions in AD-11.
4. Rewrite AD-4/AD-6 into one explicit sequence: ingestion calls `adapter.plan()`, helper executes, `adapter.parse()` maps; add the edge to the graph; state PDF-vs-text input.
5. Add Usage Taxonomy, model-year identity, slug rule, source class, staging path, and cache location to AD-3/conventions.
6. Add an enforceable import-boundary check to AD-10.
7. Pin exact Python minor and versions for FastAPI, htmx, pdfplumber at scaffold.
