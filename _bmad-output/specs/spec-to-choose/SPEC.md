---
id: SPEC-to-choose
companions:
  - glossary.md
  - ../../planning-artifacts/architecture/architecture-to-choose-2026-10-11/ARCHITECTURE-SPINE.md
  - ../../../docs/ux/EXPERIENCE.md
  - ../../../docs/ux/DESIGN.md
sources:
  - ../../../docs/prd.md
  - ../../../docs/product-brief.md
  - ../../planning-artifacts/prds/prd-to-choose-2026-09-27/addendum.md
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# Fit my Ride (v1)

## Why

A vision and a pain for two builders, shared with a few friends: bike sites describe frames richly but never answer whether a bike fits *your body*, and vendor geometry tables sit in PDFs with inconsistent names and units. v1 answers only that question for two vendors' catalogs, self-hosted for up to 5 users, and doubles as a testbed for AI-assisted extraction and parallel AI coding agents. If the fit answer alone isn't worth using, nothing else matters yet.

## Capabilities

- **CAP-1**
  - **intent:** A rider can enter height, cycling inseam and riding style and receive the candidate bikes that suit them.
  - **success:** A bike is excluded only when a known Core Parameter value falls outside the rider's ideal range; a bike with an unjudgeable parameter is never excluded on that basis.
- **CAP-2**
  - **intent:** A rider can see one row per bike model across the five Core Parameters (HTA, S, R, STA, BB), each cell coloured on a continuous diverging scale against their ideal range.
  - **success:** Every cell is coloured or explicitly `unknown`; none is omitted; the chosen size is named; no binary good/bad flag exists.
- **CAP-3**
  - **intent:** A rider can sort the table by any Core Parameter column or by In-Range Count.
  - **success:** Sorting works on both; no weighted or composite score is computed or shown anywhere.
- **CAP-4**
  - **intent:** The system can judge each Core Parameter value against the rider's inputs through a named, replaceable evaluator.
  - **success:** For each Core Parameter, either an evaluator yields a deviation from the ideal range or the cell is `unknown`; changing one parameter's method touches only its evaluator.
- **CAP-5**
  - **intent:** A builder can manually run ingestion for one vendor's PDF catalog from the CLI, optionally restricted to a page range.
  - **success:** Re-running on an unchanged PDF with unchanged adapter, LLM provider, model and prompt produces zero changes.
- **CAP-6**
  - **intent:** The system can extract each vendor's geometry per model and size through a dedicated per-vendor adapter into the canonical schema and Usage Taxonomy.
  - **success:** Every stored length is in cm and every angle in degrees; an unrecognised field name is flagged, never dropped or guessed; adding a vendor requires only a new adapter, its mapping data and fixtures.
- **CAP-7**
  - **intent:** The system can resolve conflicting values for a field by provenance before commit.
  - **success:** An official vendor source outranks any other; among official sources the most recently dated wins; lower-precedence sources are not consulted once an official value exists.
- **CAP-8**
  - **intent:** A builder can review everything the parser extracted and must approve it before it is saved.
  - **success:** The review lists field, value, unit, source, matched synonym, flags each arbitrated conflict, each unrecognised name and each bike blocked for a missing Core Parameter; nothing reaches the approved data before approval; the catalog loader rejects unapproved files.
- **CAP-9**
  - **intent:** A rider can use the app as an installable PWA on desktop or phone against a self-hosted server, with no account.
  - **success:** The app installs on a phone through the existing HTTPS front door; the server stores no rider data and logs no rider measurements.

## Constraints

- The architecture spine's invariants AD-1 to AD-12 bind every build: pure core with I/O only in shells; approved files in git are the source of truth and SQLite is derived and read-only at runtime; one adapter per vendor behind one contract; LLM only in ingestion through one helper; no rider data on the server; one container with no runtime state; auth and TLS in front of the app, never in it.
- Bike parameters are Core (HTA, S, R, STA, BB: required from every vendor, the only v1 table columns) or Optional (the other seven: stored when present, not shown). A bike missing any Core Parameter in any size is blocked from ingestion.
- Data sources are vendors' official PDFs only: no scraping, vendor APIs or aggregators; at most two vendors in v1 (KTM, Van Rysel); the Canonical Schema follows Van Rysel naming.
- Each vendor's extraction pattern is validated by hand on one representative page, then reused across that vendor's pages.
- Synonym mapping, unit normalisation and taxonomy mapping are one reusable mechanism; provenance is a generic mechanism.
- Two builders run AI coding agents in parallel, each in its own git worktree; no agent commits or pushes; work is split into stories one agent can finish alone.
- CI and a pre-commit hook (ruff, pytest) run identical commands locally and on GitHub Actions.
- Home server, Docker, Python; ingestion runs on a builder's machine and API keys never enter the image or repo.

## Non-goals

- Marketplace, where-to-buy map, dealer list or shop badges.
- User accounts, saved profiles, or any auth layer inside the app.
- Weighted or composite fit score.
- Spec-sheet browsing: materials, components, wheel size.
- Scraping or vendor APIs; scheduled ingestion; an ingestion UI.
- Free-text prompt, height-only quick mode, post-purchase feedback, search analytics.
- Public or multi-tenant hosting, monetisation, more than two vendors.
- Displaying the Optional Parameters in the v1 table.

## Success signal

You or a friend uses the table to help decide a real bike purchase and finds the fit judgment clearer than reading two spec sheets by hand, and both vendors' full catalogs ingest with no manual database edits to fix bad data.

## Assumptions

- The home server already has a TLS reverse proxy with Authentik forward-auth; the manifest, icons and service worker bypass it so the PWA installs.
- Best size per model: fewest out-of-range parameters, then smallest total deviation, then vendor size order.
- v1 delivers the table with every cell `unknown` until CAP-4 evaluators exist; CAP-4 is the first epic.

## Open Questions

- How are STA, HTA and BB evaluated, if at all? Stack and reach need a rule written down in `docs/fit-rules.md` (Story 1.4); the other three are decided in Story 1.5 as either a rule or "not evaluated in v1".
- Which LLM provider is the default, Claude or OpenAI? Decided by the spike in Story 2.3.
- Should `RiderInput` stay extensible so quick or expert modes can be added later, as the PRD addendum asks? No new rider input is planned for v1.
