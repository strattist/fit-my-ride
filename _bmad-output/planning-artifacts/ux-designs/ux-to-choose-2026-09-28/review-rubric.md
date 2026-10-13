# Spine Pair Review — Fit my Ride

## Overall verdict

This is a well-executed fast-path spine pair: canonical section shapes are followed exactly, every color/typography/spacing token resolves, both PRD journeys have full Key Flows with climax and failure paths, and the heavy colorblind/unknown-data requirements are threaded consistently through both files. The gaps that matter are narrow and concrete rather than structural: two frequently-used interactive elements (the cell detail popover/bottom sheet, and the show-excluded toggle) have real behavioral specs in EXPERIENCE.md but no matching visual spec in DESIGN.md, one internal cross-reference ("see Column states") points at a section that doesn't exist, and the one worked visual mock in `.working/` is never linked from either spine. None of this blocks a downstream consumer entirely — the surrounding text carries enough information to infer most of it — but the popover and toggle gaps would force a builder to invent appearance without spine guidance.

## 1. Flow coverage — strong

Checked: PRD §2.3 UJ-1 and UJ-2 against EXPERIENCE.md § Key Flows, for named protagonist, numbered steps, a climax beat, and a failure path.

- UJ-1 ("check whether your shortlisted bike fits") → Flow 1 (Camille, desktop) and Flow 2 (Camille, phone/imperial). Both have a named protagonist, numbered steps, a bolded **Climax**, and a `Failure:` line.
- UJ-2 ("add a new vendor's catalog") → Flow 3 (Baptiste, CLI review). Same shape: protagonist, steps, climax, failure.
- All 7 FRs are traceable into at least one flow, state row, or the Builder Review section.

### Findings

None.

## 2. Token completeness — strong

Checked: every frontmatter token in DESIGN.md's `colors`, `typography`, `rounded`, `spacing`, `components`, and every `{path.to.token}` reference in both files' prose, against `design-md-spec.md`'s type rules.

- All 23 color tokens have hex values; heat-tier pairs each carry a `-text` companion for on-fill contrast.
- Contrast targets are stated for the load-bearing combination (heat scale: "at least 4.5:1... ΔE ≥ 27" under protan/deutan/tritan simulation) — not eyeballed.
- Every `{colors.*}`, `{typography.*}`, `{rounded.*}`, `{spacing.*}` reference found in DESIGN.md and EXPERIENCE.md (`{colors.error}`, `{colors.focus-ring}`, `{spacing.tap-target}`, `{colors.background}`, etc.) resolves to a defined frontmatter token.
- No dark/light pairs needed beyond the documented `diagram-card` exception, since the product is dark-only by design (not a light/dark togglable theme).

### Findings

None. (See Mechanical notes for a non-blocking observation about the `fontFeature` key.)

## 3. Component coverage — thin

Checked: every component name used anywhere in either file, cross-matched between DESIGN.md § Components (visual spec) and EXPERIENCE.md § Component Patterns (behavioral spec).

### Findings

- **high** The cell detail popover (desktop) and its phone equivalent, the bottom sheet, have real, repeatedly-cited behavioral specs — EXPERIENCE.md § Component Patterns ("Heat cell... Tap or hover shows a detail popover: value, rider's range, distance from range, tier name"), § State Patterns ("Unknown cell"'s popover copy), § Interaction Primitives, § Responsive & Platform ("Cell tap opens a bottom sheet for the popover"), and Key Flow 2's climax — but DESIGN.md § Components has no matching entry: no background, border, radius, typography, or elevation is specified for either form factor. It is the second most-used interactive surface in the product after the table itself. *Fix:* add a `popover` (and phone `bottom-sheet`) component to DESIGN.md's frontmatter `components` and a matching § Components bullet.
- **high** The show-excluded toggle has a real behavioral rule in EXPERIENCE.md § Component Patterns ("Off by default... On, excluded bikes appear at the bottom, visibly marked") and appears as a switch control in `.working/key-results-desktop.html`, but has no DESIGN.md § Components entry or frontmatter token — unlike its sibling `unit-toggle`, which has both. *Fix:* add a `show-excluded-toggle` component token/bullet to DESIGN.md.
- **medium** "In-Range Count cell" has a full visual spec in DESIGN.md § Components but no matching row in EXPERIENCE.md § Component Patterns; its behavior (used as a sort key, recomputed as `n / evaluated` when columns are unevaluated) is scattered across § Information Architecture, § Sorting, and § State Patterns instead. *Fix:* add a Component Patterns row, or note in DESIGN.md that its behavior lives elsewhere.
- **medium** "Bike cell" has a full visual spec in DESIGN.md § Components ("It is pinned on scroll") but no matching row in EXPERIENCE.md § Component Patterns; its pinning behavior is stated instead in DESIGN.md's own § Layout & Spacing and in EXPERIENCE.md § Responsive & Platform. *Fix:* same as above.
- **low** "Unknown cell" has a DESIGN.md § Components visual entry, but its behavioral rules live only in EXPERIENCE.md § State Patterns ("Unknown cell", "Not-evaluated column" rows) rather than § Component Patterns — the content exists, just filed under a different heading than its DESIGN.md counterpart's name suggests. *Fix:* cross-reference the state rows from the Component Patterns table, or vice versa.

## 4. State coverage — adequate

Checked: every IA surface (Fit/Form, Fit/Results, Builder review) walked against EXPERIENCE.md § State Patterns for empty, cold-load, focus, error, offline, and permission-denied states, where applicable.

- Form: first run, returning (remembered values), validating/error, offline — all covered.
- Results: computing/cold-load, loaded, no-fitting-bikes/empty, unknown cell, not-evaluated column, all-columns-unevaluated, offline, load failure, long catalog — all covered.
- Permission-denied correctly omitted (no accounts/auth in v1).
- Builder Review (CLI) states (counts header, conflict flags, unrecognized flags, approve/abort, idempotent re-run) are specified in prose in § Builder Review (CLI) rather than the State Patterns table — a reasonable choice given it's a distinct, non-tabular surface, not a gap.

### Findings

- **high** EXPERIENCE.md § Information Architecture says "All 12 always appear, colored or not (see Column states)" — no section or subsection titled "Column states" exists anywhere in the document. The nearest actual content is § State Patterns' "Not-evaluated column" and "Unknown cell" rows. *Fix:* either add a "Column states" anchor/subheading under § State Patterns, or change the pointer to name the actual rows.
- **low** No explicit "Focus" row in § State Patterns for form fields, table headers, or heat cells, unlike the example spines' dedicated Focus row. Focus behavior is described only generically in § Accessibility Floor ("The focus ring uses `{colors.focus-ring}` and stays visible against every fill") and in DESIGN.md's Heat cell bullet. *Fix:* optional — add a one-line Focus row if per-element focus treatment ever needs to diverge.

## 5. Visual reference coverage — adequate

Checked: every file in `mockups/`, `wireframes/`, `imports/` (no `mockups/`/`wireframes/` directories exist), plus `.working/key-results-desktop.html` and its preview PNG as directed, against inline links in both spines.

- `imports/BikeGeometry.svg` — linked inline in DESIGN.md § Components (Geometry Diagram bullet) and EXPERIENCE.md § Component Patterns and § Inspiration & Anti-patterns, each naming what it illustrates. Good.
- `imports/rcr-geometry-source.png` — linked inline in EXPERIENCE.md § Inspiration & Anti-patterns, correctly scoped as an inspiration/naming source rather than shipped art.
- Spines-win-on-conflict is stated once, in EXPERIENCE.md's frontmatter blockquote. Good.
- `.working/key-results-desktop.html` (and `-preview.png`) is a fully worked Results-page composition — on inspection it matches the spines closely (summary bar, count line, legend, table, five illustrative bikes, unknown/not-evaluated states, cell popover, Geometry Diagram) — but is never referenced inline from either spine. Neither example spine's `→ Composition reference:` pattern appears anywhere in EXPERIENCE.md § Information Architecture.

### Findings

- **medium** `.working/key-results-desktop.html` exists, is current (matches the final token/component decisions per `.memlog.md`'s last entries), and would materially help a downstream consumer — but nothing in either spine points to it, and `.memlog.md` notes it is "not yet promoted to `mockups/`." A reader of the spines alone has no way to discover it. *Fix:* promote to `mockups/` and add a `→ Composition reference:` line to § Information Architecture, or note the pending promotion explicitly in § Open Items.

## 6. Bloat & overspecification — strong

Checked: pixel specs duplicating tokens, source restatement, prose-where-a-table-works, unread-by-downstream-consumer sections, decorative narrative untied to a decision, and editorial voice bleeding into EXPERIENCE.md.

- DESIGN.md carries editorial voice appropriately ("should feel like a sport-science instrument"), consistent with the spec allowing this.
- EXPERIENCE.md stays functional throughout, including Key Flow climaxes — each ties directly to a decision or FR (e.g. Flow 3's climax is FR-7's pre-commit review catching a bad synonym match, not decorative color).
- The one-line scope-boundary restatement in § Foundation ("No dealer or map layer, no accounts...") cites PRD section numbers rather than reproducing FR text, and is load-bearing for IA/flow scoping rather than filler.
- No pixel values found duplicating a token; all sizing in prose refers to `{spacing.*}`/`{rounded.*}` tokens.

### Findings

None.

## 7. Inheritance discipline — adequate

Checked: `sources` frontmatter resolution, UJ/FR/glossary term fidelity to `docs/prd.md`, `docs/product-brief.md`, and the addendum, component-name identity across both files, and token-reference resolution.

- All three `sources` paths resolve to real files with consistent content.
- FR-1 through FR-7 are cited verbatim and correctly throughout EXPERIENCE.md.
- Glossary terms (Rider, Required Tier, Geometry Parameter, Canonical Schema, Synonym Map, Usage Taxonomy, Heatmap Table, In-Range Count) are used consistently and capitalized correctly in both files.
- `{path.to.token}` references in EXPERIENCE.md all resolve to DESIGN.md tokens by name (checked in category 2).

### Findings

- **low** EXPERIENCE.md's Key Flows never cite "UJ-1" / "UJ-2" by name (Flow 1/2 realize UJ-1, Flow 3 realizes UJ-2, but only by inference), unlike the FR-# citations used pervasively elsewhere in the same file. *Fix:* add "(realizes UJ-1)" / "(realizes UJ-2)" annotations to the flow headers, mirroring the PRD's own "Realizes UJ-1" phrasing.
- **low** DESIGN.md § Layout & Spacing refers to "the bike column" (lowercase), while EXPERIENCE.md's IA table and DESIGN.md's own § Components section ("Bike cell") treat it as a proper name. *Fix:* capitalize for consistency.
- **low** The PRD glossary term "Ingestion Pipeline" is never used verbatim in EXPERIENCE.md (only "ingestion command," "the parser," "Builder Review"). Minor terminology drift from the source glossary. *Fix:* use "Ingestion Pipeline" at least once in § Foundation or § Builder Review (CLI) for traceability.

## 8. Shape fit — strong

Checked: DESIGN.md section order against the canonical Brand & Style → Colors → Typography → Layout & Spacing → Elevation & Depth → Shapes → Components → Do's and Don'ts sequence; EXPERIENCE.md required defaults, required-when-applicable sections, and invented sections earning their place.

- DESIGN.md has all 8 canonical sections, in exact canonical order, none omitted.
- EXPERIENCE.md has all required defaults: Foundation, IA, Voice and Tone, Component Patterns, State Patterns, Interaction Primitives, Accessibility Floor, Key Flows.
- Required-when-applicable sections both trigger and both appear: Inspiration & Anti-patterns (memlog shows extensive reference-product and rejection history — Aura, 99spokes, streaks/traffic-light rejections) and Responsive & Platform (multi-surface: desktop + phone).
- Invented sections both earn their place: "Builder Review (CLI)" documents UJ-2's genuinely distinct CLI surface; "Open Items" is expected per this review's framing and tracks real, previously-flagged open questions rather than hiding gaps.

### Findings

None.

## Mechanical notes

- **Broken cross-reference (high, see § 4 State coverage):** EXPERIENCE.md § Information Architecture says "(see Column states)" — no section by that name exists anywhere in either file.
- **Frontmatter completeness:** both files' frontmatter is complete against the spec (DESIGN.md: name, description, colors, typography, rounded, spacing, components; EXPERIENCE.md: name, status, sources, updated) and all `sources` paths resolve.
- **Non-blocking spec deviation:** DESIGN.md's `numeric`/`numeric-lg` typography tokens include a `fontFeature: 'tnum'` key not among `design-md-spec.md`'s documented subset (`fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`). It's a reasonable, resolvable extension (maps to CSS `font-feature-settings` for tabular figures) — flagged for awareness, not a finding.
- **Filesystem hygiene:** `imports/BikeGeometry.svg:Zone.Identifier` is a stray Windows download-metadata sidecar file, not a content reference — harmless but worth cleaning up.
- No Mermaid diagrams are used in either file (N/A).
- No `mockups/` or `wireframes/` directories exist; not required (omittable), and not a finding on their own.
