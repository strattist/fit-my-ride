# Adversarial Review — Architecture Spine (Fit my Ride)

Reviewed: `ARCHITECTURE-SPINE.md` (draft, 2026-10-11) against `docs/prd.md` (final).
Method: for each finding, two units one level down (agents/builders in separate worktrees) that each obey every AD literally yet produce incompatible work, or a PRD requirement no AD owns.

## Verdict

**Not safe to fan out to parallel builders yet.** The paradigm and layering are sound, but the spine leaves 4 seams where compliant builders collide (adapter/LLM contract, who owns unit conversion and the record shape, the approved-file schema, the evaluator output type) and silently narrows PRD scope (12 -> 5 columns; blocked bikes vs "unknown" cells). About 10 tightened/added ADs close it. None require changing the stack.

Severity: B = blocker (will cause rework or a wrong product), M = major, m = minor.

---

## F1 (B) PRD scope silently narrowed: 12 columns vs 5, and "unknown due to missing data" made unreachable

- **Units:** Web builder (renders the Heatmap Table) vs PRD-driven test author / adapter builder.
- **Incompatibility:** PRD FR-2 / Glossary: one column per Geometry Parameter, fixed set of 12; SM-C1 forbids changing the set. AD-3 makes only 5 Core Parameters "the only columns in the v1 table" and 7 "not shown in v1". A builder following AD-3 ships 5 columns and is compliant; one following the PRD ships 12. Separately, AD-7 blocks any bike missing any Core Parameter in any size, so it never reaches the catalog. PRD FR-1/FR-2/UJ-1 edge case says such a bike must still appear with an "unknown" cell. With AD-7 as written that state can only occur for the 7 Optional parameters, which AD-3 does not show. The PRD behaviour is unreachable. SM-2 ("full catalogs ingest") is also unmeetable for any blocked bike.
- **Fix:** Either amend the PRD explicitly (5 shown, 7 stored, UJ-1 edge case reworded) or revert AD-3 to 12 columns. Decide and record in AD-3. Rewrite AD-7: a bike missing Core data is **committed with explicit `missing` cells** and flagged in review; only structurally unusable records (no model identity, no sizes) are blocked. Add a PRD-coverage line stating which FR consequences are intentionally changed.

## F2 (B) Adapter contract cannot be implemented as written: adapters may not reach the LLM

- **Units:** KTM adapter builder vs Van Rysel adapter builder (or either vs ingestion builder).
- **Incompatibility:** AD-4: adapter "given a PDF ... returns canonical records", may only read the PDF, never writes. AD-6: LLM only via `ingestion/llm`, adapters "supply the prompt, page selection, output schema". The dependency graph forbids `adapters -> ingestion`. So an adapter cannot call the helper. Builder A (clean PDF, pdfplumber only) writes `extract(pdf) -> records`. Builder B (messy PDF) needs the LLM, and either (i) imports `ingestion.llm` (violates graph), (ii) accepts an injected callable (a different signature from A), or (iii) exposes `prompt()/schema()/parse(raw)` and expects ingestion to orchestrate. All three obey some AD text; none interoperate. OCR (PRD FR-5 "LLM/OCR") has no owner either.
- **Fix:** New/tightened AD-4: contract is **two-phase** and defined once in `adapters/contract` (or `core/schema`): `plan(pdf, pages) -> ExtractionPlan` (page selection, deterministic table reads, optional LLM request spec), then `map(raw_extraction) -> list[Result]`. Ingestion owns calling pdfplumber/OCR/LLM. Adapters are therefore pure given raw extraction (and trivially fixture-testable). State where OCR lives.

## F3 (B) Two owners of unit conversion and of the canonical record type

- **Units:** Adapter builder vs core/schema builder (and catalog loader builder).
- **Incompatibility:** AD-1 says unit conversion and canonical naming are implemented once in `core/` and imported by both shells. AD-4 says the adapter "owns that vendor's ... unit conversions". An adapter builder hand-rolls mm->cm (rounding to 1 decimal); another uses `core/units` (no rounding, or 2 decimals). Both comply. Likewise the "canonical record" shape (value, unit, source page, original field name) is described in AD-4 but placed in no module. `core/schema` is only named for the parameter set. Ingestion, adapters and catalog loader each end up with their own dataclass.
- **Fix:** AD-3/AD-4: `core/units` is the only conversion code; adapters declare *source unit per field* in data and call core. `core/schema` also owns the `ParameterValue`, `SizeRecord`, `BikeRecord`, `Provenance` and `Result` types, the rounding/precision rule (store at source precision, convert once, round once), and the identity/slug function (see F8).

## F4 (B) No owner or definition of the approved-file schema; catalog loader and ingestion can disagree

- **Units:** Ingestion/staging builder vs `catalog load` builder.
- **Incompatibility:** AD-2 makes files the source of truth; Conventions say "JSON, sorted keys, schema_version". Nothing says the file granularity (per vendor? per model? per run?), the envelope, whether staged and approved shapes are identical, or what the loader does on an unknown `schema_version`. Graph shows both depend only on `core`, so the schema must live there, but AD-3 only lists parameters. Granularity also matters for the worktree policy: two agents re-ingesting the same vendor produce whole-file merge conflicts if there is one file per vendor.
- **Fix:** New AD: "Approved file format" in `core/schema`: one JSON file per `(vendor, model)` under `data/ingested/<vendor>/<model_slug>.json`, envelope `{schema_version, bike_id, sizes[], provenance[], idempotency_key, adapter_version}`; staged files use the same shape plus a `review` block that is stripped on approval. Loader rejects unknown major `schema_version` and fails the build (not the server).

## F5 (B) Fit evaluator output type is undefined: enum vs signed magnitude

- **Units:** `core/fit` evaluator builder vs web renderer / sorter builder.
- **Incompatibility:** AD-8: evaluator maps to "a diverging cell state". PRD FR-2: scale is continuous/diverging, not binary; UJ-1 says sort a column to see "how far off borderline bikes are". Builder A returns an enum (`too_short|ideal|too_long|unknown`). Builder B returns a signed float. The renderer written to A cannot draw gradients; the sorter written to B cannot determine "in range" without a threshold. In-Range Count definition ("falls within the ideal range") has no stated inclusive/exclusive bounds or tie handling.
- **Fix:** AD-8: evaluator returns `CellEval(state, deviation: float|None, range: (lo, hi)|None)`; `state` derived from `deviation` by one function; `unknown` iff `deviation is None`. In-Range Count counts `state == ideal` only. Specify sort policy for `unknown`: always last, regardless of direction; ties broken by model name.

## F6 (B) FR-1 exclusion has no owner; spine contradicts or ignores it

- **Units:** Fit-engine builder vs web builder.
- **Incompatibility:** FR-1 says bikes outside the ideal range are *excluded* (and FR-2 shows "the bikes remaining after FR-1"). UJ-1 and FR-2's too-short/too-long colours, plus sort-by-reach "to see how far off borderline bikes are", only make sense if out-of-range bikes stay visible. AD-5 says "Size never filters", AD-8 says nothing of exclusion. The core builder implements no exclusion (compliant); the web builder adds a `?hide_out_of_range` filter on its own in the template (compliant, but now evaluation logic lives in a template, which AD-8 says to prevent). Which parameters trigger exclusion, and per size or per chosen size, is open.
- **Fix:** Add to AD-8/AD-5: `core/fit.evaluate(rider, models) -> list[ModelResult]` is the only place that excludes; define exclusion rule exactly ("exclude a model iff its chosen size has a *known* Required-Tier-correspondent parameter outside range"; and state the visible-vs-excluded split the UI shows). If PRD is contradictory, flag it as a PRD defect to resolve before epics.

## F7 (M) Size selection criterion undefined, and circular with the "all unknown" default

- **Units:** Fit-engine builder writing size selection vs builder writing evaluators.
- **Incompatibility:** AD-5: "the core picks the best-fitting size". Best by what: max In-Range Count, min total |deviation|, a stack/reach target? AD-8 says unevaluated parameters are `unknown` and PRD OQ1 says none has a resolved method. With every evaluator unknown, there is no best size, In-Range Count is 0 for all, FR-1 never excludes, and the v1 heatmap is a grey table. Two builders will invent different tiebreakers (smallest size, middle size, first).
- **Fix:** AD-5: size choice = max In-Range Count, tiebreak min sum of |deviation| over known cells, then the size with the lowest explicit sort order; if all unknown, report `size=None` and show all sizes' values rather than picking one. Add a v1 acceptance gate: at least N evaluators (state which) must be non-`unknown` before UJ-1 is considered delivered, or the spine must say outright that v1 ships with a partly grey table.

## F8 (M) Bike identity and size labelling are underdetermined (model year, variants)

- **Units:** KTM adapter vs Van Rysel adapter.
- **Incompatibility:** Identity is `<vendor_slug>:<model_slug>`. KTM slugs "Revelator Alto Master" as `revelator-alto-master`; Van Rysel adapter slugs "RCR Pro 2026" as `rcr_pro_2026` (the year in the id) and uses underscores (the vendor slug example uses `van_rysel`). Same model across catalog years: overwrite or new entity? Several trims sharing one geometry: one model or several? Size sort order "explicit" but assigned by whom (S/M/L vs 49-58 vs "ML")?
- **Fix:** Slug function in `core`; hyphen vs underscore chosen once. State: identity excludes model year; catalog year lives in provenance `source_date`; trims sharing a geometry table are one model with `variants` names (or separate; pick one). Size sort order = ascending by the adapter-supplied rank, validated by core as dense integers.

## F9 (M) Idempotency key does not cover what changes the output; and provenance date can break idempotency

- **Units:** Pipeline builder vs LLM helper builder (and adapter builder).
- **Incompatibility:** AD-7 key = hash(vendor, PDF content, page range, adapter version). The LLM provider/model/prompt version/cache state is outside the key. Swapping Claude to OpenAI (AD-6 "a config choice") yields different values under an unchanged key; the pipeline either short-circuits ("zero changes", stale data) or re-extracts (violating the key semantics). Separately, every value carries `source_date`; if the builder fills it from the wall clock, a re-run changes every record, contradicting FR-4. AD-1 forbids the clock in core, so it will be injected, but from where is not said. Also unspecified: where the key is stored and compared to, and what a *changed* PDF does to models no longer present (delete or keep?).
- **Fix:** AD-7: `source_date` is the document's publication date supplied by the operator/adapter, never `now()`. Add provider+model id+prompt hash to the key, or state that the helper cache (keyed on them) is the idempotency boundary. Key stored inside each approved file. Re-ingest semantic is "replace per `(vendor, model)`, report vanished models in review, never auto-delete."

## F10 (M) Conflicting mutation paths into adapter mapping data and the LLM cache

- **Units:** Review/ingestion builder vs adapter builder.
- **Incompatibility:** AD-4: adapters never write files; AD-6: LLM may "suggest a mapping flagged for review". Where does an *approved* suggestion go? The only persistence for Synonym Maps is "adapter mapping data". Ingestion builder writes accepted synonyms into `adapters/<vendor>/synonyms.json` (breaks the graph and "adapters never write"); adapter builder hand-edits it in the same PR. In addition, the LLM "result caching" location is unstated: committed (reproducible, bloats the repo) or gitignored (re-spend and non-reproducible on a second worktree).
- **Fix:** AD-4/AD-7: Synonym Maps are data files under `adapters/<vendor>/mapping/`, edited only by a human in a normal commit; review output emits a *proposed-patch* file, never applies it. State the cache path (e.g. `.cache/llm/`, gitignored) and that approved output, not the cache, is the reproducible record.

## F11 (M) Usage Taxonomy and rider input have no owner in `core/schema`

- **Units:** Web form builder vs adapter builder.
- **Incompatibility:** PRD: one fixed taxonomy (road, gravel, MTB, city/commute, touring, e-bike) used both for rider "riding style/goal" and vendor category mapping. AD-4 puts "Usage Taxonomy mapping" in each adapter; AD-3 does not list the taxonomy in `core/schema`; the ER diagram has no category attribute on `MODEL`. Web builder hardcodes an enum in a template; adapter builders define their own string values (`gravel` vs `Gravel` vs `gravel_bike`, `e_bike` vs `ebike`). No AD says how a bike's category affects results at all (FR-1 filters on geometry only), so it is plausibly a no-op.
- **Fix:** AD-3: `core/schema` owns the Usage Taxonomy enum and `RiderInput` (height_cm, inseam_cm, style) with validation ranges. ER: `MODEL.categories[]` (zero-or-more, unmapped -> `unrecognized`). State explicitly whether style influences evaluation in v1.

## F12 (M) Parameter semantics not pinned: adapters will map different measurements to the same code

- **Units:** KTM adapter vs Van Rysel adapter.
- **Incompatibility:** AD-3 names `BB` "Bottom Bracket Drop (cm)" and `STA`, `S`, `R`. Vendors publish BB *height* or BB *offset*, effective vs actual seat tube angle, c-c vs c-t seat tube length, stack/reach to different datum. KTM's adapter maps its BB height to `BB`; Van Rysel's reports drop (a different sign and magnitude). Each is "mapped to canonical". Also PRD says the schema follows Van Rysel's table, but nothing in the spine records Van Rysel's definitions, so "canonical" is whatever the first adapter did.
- **Fix:** AD-3: add a definition column per parameter (measurement, datum, sign convention) in `core/schema`, sourced from Van Rysel's table. Adapter must either supply the canonical-definition value or return `unrecognized`/`missing` with a reason; a derivation (e.g. drop from height + wheel radius) must be an explicit, named function in core, reviewed.

## F13 (M) Rider data on the server despite AD-9: URL query strings and service worker

- **Units:** Web/FastAPI builder vs PWA/ops builder.
- **Incompatibility:** AD-9 puts rider inputs and sort order in the page URL and says the server "logs no rider measurements". Default uvicorn access logs record the full request line including the query string. A compliant builder uses GET `?height=..&inseam=..`, the default server config logs every rider's measurements, and observability is "Deferred". The PWA service worker may cache rider-specific URLs. Also unspecified: whether the URL carries metric (convert at the edge, bookmarkable and unambiguous) or the entered imperial value, and where conversion code lives (core vs web; see F3).
- **Fix:** AD-9: URL carries metric canonical values only plus a `units` display flag; access log disabled or path-only formatter; service worker caches static shell only, never the result route. Imperial/metric conversion functions are in `core/units`.

## F14 (m) Catalog build moment and read-only guarantees are ambiguous

- **Units:** Dockerfile builder vs web builder.
- **Incompatibility:** AD-11: DB built "at image build or container start". Building at start needs the loader and a writable path inside a container whose app opens it read-only; building at image build bakes catalog into the image (updates need a rebuild, fine). One builder writes a start script that needs a writable FS; the other a build-stage step. "No ingestion dependencies' credentials" is also ambiguous (no *keys*, or no ingestion libraries?). The single Python package ships `ingestion` and its LLM SDKs into the image.
- **Fix:** AD-11: DB built at image build only; container filesystem may be read-only; web opens with `mode=ro&immutable=1`. The runtime install group excludes ingestion/LLM dependencies (uv dependency groups).

## F15 (m) Review gate is convention, not mechanism; approval path for unattended agents is missing

- **Units:** Ingestion builder vs any other builder / AI agent.
- **Incompatibility:** FR-7: "no extracted record reaches the database without review". AD-2/AD-7: only convention keeps files out of `data/ingested/`; nothing marks an approved file as having passed review (a hand-edited or agent-generated JSON loads fine). The gate is an interactive terminal prompt; agents in worktrees cannot answer it, so either it grows a `--yes` flag (defeating the gate) or agents hand-write files. Approve granularity (whole batch / per model / per field) and what "abort" leaves behind are unspecified. Review also must show the Usage Taxonomy mapping and losing arbitration candidates; AD-4's record carries neither, and the approved file stores only the winner.
- **Fix:** AD-7: approval writes `review: {approved_by, approved_at, report_hash}` into each approved file; loader refuses files without it (CI test). Per-model approval granularity. Non-interactive approval only via an explicit `--approve-report <hash>` that references a report a human has seen. Records keep losing candidates in provenance.

## F16 (m) Vendor registry and the 2-vendor limit have no owner

- **Units:** CLI builder vs catalog loader builder.
- **Incompatibility:** FR-4 sets a max of 2 vendors; the spine says the adapter contract "already allows more". CLI enumerates vendors by scanning `adapters/`; loader enumerates `data/ingested/`; slug validation differs. No owner for the limit.
- **Fix:** One `VENDORS` registry in `core/schema` (slug, display name, adapter path), used by CLI, loader and tests; limit stays a test, not code.

---

## PRD coverage gaps (no AD owns them)

| PRD item | Gap |
| --- | --- |
| FR-1 exclusion, UJ-1 | No owner (F6) |
| FR-2 12 columns | Narrowed to 5 without PRD change (F1) |
| FR-2 continuous scale | Cell state type undefined (F5) |
| FR-3 sort of `unknown` | Policy undefined (F5) |
| FR-4 2-vendor limit, page range | Limit unowned (F16); page range is in key, but merging partial-range runs into existing files is undefined (F9) |
| FR-5 "LLM/OCR" | OCR has no component (F2) |
| FR-5 Usage Taxonomy | Not in core/schema (F11) |
| FR-6 arbitration | Only one source per run exists in practice; source rank class and where prior approved values enter arbitration are unspecified (F9, F15). Define source classes (`official`, other) in `core/schema` and say whether arbitration spans runs |
| FR-7 "matched synonym" | AD-4 returns original field name, not the matched map entry/confidence; add to record |
| PWA | Installability only; offline use impossible with server-side core. State that as a non-goal, and cache policy (F13) |
| SM-2 "zero manual DB edits" | No path for correcting a wrong value except re-ingest or editing JSON; state the sanctioned correction path (override file with provenance) |

## Summary of AD changes

| AD | Change |
| --- | --- |
| AD-3 | Add parameter definitions, taxonomy, types, vendors registry, slug rule; resolve 12 vs 5 (F1, F3, F8, F11, F12, F16) |
| AD-4 | Two-phase contract; no conversions outside `core/units`; mapping files human-edited (F2, F3, F10) |
| AD-5 | Size-selection rule and the all-unknown case (F7) |
| AD-7 | Missing Core => commit with `missing`; key contents; date source; replace semantics; mechanical approval marker (F1, F9, F15) |
| AD-8 | Evaluator return type; exclusion owner; unknown sort policy (F5, F6) |
| AD-9 | Metric-only URL, log suppression, cache scope (F13) |
| AD-11 | Build at image build, read-only FS, dependency groups (F14) |
| New AD | Approved-file schema and granularity (F4) |
