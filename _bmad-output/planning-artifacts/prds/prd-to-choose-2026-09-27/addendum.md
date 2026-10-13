# Addendum: Fit my Ride PRD

Technical-how and process notes that don't belong in the PRD's capability narrative, but should carry forward into architecture. For the fuller Should/Could/Won't backlog and long-horizon ideas, see `docs/product-brief.md`'s own addendum (`_bmad-output/planning-artifacts/briefs/brief-to-choose-2026-09-27/addendum.md`) — not duplicated here.

## Build process: multiple AI agents in parallel

This project will be built by two people, each running AI coding agents, working in parallel rather than one agent at a time. This is a process constraint, not a product feature — it shapes architecture and epics/stories, not the PRD's functional requirements.

- Mechanism already decided and recorded in `AGENTS.md`: each parallel agent works in its own git worktree; merge back via normal git; never two agents editing the shared main checkout directly.
- **Component boundary — decided:** Fit Engine and Data Pipeline share only the database (the Canonical Schema store) as their interface, nothing else. Fit Engine is read-only against it. Data Pipeline is the sole read-write component. This lets one agent build ingestion while another builds the heatmap UI without touching the same files.
- Implication for epics/stories (downstream, `bmad-create-epics-and-stories`): favor stories sized and bounded so a single agent can complete one without needing another story's in-flight changes.

## Extraction strategy (technical-how for FR-5, for architecture)

Per-vendor PDF layouts are assumed to repeat their page structure across the catalog. Suggested approach: hand-validate the extraction pattern against one representative page per vendor, then reuse that validated pattern across the rest of that vendor's pages — rather than re-deriving structure per page from scratch. Reduces both cost (less full LLM/OCR reasoning per page) and risk (a validated pattern is more predictable than independent per-page inference). Combine with FR-4's page-range restriction to skip pages outside the geometry-table section entirely.

Build the Synonym Map, unit normalization (→ cm), and Usage Taxonomy mapping (all FR-5) as **one reusable mechanism** — a canonical target plus a per-vendor dictionary — not three separate ones. All three are the same shape of problem (reconcile a vendor's own vocabulary/units against one canonical target); a single mechanism reused three ways is architecturally simpler than three bespoke ones.

Build Provenance (FR-6) as a **generic mechanism**, not bespoke conflict-arbitration logic. The same source+date envelope is intended to later power a brand-verified badge and an estimated-vs-confirmed measurement label (deferred features, brief addendum) — building it generically now avoids reimplementing it when those land.

Build the Fit Engine **input-shape-agnostic** rather than hard-coded around the Required Tier form. Height-only quick mode (brief addendum, deferred) and a possible future geometry-target/expert mode are two ends of one input-precision spectrum meant to share the same Fit Engine — a rigid Required-Tier-only input path would need reworking to add either later.

## Options considered, not re-litigated here

- **Ingestion trigger surface** (CLI vs. admin UI button): PRD settles on CLI for v1 (§4.2) since there's no auth surface to gate a UI trigger behind and both users have shell access. Revisit only if a non-technical user ever needs to trigger ingestion.
- **Riding style/goal input shape** (dedicated enum vs. reusing Usage Taxonomy): PRD settles on reuse (§4.1) to avoid maintaining two overlapping category lists.

## Vendor data sourcing — decided

V1 vendors: **KTM** and **Van Rysel** (§6.1). KTM carries a large number of distinct model references — expect its catalog side of the Data Pipeline work to be sized accordingly (more PDF variants/pages to reconcile through the Synonym Map than a single-lineup vendor like Van Rysel).

Any future scraping (post-v1, vendor 3+) is restricted to publicly available, officially distributed information only — PDFs or the vendor's own public website. No authenticated/restricted sources, and no third-party aggregators standing in as an "official" source for provenance arbitration (FR-6). This resolves the legal/ToS concern by policy rather than case-by-case judgment calls.

## Deployment (carried from the brief, restated for architecture)

Self-hosted, up to 5 users. No public-facing deployment, auth hardening, or scaling concerns belong in v1. A move to the public web is a possible long-term step, not a v1 requirement — architecture shouldn't hard-code assumptions that would make that move painful later, but shouldn't design for it now either.

## Open technical questions for architecture

- Per-parameter evaluation against Required Tier measurements (PRD §8, Open Question 1) — whether any of the 12 Geometry Parameters plug directly against a rider measurement (a seat-tube-related parameter against cycling inseam is the plausible candidate) is still unconfirmed; several (Reach, Stack, Head Tube Angle, ...) have no obvious direct counterpart from height/inseam/style alone regardless, and may need an additional rider input, decided when the Fit Engine is actually built. Interim v1 behavior is settled: an unevaluated parameter renders as "unknown" (no color) rather than blocking the Heatmap Table.
- Stack choice, and the concrete CI + pre-commit components that follow from it (policy already fixed in `AGENTS.md`; specifics are TODO, to be defined together).
