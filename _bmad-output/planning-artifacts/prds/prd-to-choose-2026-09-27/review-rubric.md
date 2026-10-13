# PRD Quality Review — Bike Selection Platform PRD (prd-to-choose-2026-09-27)

## Overall verdict

This PRD is unusually disciplined for its stakes: the thesis (fit-answer-only, nothing else) is stated once and never diluted, scope cuts are argued rather than asserted, and every FR carries testable consequences. The two real weaknesses are structural, not tonal: the Heatmap Table's actual v1 column set is never pinned down (Glossary gives examples, a success metric asserts an exact count), and the single open question left in §8 is more load-bearing than its footnote-sized treatment suggests — it governs whether most of FR-2/FR-3 can be built at all. Neither is a blocker at hobby scale, but both are worth a paragraph before this feeds architecture.

## Decision-readiness — adequate

Decisions are stated as decisions, not hedged as "considerations": §4.2's CLI-vs-UI trigger choice gives its reason inline ("no accounts/auth surface to gate a UI trigger behind"), and the addendum's "Options considered, not re-litigated here" section is exactly the pattern the rubric wants — a decision recorded once, not re-argued. Trade-offs name what was given up: FR-3's consequence ("No weighted or composite fit score is computed or displayed anywhere in v1") is stated plainly, and §6.2 admits In-Range Count is a stand-in because "no ideal-range-weighting formula exists yet." Open Questions in §8 are genuinely open (not rhetorical-with-an-answer-attached) and each has a stated reason for staying open. No dimension of this PRD reads as smoothed-to-neutral — no persona "values" language, no FR is vaguely "important."

### Findings
- **medium** Open Question 1's centrality is undersold (§8, item 1; FR-2). Only one Geometry Parameter pairing is named as having a settled "direct plug" evaluation (cycling inseam vs. standover). The other four examples the Glossary lists for Geometry Parameter (reach, stack, seat tube angle, top tube) have no stated evaluation method against Required Tier inputs — that's explicitly what's left open. As written, this reads as one bullet among two Open Questions; in substance it determines whether most of the Heatmap Table's columns (FR-2) and most of In-Range Count's inputs (FR-3) can be built at all. Leaving it open is fine (it's honestly flagged, with a reason — "decided when the Fit Engine is actually built"); the gap is that the PRD doesn't say what the Heatmap Table does with those columns in the interim (ship without them? render permanently "unknown"? block FR-2 entirely until resolved?). *Fix:* one sentence in §8 or FR-2 stating the fallback/interim behavior, or explicitly scoping FR-2's v1 columns down to only the parameters with a resolved evaluation method.

## Substance over theater — strong

Two personas (Rider, builder), both drive real decisions in both UJs — no persona padding. No NFR boilerplate section exists at all (appropriate here, not a gap — see Shape fit). The Vision statement (§1) is specific enough that it couldn't be swapped into another PRD unchanged: "It's a hobby project for two builders, not a business... The build itself is also the point." The differentiation claim (existing tools "stop short of answering... will this fit my body") reads as an earned observation from the builders' own experience, not a templated market-positioning paragraph. No findings.

## Strategic coherence — strong

The thesis — answer the fit question, and only that question — is stated in §1 and never contradicted downstream. Every feature (Fit Engine, Data Pipeline) traces to it; every Non-Goal (§5) and every MVP deferral (§6.2) is argued in terms of protecting that thesis rather than "not enough time." SM-1 ("actually use... to help decide on a real bike purchase") is about outcome quality, not activity volume — no DAU/MAU vanity-metric tell. SM-C1 is a genuine counter-metric naming the specific failure mode it guards against (breadth-creep before the core loop proves out), tied to SM-2. MVP scope kind (problem-solving) matches the scope logic used throughout. No findings.

## Done-ness clarity — adequate

Every FR (FR-1 through FR-7) carries a "Consequences (testable)" list with concrete, checkable statements — "Re-running ingestion against unchanged source PDFs produces no duplicate or altered records," "An official vendor source outranks scraped, community, or aggregator sources," etc. No instances of "handles gracefully" / "reasonable performance" / "user-friendly" hedge language were found. This is the PRD's strongest dimension mechanically. Two gaps keep it at "adequate" rather than "strong":

### Findings
- **medium** Geometry Parameter roster isn't enumerated as a fixed set (§3 Glossary; §7 SM-C1). The Glossary defines Geometry Parameter with "e.g." examples (reach, stack, seat tube angle, top tube, standover) — non-exhaustive by its own wording — but SM-C1 refers to "the 2-vendor / 5-parameter v1" as though the count were a settled fact. No feature section or FR states the authoritative v1 parameter list. An engineer implementing FR-2's Heatmap Table columns has no single place in the PRD to read off the definitive column set. *Fix:* either enumerate the v1 parameter set explicitly (e.g., a bullet list in §4.1), or drop the specific count from SM-C1 until it's decided (it can still name the failure mode — breadth-creep — without asserting "5").
- **low** FR-7's pre-commit review doesn't state whether FR-6's conflict-arbitration outcomes are visible in the review summary. The reviewed fields are listed as "field, value, unit, source, matched synonym" — if two sources conflicted and one was auto-selected per FR-6, the review as specified surfaces only the winning value, not that a conflict occurred. Given the builder JTBD is explicitly to "skip re-checking every field by hand" on trust in the pipeline, a silently-resolved conflict is a plausible trust gap in exactly the step meant to catch problems. *Fix:* add "flags when arbitration selected among conflicting sources" to FR-7's consequences, or note this is deliberately deferred.

## Scope honesty — strong

§5 Non-Goals and §6.2 Out of Scope for MVP are the strongest sections in the document. Every deferral in §6.2 is argued, not asserted, and the arguments differ per item in ways that show real thinking rather than a template: post-purchase feedback is "fully out of scope for v1, not just deferred" with a stated reason (no way to contact a rider without accounts); search-analytics logging, by contrast, is judged safe to build early precisely because it doesn't have that dependency. Open-item density (2 Open Questions in §8, both genuinely non-blocking and reasoned) is well calibrated to a hobby-scale, already-reviewed PRD — this is the rubric's "high count on a low-stakes PRD is fine" case working as intended, not a sign of unresolved work. No findings.

## Downstream usability — adequate

FR/UJ/SM numbering is contiguous and unique; every FR states which UJ it realizes, every SM states which FRs it validates, and all of these cross-references resolve correctly. Sections are largely self-contained. The addendum cleanly separates technical-how from the PRD's capability narrative (per its own stated purpose), which will help architecture consume the PRD without re-deriving what's already decided.

### Findings
- **low** Glossary drift between "tolerance" (FR-1's consequence: "falls outside the Rider's tolerance for that parameter") and "ideal range" (§3's definition of Heatmap Table: "relative to the Rider's ideal range"). These may be the same concept under two names (hard-exclusion boundary = edge of the continuous scale) or two different concepts (a narrower hard cutoff inside a wider graded range) — the PRD doesn't say which, and neither term has its own Glossary entry. This is exactly the kind of term a downstream architecture doc would need to implement consistently. *Fix:* add both as Glossary entries, or state explicitly whether tolerance is the ideal range's boundary.

## Shape fit — strong

This is a hobby/solo-shaped PRD (§1: "a hobby project for two builders, not a business... self-hosted") and it's formatted accordingly: two UJs with informal "you"-as-protagonist framing rather than named personas with backstories, no NFR section, no compliance scaffolding, Open Questions kept to the two that actually matter. Nothing here reads as over-formalized (no UJ-density padding) or under-formalized (the fit-comparison UX, the one part of this product with meaningful user experience, does get a UJ). The addendum's separation of process/technical-how from the PRD's capability narrative is itself a good shape decision for a PRD that feeds architecture next. No findings.

## Mechanical notes

- **No bracket-tag convention used.** The PRD contains no `[ASSUMPTION: …]`, `[NOTE FOR PM]`, or `[NON-GOAL for MVP]` tags anywhere; the same functions (flagging inferences, deferred decisions, explicit non-goals) are carried in plain prose instead (§6.2's argued bullets, the addendum's "Options considered, not re-litigated here"). This works substantively — nothing reads as a hidden, unflagged inference — but there is no Assumptions Index to roundtrip-check, and a reader scanning for the standard tags would find none. Given this PRD already went through a resolved review conversation, this is a format choice rather than a gap.
- **Capitalization drift, cosmetic only.** "Required Tier" is capitalized as a proper Glossary term (§3) but FR-1's heading reads "Required-tier fit filtering" (lowercase, hyphenated). No ambiguity results.
- **ID continuity is clean.** FR-1–FR-7, UJ-1–UJ-2, SM-1/SM-2/SM-C1 are contiguous, unique, and every cross-reference ("Realizes UJ-1," "Validates FR-4, FR-5, FR-6, FR-7") resolves to a real target. No gaps, no duplicates.
- **Working title left unconfirmed.** The title line carries "*Working title — confirm.*" but this is never resurfaced in §8 Open Questions. Trivial, but it is technically an untracked open item.
