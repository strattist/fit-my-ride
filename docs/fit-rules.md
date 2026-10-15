# Fit rules

**Status: APPROVED.** Story 1.4 evaluators implement exactly this document.

Approved by: Baptiste · Approved on: 2026-10-15

## How to read this

Each rule turns a rider (`height_cm`, `inseam_cm`, `style`) into an **ideal range** for one
Core Parameter. The evaluator returns the signed distance from the value to that range, in
cm: 0 inside the range, negative below it (too short/low), positive above it (too long/high).

Only Stack (S) and Reach (R) are defined here. HTA, STA and BB are decided in Story 1.5.

## Provenance of the numbers

No authoritative public formula maps height and inseam to stack and reach; bike-fit guidance
treats stack and reach as a starting point refined by a fitter. The only published formula
found is BikeSize's height-only method
([methodology](https://bike-size.com/about/methodology/bike-sizing)):

- stack = height x 3.1 + 20 mm
- reach = height x 2.15 + 5 mm

The style offsets and the tolerance below have no external source; they were proposed and
accepted by Baptiste as v1 values.

## Rule

All values in cm. `h` = height_cm, `i` = inseam_cm.

### Centre of the range

| Parameter | Centre (before style) | Source |
|-----------|-----------------------|--------|
| Stack S   | `0.31 * h + 2.0` | BikeSize |
| Reach R   | `0.215 * h + 0.5` | BikeSize |

Inseam is **not used** in v1: no sourced formula links it to stack or reach. See
"Future idea: inseam term" below.

### Style offsets

Added to the centre. Style values are the Usage Taxonomy wire values.

| Style           | Stack offset | Reach offset |
|-----------------|--------------|--------------|
| `road`          | 0.0          | 0.0          |
| `gravel`        | +1.0         | -0.5         |
| `mtb`           | +0.5         | +1.5         |
| `city_commute`  | +3.0         | -2.0         |
| `touring`       | +2.0         | -1.0         |
| `e_bike`        | +3.0         | -2.0         |

### Range

Ideal range = centre ± tolerance, with tolerance **1.5 cm** for both S and R. It is a fixed
v1 constant; it may later become a rider-facing input to help select bikes (a new story in
Epic 4, not part of Epic 1).

Deviation for a bike value `v` with range `[lo, hi]`:

- `v < lo` → `v - lo` (negative)
- `lo <= v <= hi` → `0`
- `v > hi` → `v - hi` (positive)

## Worked example (road, h = 175)

- Stack centre = 0.31·175 + 2.0 = 56.25 → range 54.75–57.75
- Reach centre = 0.215·175 + 0.5 = 38.125 → range 36.625–39.625
- Stack 54.0 → deviation −0.75; stack 56.0 → 0; stack 59.0 → +1.25
- Reach 40.0 → +0.375; reach 38.0 → 0; reach 36.0 → −0.625

## Future idea: inseam term

Not part of the approved rule; recorded for later updates. The intuition (unsourced, from the
drafting agent, not verified): riders with long legs for their height tend to fit a taller
stack, and short-legged riders a lower one. A candidate form was

    stack_centre += k * (inseam - r * height)

with r ~ 0.45 (a rough typical cycling-inseam-to-height ratio, ~79 cm at 175 cm) and
k ~ 0.25 cm of stack per cm of inseam difference. Both numbers were guesses. Adopt it only
with a real source or a fitter's data, then update this document before any code.

## Decisions (Baptiste)

1. Base formula: BikeSize height formula accepted.
2. Inseam: dropped from the v1 rule (see above).
3. Style offsets: accepted as proposed.
4. Tolerance ±1.5 cm accepted; may become a rider input later.
