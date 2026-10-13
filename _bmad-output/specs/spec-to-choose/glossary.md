# Glossary

Terms used across this spec. Where this file and `docs/prd.md` §3 differ, this file wins.

- **Rider** — person evaluating bike fit.
- **Required Tier** — the rider's inputs only: height, cycling inseam, riding style. Never used for bike parameters.
- **Core Parameter** — one of five frame values required from every vendor and shown in the v1 table: Head Tube Angle `HTA` (deg), Stack `S` (cm), Reach `R` (cm), Seat Tube Angle `STA` (deg), Bottom Bracket Drop `BB` (cm).
- **Optional Parameter** — one of seven further values stored when a vendor publishes them, not shown in v1: Seat Tube Length, Head Tube Length, Top Tube Length, Chainstay Length, Fork Length, Fork Rake, Wheel Base (all cm).
- **Canonical Schema** — the single set of parameter names, units and record shapes in `core/schema`; naming follows Van Rysel.
- **Synonym Map** — per-vendor dictionary from that vendor's field names to the Canonical Schema, owned by the vendor's adapter.
- **Usage Taxonomy** — fixed riding-style set (road, gravel, MTB, city/commute, touring, e-bike); also the rider's style input.
- **Adapter** — per-vendor module with a `plan` phase (what to extract) and a pure `map` phase (raw fields to canonical records).
- **Provenance** — source and date of a stored value, used for arbitration.
- **Heatmap Table** — one row per bike model, one column per Core Parameter, cells coloured against the rider's ideal range.
- **Evaluator** — named function judging one Core Parameter value for a rider; returns `unknown` or a signed deviation from the ideal range.
- **In-Range Count** — number of a bike's Core Parameters within range; a sort key, not a score.
- **Ingestion Pipeline** — manual, idempotent flow: extract, map/convert, arbitrate, stage, review, commit.
- **Approved files** — reviewed extraction output under `data/ingested/<vendor>/`, tracked in git; the catalog database is derived from them.
