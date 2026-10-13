---
title: PRD: Fit my Ride
status: final
created: 2026-09-27
updated: 2026-10-11
---

# PRD: Fit my Ride

## 0. Document Purpose

This PRD is for the two people building this project (and any AI coding agent working from it). It turns the product brief's converged v1 bet into features, functional requirements, and explicit scope boundaries that architecture, epics, and stories build from. Vocabulary is Glossary-anchored (§3); features are grouped with FRs nested and numbered globally. It builds on `docs/product-brief.md` — read that first for the why; this is the what. Amended 2026-10-11 to match the architecture spine (`_bmad-output/planning-artifacts/architecture/architecture-to-choose-2026-10-11/ARCHITECTURE-SPINE.md`): 5 Core Parameters instead of 12 table columns, bikes missing a Core Parameter are blocked at ingestion, angles in degrees.

## 1. Vision

Fit my Ride is a bike-fit matching tool: a Rider enters a small set of body measurements and sees, at a glance, how well specific bikes' geometry matches their body — via a Heatmap Table comparing every candidate bike's key frame dimensions against the rider's ideal range. It's seeded with two vendors' complete catalogs, extracted from their PDF geometry tables via LLM/OCR into one Canonical Schema.

Existing bike-search tools describe bikes richly (frame material, components, wheel size) but stop short of answering the one question that actually decides a purchase: will this fit my body. This product answers that question directly, and only that question, in v1 — no marketplace, no map of where to buy, no accounts. If the fit answer alone isn't worth using on its own, nothing else about the product matters yet.

It's a hobby project for two builders, not a business: no monetization, a handful of users, self-hosted. The build itself is also the point — an excuse to see what AI-assisted tooling (PDF/OCR extraction, canonical-schema reconciliation, parallel AI coding agents) can do across a real, opinionated product.

## 2. Target User

### 2.1 Jobs To Be Done

- As a Rider (one of the two builders, or a friend they share it with), I want to know whether a specific bike will fit my body before I buy it, without manually cross-referencing PDF spec sheets across brands.
- As a builder, I want an Ingestion Pipeline I can trust well enough to skip re-checking every field by hand — the pre-commit review earns that trust.
- As a builder, I want to see what AI-assisted extraction and app-building can actually do end-to-end, on a project I care about.

### 2.2 Non-Users (v1)

- Anyone outside the self-hosted install's handful of users (public/internet-facing traffic is explicitly out of scope).
- Riders looking for a where-to-buy or test-ride answer (map/shop/dealer layer is deferred).
- Riders wanting bikes from more than the two seeded vendors.

### 2.3 Key User Journeys

- **UJ-1. You check whether your shortlisted bike actually fits before buying it.**
  - **Persona + context:** You (or your friend), about to buy a new bike, unsure whether the reach and stack actually work for your body.
  - **Entry state:** On the self-hosted web app (PWA), no login — v1 has no accounts.
  - **Path:** Enter height, cycling inseam, and riding style/goal → submit → view the Heatmap Table of both vendors' bikes → sort by In-Range Count → sort by one column you care about (e.g. reach) to see how far off borderline bikes are.
  - **Climax:** The diverging cell colors tell you, parameter by parameter, which bikes are ideal / too-long / too-short for your body — no more mental math off a PDF spec sheet.
  - **Resolution:** You walk away knowing which 1-2 bikes are worth test riding.
  - **Edge case:** A Core Parameter that has no evaluation method yet shows "unknown" for that cell, rather than being falsely marked in-range or silently excluding the bike. (A bike missing a Core Parameter value never reaches the catalog; see FR-7.)

- **UJ-2. You add a new vendor's catalog without hand-editing the database.**
  - **Persona + context:** You (the builder), with a vendor's PDF geometry spec sheet in hand.
  - **Entry state:** On the ingestion trigger surface, vendor PDF file ready.
  - **Path:** Trigger ingestion for the vendor → the pipeline runs LLM/OCR extraction → you get a pre-commit summary listing every field (value, unit, source, matched synonym) → you scan it for anything that looks wrong → you approve → data commits to the Canonical Schema.
  - **Climax:** Catching a bad synonym match before it corrupts the schema, because the review step showed it plainly.
  - **Resolution:** The vendor's full catalog is now queryable in the same canonical units and taxonomy as the other vendor, ready to appear in riders' heatmaps.
  - **Edge case:** Re-running ingestion on the same, unchanged PDF produces no duplicate or altered records (idempotent).

## 3. Glossary

- **Rider** — The person using the platform to evaluate bike fit.
- **Required Tier** — The mandatory rider input (height, cycling inseam, riding style/goal) that hard-excludes non-fitting bikes; the only input tier active in v1.
- **Geometry Parameter** — A single measurable frame dimension. The fixed v1 set is 12 parameters, in two classes. Naming and units follow Van Rysel's own geometry table, used as the Canonical Schema's baseline (see Synonym Map). Distinct from wheel size (§5).
- **Core Parameter** — One of five Geometry Parameters that every vendor must supply for every bike and size, and the only columns of the v1 Heatmap Table: Head Tube Angle (HTA, degrees), Stack (S, cm), Reach (R, cm), Seat Tube Angle (STA, degrees), Bottom Bracket Drop (BB, cm).
- **Optional Parameter** — The other seven Geometry Parameters: Seat Tube Length, Head Tube Length, Top Tube Length, Chainstay Length, Fork Length, Fork Rake, Wheel Base (all cm). Stored when the vendor publishes them; not shown in v1.
- **Canonical Schema** — The platform's unified set of Geometry Parameter names and units (lengths in centimeters, angles in degrees) that every vendor's data is mapped onto, per model and per frame size.
- **Synonym Map** — A per-vendor dictionary translating that vendor's own field names to the Canonical Schema. Needed because vendors name the same parameter differently — the Canonical Schema uses Van Rysel's naming; KTM's equivalents are reconciled through this map (FR-5).
- **Usage Taxonomy** — The fixed set of riding-style categories (road, gravel, MTB, city/commute, touring, e-bike) that each vendor's own categories are mapped onto at ingestion.
- **Provenance** — The recorded source and date of a stored Geometry Parameter value, used to arbitrate conflicts between sources.
- **Heatmap Table** — The fit-comparison output: one bike per row, one Geometry Parameter per column, each cell colored on a diverging scale relative to the Rider's ideal range.
- **In-Range Count** — The number of a bike's Geometry Parameters that fall within the Rider's ideal range; usable as a sort key in place of a weighted score.
- **Ingestion Pipeline** — The manually triggered, idempotent process that extracts a vendor's PDF geometry data into the Canonical Schema.

## 4. Features

### 4.1 Fit Engine

**Description:** The Rider supplies Required Tier measurements and gets back a Heatmap Table of candidate bikes across the 5 Core Parameters (§3), sortable by column or by In-Range Count. Riding style/goal is selected from the same fixed Usage Taxonomy used for vendor category mapping, not free text — one taxonomy, not two. Realizes UJ-1.

**Functional Requirements:**

#### FR-1: Required Tier fit filtering

A Rider can submit height, cycling inseam, and riding style/goal to receive a filtered comparison of candidate bikes. Realizes UJ-1.

**Consequences (testable):**
- A bike is excluded only when a Core Parameter value with a defined evaluation method falls outside the Rider's ideal range for that parameter.
- A Core Parameter with no evaluation method never excludes a bike — its cell renders as "unknown" (see FR-2).
- Exclusion is decided in the fit engine, never in the page template.

#### FR-2: Heatmap Table output

A Rider can view a Heatmap Table of the bikes remaining after FR-1, one row per bike model, one column per Core Parameter, each cell colored on a diverging scale (too-short / ideal / too-long) relative to the Rider's ideal range. Realizes UJ-1.

**Consequences (testable):**
- Each row shows the Rider's best-fitting frame size for that model (named in the row); size never filters or sorts rows.
- Values without an evaluation result render as a distinct "unknown" cell state (no color applied to the cell) — never blank in the sense of omitted, never silently dropped from the row.
- The color scale is continuous/diverging, not a binary good/bad flag.
- If a Geometry Parameter directly corresponds to a Required Tier measurement, the comparison is a direct plug — no third-party fit methodology or professional fitter involved. Whether any of the 5 Core Parameters have such a direct correspondence, which ones, and how the rest are evaluated, is still fully open (§8, Open Question 1).
- A Core Parameter without a resolved evaluation method (§8, Open Question 1) renders as "unknown" — no color applied — for every bike. This is a v1 fallback so the Heatmap Table can ship without waiting on that open question, not a statement that the data is missing. Defining the evaluators is the first piece of build work.

#### FR-3: Heatmap sorting

A Rider can sort the Heatmap Table by any single Geometry Parameter column, or by In-Range Count. Realizes UJ-1.

**Consequences (testable):**
- No weighted or composite fit score is computed or displayed anywhere in v1.

### 4.2 Data Pipeline

**Description:** A manually triggered, idempotent pipeline extracts a vendor's PDF geometry tables into the Canonical Schema, with a mandatory pre-commit review step. The trigger is a CLI command, not an admin UI button — v1 has no accounts/auth surface to gate a UI trigger behind, and the two people running ingestion are also the ones with shell access. Realizes UJ-2.

**Functional Requirements:**

#### FR-4: Manual, idempotent ingestion trigger

A builder can manually trigger ingestion for one vendor's PDF catalog. Realizes UJ-2.

**Consequences (testable):**
- Re-running ingestion against unchanged source PDFs produces no duplicate or altered records.
- The system supports a maximum of 2 vendors in v1.
- A trigger can restrict extraction to a specified page range within a vendor's PDF, instead of always processing the whole document.

**Out of Scope:**
- Scheduled/automatic ingestion (manual trigger only in v1).
- Any data source other than vendor PDFs (no scraping, no vendor APIs).

#### FR-5: Canonical extraction and mapping

The system extracts Geometry Parameter values per model and per frame size from a vendor's PDF through a dedicated per-vendor adapter (using LLM/OCR where needed) and maps them into the Canonical Schema (Synonym Map + unit conversion) and the Usage Taxonomy. The Canonical Schema's field names and units follow Van Rysel's own geometry table; KTM's differently-named equivalents are reconciled through the Synonym Map. Realizes UJ-2.

**Consequences (testable):**
- A field name the Synonym Map doesn't recognize is flagged for review, never silently dropped or guessed.
- Every stored length is in centimeters and every angle in degrees, regardless of the source unit.
- Every vendor must supply all 5 Core Parameters; the 7 Optional Parameters are stored when present.
- Adding a vendor means adding one adapter (with its Synonym Map and fixtures), with no change to the fit engine or the web app.

#### FR-6: Provenance-based conflict arbitration

Every ingested field stores its Provenance (source, date); conflicting values across sources are resolved automatically before commit. Realizes UJ-2.

**Consequences (testable):**
- An official vendor source outranks scraped, community, or aggregator sources.
- Among multiple official sources, the most recently dated value wins.
- Arbitration is short-circuiting: once an official-source value is found for a field, lower-precedence sources are not consulted for that field.

#### FR-7: Pre-commit parser review

A builder can review a summary of everything the parser extracted (field, value, unit, source, matched synonym) before it is written to the database, and must approve it before commit. Realizes UJ-2.

**Consequences (testable):**
- No extracted record reaches the database without passing through this review step.
- A bike missing any Core Parameter in any size is blocked from ingestion and listed in the review; other bikes in the batch can still be approved.
- When FR-6 resolves a conflict between sources, the review summary flags that arbitration happened, not just the winning value — so a builder can see a conflict was silently settled rather than trusting a single number that looks uncontested.

## 5. Non-Goals (Explicit)

- Not a marketplace, and not a where-to-buy map/dealer directory in v1 (see §6.2 for the deferred version).
- Not a monetized product — no ads, no paid tier, no revenue model.
- Not a public/multi-tenant web service — v1 is self-hosted for a handful of users, not internet-scale.
- Not a spec-sheet browser — frame material, components, wheel size (distinct from Wheel Base, a Geometry Parameter, §3), and other non-geometry specs are not modeled in v1.
- Not building user accounts, saved profiles, or any auth layer in v1.
- Not computing or displaying a weighted global fit score in v1.
- Not scraping vendor websites or calling vendor APIs — PDF extraction only.

## 6. MVP Scope

### 6.1 In Scope

- Required Tier rider input and hard-exclusion filtering (FR-1).
- Heatmap Table output over the 5 Core Parameters, sortable by column or In-Range Count (FR-2, FR-3).
- Two vendors, full catalogs, PDF/OCR-seeded (FR-4): **KTM** and **Van Rysel** — chosen for contrasting PDF layouts, to stress-test the parser and Synonym Map early.
- Canonical Schema + Synonym Map + unit normalization (cm, degrees) + Usage Taxonomy mapping (FR-5).
- Provenance-based conflict arbitration (FR-6).
- Manual-trigger, idempotent ingestion with mandatory pre-commit parser review (FR-4, FR-7).
- Self-hosted deployment for up to 5 users; delivered as a PWA (installable, usable on desktop or phone browser).

### 6.2 Out of Scope for MVP

- **Free-text prompt** as an input shortcut on top of the structured form — quality-of-life, not core to the fit bet.
- **Height-only quick mode** (population-typical proportions, values tagged "estimated") — the other end of the input-precision spectrum; deferred until the Required Tier path is proven.
- **Dealer list with distance** and **shop badges** (fitting-available / test-ride-available / last-verified) — the entire shop/map layer is deferred; v1 must prove the fit layer is worth using on its own first.
- **Post-purchase feedback collection** (kept vs. returned, comfort rating) — fully out of scope for v1, not just deferred. Collecting this meaningfully means being able to contact the rider after purchase, which needs some form of account or stored contact info — and v1 has no accounts. Revisit once there's a way to reach a rider post-purchase, not before.
- **Search analytics logging** (what riders search for — measurements, filters, results shown) — deferred from MVP FRs, but unlike feedback collection this doesn't need to identify or contact anyone, so starting silent collection early (no consuming UI yet) stays cheap to bolt on during the Data Pipeline build if it turns out convenient.
- **User accounts** — no auth layer to build against in v1; any saved state has none to build on.
- **Weighted global fit score** — no ideal-range-weighting formula exists yet; In-Range Count (FR-3) is the v1 stand-in.

## 7. Success Metrics

Hobby-scale — kept deliberately light.

**Primary**
- **SM-1**: You (or your friend) actually use the Heatmap Table to help decide on a real bike purchase, at least once, and it makes that fit judgment easier and clearer than reading two vendors' spec sheets by hand. Validates FR-1, FR-2, FR-3.
- **SM-2**: Both vendors' full catalogs ingest via FR-4-FR-7 with zero manual database edits required to fix bad data. Validates FR-4, FR-5, FR-6, FR-7.

**Counter-metrics (do not optimize)**
- **SM-C1**: Don't expand the parameter set, vendor count, or input tiers before the 2-vendor / 5-Core-Parameter v1 works end-to-end — breadth-creep before the core loop works is exactly the failure mode v1's scope was cut to avoid. Counterbalances SM-2.

## 8. Open Questions

1. How does each of the 5 Core Parameters (§3) get evaluated against the Rider's Required Tier measurements? Stack and Reach plausibly relate to height and inseam through a rule of thumb; Head Tube Angle, Seat Tube Angle and Bottom Bracket Drop have no obvious counterpart from height/inseam/riding-style alone. May turn out to need an additional rider input. This is the first piece of build work. Until resolved, unevaluated parameters render as "unknown" in the Heatmap Table (FR-2).
2. ~~Stack and CI/pre-commit~~ Resolved in the architecture spine: one Python app, server-rendered pages with htmx, SQLite, Docker on a home server, `ruff` + `pytest` via pre-commit and GitHub Actions.
