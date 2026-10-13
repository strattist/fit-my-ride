# Brainstorm Intent: Bike Selection Platform (v1)

## Product Concept
A bike-fit matching platform: riders enter measurements, get a heatmap-scored comparison of bike geometries against their body, seeded from 2 vendors' PDF spec sheets. Core bet: rider-measurement-based geometry fit (not spec-sheet browsing, not a marketplace, not a map) is the differentiator worth shipping alone, before any shop/where-to-buy layer exists.

## V1 Must-Have Scope

**Fit engine**
- Required-tier rider input only: height, cycling inseam, riding style and goals. This tier is the only one that hard-excludes non-fitting bikes.
- Heatmap table output: one bike per row, one geometry parameter per column, cell color diverging relative to the rider's ideal range per parameter (too short / ideal / too long), not a flat good/bad scale.
- Ranking via heatmap interaction, not a computed score: sortable by any column, or by count of in-range parameters. No weighted global-score formula in v1 (demoted to Could — no formula exists yet).

**Data pipeline**
- Maximum 2 vendors, each with a complete catalog, seeded via vendor PDF geometry tables (LLM/OCR extraction). Vendors chosen for contrasting PDF layouts to stress-test the parser and synonym map early.
- Canonical geometry schema plus per-vendor synonym map, reconciling naming variants (e.g. "seat tube angle" / "STA" / "seat angle") into one schema. Start with a small core parameter set (stack, reach, top tube, seat angle, standover) and grow only when a filter needs it.
- Canonical unit: centimeters (cm) for all geometry values. Per-vendor unit conversion happens at ingestion, alongside the name synonym mapping.
- Usage taxonomy mapping: a small fixed category set (road, gravel, MTB, city/commute, touring, e-bike, ...) that each vendor's own category names are mapped onto at ingestion.
- Provenance and date stored per field, to arbitrate conflicts: official vendor source outranks scraped/community/aggregator sources; among conflicting official sources, most recent wins; cascade is short-circuiting (stop once an official source is found).
- Ingestion is one idempotent pipeline, manually triggered (CLI/admin button) in v1 — no scheduler yet.
- Pre-commit parser-review summary: before any extracted data is committed to the database, show what the parser extracted per field (value, unit, source, matched synonym) for review.

**Map / shops**
- Nothing in Must. The dealer-list feature was demoted to Should; the entire shop/map layer (dealer list, badges, claim flow) is deferred to a fast-follow. V1's Must-have spine is purely the fit engine plus the data pipeline.

## V1 Should-Have Scope
(Second-priority, near-term-after-Must — not core to the v1 bet.)

- Free-text prompt as an optional layer on top of the structured form: the form (measurements + usage + budget) is the real input path; the prompt is a text-to-filters translator on top of it, not a required feature.
- Height-only quick mode: rider supplies just height (plus riding style) and still gets a usable shortlist via population-typical proportions, values tagged "estimated."
- Dealer list with distance (demoted from Must): a plain list of dealers, not an interactive map.
- Shop badges: fitting-available / test-ride-available / last-verified date.
- Post-purchase feedback collection (kept vs. returned, comfort rating) — seeds later score-formula, learned-fit-model, and rating-by-rider-profile work, but collection itself starts in v1.
- Search analytics logging, even with no professional-facing UI yet, so history exists for later use.

## Core Synthesis Insights (shape how this gets built)

- **Canonical-mapping pattern**: name-synonym map (geometry field names) + unit normalization (→ cm) + usage-taxonomy mapping are one reusable pattern — a canonical target plus a per-vendor dictionary — not three separate mechanisms. Build it once, reuse it across all three.
- **Single trust envelope**: provenance + date-per-field is one mechanism that powers vendor-conflict arbitration now, and will later power the brand-verified badge and the estimated-vs-confirmed measurement label. Design it as one envelope, not bespoke logic per use case.
- **Input-precision spectrum**: height-only mode and geometry-target/expert mode are two ends of a single input-precision spectrum, not competing entry points — the same fit engine should serve both ends.
- **Differentiator bet**: deferring the entire shop/map layer sharpens the v1 bet deliberately — the fit layer alone must be worth using before any where-to-buy utility exists. This resolves the "map is real value but not essential to fit" tension by choosing fit-only first.

## Key Decisions / Constraints (v1 scope and architecture)

- Max 2 vendors with complete catalogs (not many vendors shallow) — depth over breadth for v1.
- Cm is the sole canonical geometry unit; all vendor units are converted at ingestion.
- Ingestion is manual-trigger and idempotent, with a mandatory pre-commit parser-review summary (field/value/unit/source/matched-synonym) — no automatic scheduling in v1.
- Hard-exclude filtering applies only at the required input tier (height, cycling inseam, riding style/goals); no other tiers are active for filtering in v1 (recommended/useful/optional tiers are Could).
- Ranking is done via heatmap sort / in-range-parameter count, not a computed weighted score — no scoring formula exists yet, and building one is explicitly out of v1 scope.
- Data-conflict precedence: official vendor source > scraped > community/aggregator; most recent wins among official sources; cascade stops at the first official hit.
- Sparse/missing attribute data is shown honestly as "unknown," never silently excluded.
- No user accounts in v1 (Won't-this-time); this affects architecture in that any saved state (e.g. measurements) has no auth layer to build against in v1.
