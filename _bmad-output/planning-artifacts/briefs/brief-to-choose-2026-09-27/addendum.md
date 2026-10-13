# Addendum: Fit my Ride

Supporting detail from the brainstorming session that doesn't belong in the brief itself, but is worth keeping for the PRD/architecture phase. See `_bmad-output/brainstorming/brainstorm-bike-selection-platform-2026-09-21/` for the full session log.

## Deployment

V1 target: self-hosted, up to 5 users (the two builders + a few others at most). No public-facing deployment, auth hardening, or scaling work belongs in v1. A move to the public web is a possible long-term step, not a v1 requirement — worth a light mention in architecture (e.g. don't hard-code assumptions that would make that move painful later) but not worth designing for now.

## Should-have (near-term after v1, not core to the bet)

- Free-text prompt as an optional layer on top of the structured form (form is the real input path; prompt is a text-to-filters translator on top).
- Height-only quick mode: rider gives just height (+ riding style), gets a shortlist via population-typical proportions, values tagged "estimated."
- Dealer list with distance (plain list, not an interactive map) — demoted from Must because shops-in-from-the-start turned out to be a nice-to-have, not important for v1.
- Shop badges: fitting-available / test-ride-available / last-verified date.
- Post-purchase feedback collection (kept vs. returned, comfort rating) — seeds a later score formula, a learned-fit model, and rating-by-rider-profile work; collection itself should start in v1 even without any UI consuming it yet.
- Search analytics logging, even with no professional-facing UI yet.

## Could-have / Won't-this-time (explicitly parked)

- Recommended/useful/optional rider-input tiers (torso length, arm length, sit bone width, flexibility, foot length, hand size, body weight, etc.) — later tiers re-rank/score rather than hard-exclude, to avoid empty result lists as inputs get more specific.
- "N of M parameters in range" as a transparent score stand-in, instead of a weighted formula.
- Geometry-target/expert mode: bypass rider measurements, enter target geometry values (with tolerance) directly — same heatmap engine, different input path. Includes a "clone my current bike" shortcut.
- Incremental refresh (hash/ETag/Last-Modified per source doc, re-parse only changed ones — LLM parsing is the costly part).
- Full interactive map, fitting-available tag + booking link, component near-miss hints (e.g. "reach 8mm short, a 10mm longer stem would fit"), frame-shape filter, made-in filter.
- Full weighted global score, brand self-service claim flow, shop-owner claim flow, user accounts, full component simulation, second-hand marketplace, club/event integration, side-by-side comparison page.

## Reusable patterns worth carrying into architecture

- **Canonical-mapping pattern**: name-synonym map (geometry fields) + unit normalization (→ cm) + usage-taxonomy mapping are one mechanism — a canonical target plus a per-vendor dictionary — not three separate ones. Build once, reuse across all three.
- **Trust envelope**: provenance + date-per-field powers vendor-conflict arbitration now, and later the brand-verified badge and estimated-vs-confirmed measurement label. Same mechanism, not bespoke logic per use case.
- **Input-precision spectrum**: height-only mode and geometry-target/expert mode are two ends of one spectrum, not competing entry points — same fit engine serves both.

## Longer-horizon ideas (well past v1, kept for context)

- Two-phase data strategy: platform seeds catalogs via PDF/scraping first (cold start), then brands "claim" and self-maintain their catalog later (self-entered data outranks seeded data in the precedence rule already decided).
- Learning-based fit: train on post-purchase feedback (kept/returned, comfort) to replace the hand-written ideal-range formula.
- Comparison as a second product axis once fit is solved: price, specs, ratings, price history.
- Reverse-search: new bike published → notify riders it fits.
- Unlimited-budget riffs (not being pursued, kept for flavor): ML models mapping measurements to bikes, brand partnerships for cleaner data feeds or co-designed bikes.

## Open questions not yet resolved

- Legal/ToS status of scraping vendor sites as a fallback data source (v1 avoids this by using PDFs only, but it's unresolved for later vendors).
- Which specific two vendors, and the source for each geometry parameter's "ideal range" (published fit methodology vs. a professional fitter's input) — needed before the fit engine can actually score anything.
- Height-only fallback proportions: what population data backs the "estimated" values.
