---
title: 'Story 1.3: Rider input and the evaluator seam'
type: 'feature'
created: '2026-10-15'
status: 'done'
baseline_commit: 'bcef16e90c7dac18196175efe5a2d81cd011ef5f'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/docs/architecture.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** There is no validated rider input and no place to plug in per-parameter fit rules, so a Core Parameter nobody has defined a rule for could get a guessed colour.

**Approach:** Add `RiderInput` (height 120-230 cm, inseam 50-120 cm, style from the Usage Taxonomy) to `core/schema`, and a `core/fit` evaluator registry with one slot per Core Parameter that returns `unknown` when empty and a signed deviation (0 in range, negative too short, positive too long) when an evaluator is registered. No real fit rules yet (stories 1.4, 1.5); tests register stand-in evaluators.

</frozen-after-approval>

## Implementation Notes

- Test-first, one scenario at a time (red seen before each piece of code).
- `core/schema`: added `Style` (Usage Taxonomy), `RiderInput`, `InvalidRiderInputError`. `core/fit`: `UNKNOWN`, `Evaluator`, `EvaluatorRegistry` (per-instance, no global state; `register` replaces a slot). Only Core Parameters can be registered or evaluated; Optional ones raise.
- Style accepts a `Style` or its string value; anything else raises `InvalidRiderInputError`.
- Gate green: ruff check, ruff format --check, 66 tests including the boundary test.
- Not committed, per the user's standing rule; sprint status set to `review`.
- Review: no subagents spawned (not requested); inline self-review only. Rejected as low: bool/str inputs for heights (`True` passes the range), no `NaN` handling needed (NaN fails the range check and raises).

## Review Triage Log

| Finding | Verdict | Route | Evidence |
|---------|---------|-------|----------|
| `RiderInput(True, ...)` or numeric strings | low | rejected | Unlikely misuse; web boundary parses input. |
