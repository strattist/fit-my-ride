---
title: 'Story 1.4: Stack and Reach evaluators'
type: 'feature'
created: '2026-10-15'
status: 'done'
baseline_commit: '82cadbdcf7172a49bba9f5ebae3598a67cf668a3'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/docs/fit-rules.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Stack and Reach are Core Parameters with no fit rule, so they always render `unknown` and the two most telling cells carry no answer.

**Approach:** Implement exactly the rule approved in `docs/fit-rules.md` as `core/fit` evaluators for S and R: centre = BikeSize height formula + per-style offset, range = centre ± 1.5 cm, deviation = signed distance to the nearest edge (0 inside). Inseam is not used. Registered into an `EvaluatorRegistry` through one function; tests use values from the document.

</frozen-after-approval>

## Implementation Notes

- Test-first, one scenario at a time.
- Module `core/fit_rules.py` cites `docs/fit-rules.md`.
- Added `core/fit_rules.py` (`stack_deviation`, `reach_deviation`, `register_stack_reach`) and `tests/core/test_fit_rules.py` (in-range, both edges, each side outside, every style, height, inseam ignored, other parameters stay `unknown`).
- The doc's worked example had rounded the reach range (38.1, 36.6-39.6); the formula gives 38.125, 36.625-39.625. Doc example corrected to exact values; the rule itself is unchanged.
- Deviations and edges are rounded to 6 decimals so float noise never turns an on-edge value into a deviation.
- Gate green: ruff check, ruff format --check, pytest (100 passed). Not committed, per the user's standing rule.
- Review: no subagents spawned (not requested); inline self-review only, no findings.
- Review fixes (bmad-review): non-finite bike values now return `UNKNOWN` (NaN used to score as in-range); `-0.0` normalised to `0.0`; tests now pin that every `Style` has an offset row and a test row, and that inseam is ignored by both S and R. Gate green (109 passed). Uncommitted.
