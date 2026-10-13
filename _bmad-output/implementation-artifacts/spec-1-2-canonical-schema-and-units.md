---
title: 'Story 1.2: Canonical schema and units'
type: 'feature'
created: '2026-10-13'
status: 'done'
baseline_commit: '5e212e5a842695d6f077e086f11b8fc263e4b245'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/docs/architecture.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Nothing defines what the 12 geometry parameters are, which unit each uses, how a vendor value is converted, or how a bike is identified, so web and ingestion could disagree on what a value means.

**Approach:** Add three pure modules in `core`: `schema` (parameter registry plus a missing-value-safe parameter value), `units` (conversion to cm with a typed error) and bike-id/slug derivation, each driven by one failing test per scenario.

## Boundaries & Constraints

**Always:**
- Test-first: one failing test per scenario, written and seen red before the code; test through public functions, no mocking.
- `core` imports only the standard library and itself; no I/O.
- The full name is the parameter's meaning; the short code is only a compact key for tables and code. The mapping is explicit and lives only in `core/schema`: every `Parameter` carries both, and `parameter(code)` and `parameter_by_name(name)` resolve either way (unknown key raises). UI and docs show the full name; code and data keys use the short code.
- Parameters in canonical order `ST HT TT HTA STA CS FL FR BB S R E` (Seat Tube Length, Head Tube Length, Top Tube Length, Head Tube Angle, Seat Tube Angle, Chainstay Length, Fork Length, Fork Rake, Bottom Bracket Drop, Stack, Reach, Wheel Base). Core: `HTA` and `STA` in deg, `S`, `R`, `BB` in cm. The other seven are Optional, all cm.
- Conversion only in `core/units`; the bike-id slug comes from one function.

**Never:**
- No `RiderInput`, `CellState`, Usage Taxonomy or approved-file format (later stories); no evaluators or fit logic.
- No git commit or push; no edits to `docs/`, `epics.md` or `sprint-status.yaml`.
- No guessing: unknown units, unknown parameter codes and empty vendor or model names raise typed errors.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| List parameters | registry | 12 entries: 5 Core, 7 Optional, each with code, name, unit, tier | N/A |
| Code to name | `parameter("HTA")` | name `Head Tube Angle`, unit `deg` | unknown code raises |
| Name to code | `parameter_by_name("Bottom Bracket Drop")` | code `BB` | unknown name raises |
| Convert mm | `to_cm(1234, "mm")` | `123.4` | N/A |
| Convert inches | `to_cm(28, "in")` | `71.1` (71.12 rounded to 0.1) | N/A |
| Convert cm | `to_cm(57.46, "cm")` | `57.5` | N/A |
| Unknown unit | `to_cm(5, "furlong")` | none | raises `UnknownUnitError` naming the unit |
| Bike id, no year | `("KTM", "Strada Elite")` | `ktm:strada_elite` | N/A |
| Bike id, year | `("Van Rysel", "RCR Pro", 2025)` | `van_rysel:rcr_pro:2025` | N/A |
| Same input twice | identical args | identical id | N/A |
| Missing value | value `None` with reason | stored as `null` plus reason; never `0` | value `None` without reason raises |
| Partial geometry | only `S` and `R` given | all 12 codes present, absent ones `null` + reason "not reported" | unknown code raises |

</frozen-after-approval>

## Code Map

- `src/fit_my_ride/core/__init__.py` -- empty package; new modules go beside it.
- `tests/test_import_boundaries.py` -- already guards `core` imports; new modules must pass it unchanged.
- `tests/test_smoke.py` -- pattern for plain pytest style; add new tests as separate files.
- `docs/architecture.md` AD-3 -- source of parameter set, units, id format; Naming row: vendor slug lowercase with underscores.

## Tasks & Acceptance

**Execution:**
- [x] `tests/core/test_schema.py` + `src/fit_my_ride/core/schema.py` -- parameter registry (`Parameter`: code, name, unit, tier; `PARAMETERS`, `CORE_PARAMETERS`, `OPTIONAL_PARAMETERS`; `parameter(code)`, `parameter_by_name(name)`) -- red first
- [x] `tests/core/test_units.py` + `src/fit_my_ride/core/units.py` -- `to_cm(value, unit)` for `mm`, `cm`, `in`, rounding half-up to 0.1; `UnknownUnitError` -- red first
- [x] `tests/core/test_bike_id.py` + `src/fit_my_ride/core/schema.py` -- `slugify`, `bike_id(vendor, model, year=None)` -- red first
- [x] `tests/core/test_values.py` + `src/fit_my_ride/core/schema.py` -- `ParameterValue(value, reason)` and `complete_geometry(partial)` enforcing null-plus-reason -- red first
- [x] Run the gate and the boundary test; fix findings

**Acceptance Criteria:**
- Given `core/schema`, when I list parameters, then I get 5 Core and 7 Optional, each with unit and short code.
- Given a short code or a full name, when I look it up in `core/schema`, then I get the same parameter carrying both.
- Given a value in mm or inches, when I convert via `core/units`, then I get cm to 0.1 precision, and an unknown unit raises a typed error.
- Given a vendor and model name, when I derive the bike id, then it is `<vendor>:<model_slug>[:<model_year>]`, identical for identical input.
- Given a missing value, when it is recorded, then it is `null` plus a reason, never omitted and never zero.
- Given the gate, when run, then ruff and pytest (including the boundary test) pass.

## Implementation Notes

- Implemented directly (no subagent). Each module got its failing test first (collection error on the missing module), then the minimal code. Bike id, slug and value types live in `core/schema` as planned; `core/units` is separate.
- Gate green: ruff check, ruff format --check, 40 tests including the boundary test.
- Also set story `in-progress` in `sprint-status.yaml` per the build workflow.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Route | Evidence |
|---------|---------|-------|----------|
| Unknown code/name and empty names raise bare KeyError/ValueError, not typed (blind, edge, gap) | medium | patch | Spec says "typed errors"; only `UnknownUnitError` was typed. Added `UnknownParameterError(KeyError)` and `InvalidNameError(ValueError)`; compatible with existing catches. |
| `ParameterValue(54.2, "oops")` accepted (blind, edge, gap) | medium | patch | Verified: one-sided invariant. Now raises; vacuous `!= 0` assertion replaced. |
| `slugify` silently drops ß, ø, æ, ł, đ so "Øresund" becomes "resund" (blind, edge, gap) | medium | patch | Verified; ids are permanent catalog keys. Added small transliteration table before NFKD. |
| `ParameterValue(0.0)` violates "never zero" | false | rejected | Rule is that a *missing* value is never encoded as 0; `complete_geometry` fills `None`. A reported 0 is real data. |
| `to_cm` NaN/inf raises `InvalidOperation`; zero/negative; negative half-step rounding | low | rejected | Unlikely input; fix adds guards. Matrix silent. |
| Unit spellings `MM`, `inch`, `in.` rejected | false | rejected | Spec: no guessing; adapters declare source units as data. |
| `year` bool/negative unvalidated; non-str/None inputs; `complete_geometry` accepts raw floats, mutable dict | low | rejected | Unlikely misuse; fixes add guards. |
| "SL7"/"SL-7", "C-Dale"/"C Dale" collide | false | rejected | `sl7` and `sl_7` differ; the second pair is intended normalisation. |
| Name lookup case/whitespace sensitive | low | rejected | Exact canonical names are the contract. |
| Sprint-status edited despite Never line; status mismatch; Delivery line | false | rejected | Workflow step 3 requires the sync; fix would edit this spec. In-progress status in sprint file is correct until done. |
| `NOT_REPORTED` magic string, `-> None`, module placement, code `E` source | low | rejected | Cosmetic; no named harm. |

## Design Notes

Slug: NFKD-normalise and drop combining marks, lowercase, runs of non-alphanumerics become one `_`, strip `_`; empty result raises. Rounding uses `Decimal` with `ROUND_HALF_UP` on the decimal string of the input, so `57.45` gives `57.5`. Short codes `ST HT TT CS FL FR E` come from the UX Geometry Diagram; `schema` is one module for now and may split when `RiderInput` and friends land.

## Verification

**Commands:**
- `uv run pytest` -- expected: all tests pass
- `uv run ruff check . && uv run ruff format --check .` -- expected: no findings
