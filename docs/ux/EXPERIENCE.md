---
name: Fit my Ride
status: final
sources:
  - docs/prd.md
  - docs/product-brief.md
  - _bmad-output/planning-artifacts/prds/prd-to-choose-2026-09-27/addendum.md
updated: 2026-10-11
---

# Fit my Ride — Experience Spine

> Pairs with `DESIGN.md`, which owns how it looks. Tokens are referenced as `{path.to.token}`. If a mock or wireframe ever disagrees with either spine, the spine wins. Items tagged `[ASSUMPTION]` were not stated by Baptiste and are open to correction.

## Foundation

Self-hosted, installable PWA (up to 5 users, no accounts, no login) that works in a desktop or phone browser. Desktop is primary for reading the table; phone is a secondary device, with the table adapted for the smaller screen (see Responsive & Platform). The stack is decided in the architecture spine (server-rendered Python app); both UX spines stay framework-agnostic — visual tokens are defined once, in `DESIGN.md`, rather than borrowed from a framework's own design system. The database is metric (lengths in cm, angles in degrees). The interface is metric by default and converts on demand.

Rider-facing scope is one job: enter measurements, read the Heatmap Table. Ingestion is a CLI, so its only UX is the review summary (see Builder Review). No dealer or map layer, no accounts, no saved profiles, no free-text prompt, no height-only mode, no fit score, and no spec browsing (PRD §5, §6.2).

## Information Architecture

One rider surface with two states, plus a CLI review for builders.

| Surface | State | Reached from | Purpose |
|---|---|---|---|
| Fit | **Form** | App open (first run, or after reset) | Enter height, cycling inseam, riding style |
| Fit | **Results** | Submit on the form | Summary bar + legend + Heatmap Table |
| Builder review | CLI output | Ingestion command | Approve or abort what the parser extracted (FR-7) |

→ Composition reference: `mockups/key-fit-form.html` (Form state, first-run + validating), `mockups/key-results-desktop.html` (Results state, desktop). Spine wins on conflict.

Results is the same page as the form: on submit, the form collapses into the summary bar above the table, and Edit reopens it. There is no separate settings page, and the unit toggle lives in the form. `[ASSUMPTION]` App open with remembered values goes straight to Results, with the summary bar showing the remembered entry.

Results layout, top to bottom: summary bar → count line and Show-excluded toggle → legend → **Geometry Diagram** → table.

Table columns, left to right: **Bike** (vendor + model, pinned) · **Size** (info only) · **In-Range Count** · the 5 Core Parameters in the Canonical Schema order, each headed by its short code with the full name underneath: HTA (Head Tube Angle), STA (Seat Tube Angle), BB (Bottom Bracket Drop), S (Stack), R (Reach). All 5 always appear, colored or not (see State Patterns → "Unknown cell", "Not-evaluated column" below). The seven Optional Parameters are stored but not shown in v1.

Row rule: one row per model per vendor, so a vendor with many models has many rows. Size never filters, sorts, or categorizes rows. A bike that suits the rider is never dropped because of its size.

Per-size geometry is decided in the architecture spine (AD-5): geometry is stored per model and per size, and the fit engine picks the best-fitting size for the rider (fewest out-of-range parameters, then smallest total deviation, then vendor size order). A row's cells show that size's values, and the Size cell names it.

## Voice and Tone

Sporty and technical: short, numeric, direct. Microcopy states facts and units. It has no exclamation marks, no emoji, and no coaching language. Brand feel lives in `DESIGN.md`.

| Do | Don't |
|---|---|
| "Reach 39.4 cm · slightly long" | "This bike's reach is a bit long for you!" |
| "31 of 47 bikes fit" | "Great news, we found 31 matches 🎉" |
| "Not evaluated" | "We're working on this parameter" |
| "Unknown — no data for this bike" | "N/A" or a blank cell |
| "Offline. Reconnect to compute fit." | "Oops! Something went wrong" |
| "Enter a height between 120 and 230 cm." | "Invalid input" |

## Component Patterns

Behavioral. Visual specs live in `DESIGN.md.Components`.

| Component | Use | Behavioral rules |
|---|---|---|
| Rider form | Form state | Three fields: height, cycling inseam, riding style. All required. Submit is disabled until valid, and each field says what is missing. |
| Unit toggle | Form | Two segments, `cm` and `ft·in`. Switching converts any entered values immediately and keeps them. Height in `ft·in` is two fields (feet, inches). Inseam in `ft·in` is inches with one decimal. The database always receives centimeters. |
| Riding style select | Form | Options are loaded from the database (the Usage Taxonomy), never hard-coded in the UI. Single choice. If the list can't load, Submit is disabled and the error names the reason. |
| Summary bar | Results | Shows the submitted values in the active unit. Edit reopens the form with values retained. The unit toggle is available there too. |
| Legend | Results | Five swatches with glyph and label, plus "unknown". Always visible above the table. On phone it collapses to a tap-to-open strip. |
| Geometry Diagram | Results | One generic labeled bike schematic, always visible above the table (collapses to a tap-to-open strip on phone), showing all 12 Geometry Parameters as dimension lines with their short codes (the table shows only the 5 Core Parameters) — same diagram for every bike and every Usage Taxonomy type. Sourcing: see Inspiration & Anti-patterns. Accessible text alternative: see Accessibility Floor. **Static in v1 — no interaction with the table**; see Open Items. Visual spec: `DESIGN.md.Components` → Geometry Diagram. |
| Column header | Table | Tap or click to sort. A second line shows the rider's range for the column. Visual spec (active-state color): `DESIGN.md.Components` → Column header. |
| Heat cell | Table | Shows glyph and value at 0.1 precision (degrees for angle columns, centimeters otherwise). Tap or hover shows a detail popover (visual spec: `DESIGN.md.Components` → Popover / bottom sheet): value, rider's range, distance from range, tier name. Keyboard focus shows the same popover, via the two-tone focus halo (see Accessibility Floor). |
| Unknown / not-evaluated cell | Table | A state of the Heat cell, not a separate component — full behavior is under State Patterns ("Unknown cell", "Not-evaluated column") below; visual spec: `DESIGN.md.Components` → Unknown cell. |
| In-Range Count cell | Results, Table | The default sort key. Shows `n / 5`, or `n / evaluated` when some columns are unevaluated (see State Patterns → "All columns unevaluated"). Visual spec: `DESIGN.md.Components` → In-Range Count cell. |
| Bike cell | Table | Pinned on scroll (see Responsive & Platform below); no interaction beyond that. Visual spec: `DESIGN.md.Components` → Bike cell. |
| Size cell | Table | Plain text, no interaction. |
| Show-excluded toggle | Results | Off by default. Bikes hidden by hard exclusion (FR-1) are counted in the count line (for example "31 of 47 fit · 16 excluded"). When switched on, excluded bikes appear at the bottom, each carrying an explicit text badge ("Excluded — outside your range") — never a dimming/opacity treatment alone (accessibility review: color/opacity-only marking would be a color-only-meaning gap). Visual spec: `DESIGN.md.Components` → Show-excluded toggle, Excluded row badge. |

### Sorting

- Sort by any single column, or by In-Range Count. There is no weighted score anywhere (FR-3).
- **Default:** In-Range Count, most first.
- **Parameter column:** orders by distance from the rider's ideal range, closest first, so borderline bikes are visible. A second tap reverses the order. A third returns to the default. `[ASSUMPTION]`
- **Unknown cells always sort last**, in either direction.
- Ties keep a stable order (vendor, then model).
- Sort does not change which bikes are shown.

### Reading a cell

The cell shows the number, at 0.1 precision, with its tier glyph. The color is a second channel. The five tiers are: too short, slightly short, ideal range, slightly long, too long. For the two angle parameters, the accessible label reads "below range / above range," not "short / long." `[ASSUMPTION]`

### Reading the diagram

The Geometry Diagram is a static reference, not a filter or a control — it doesn't change the table and isn't interactive in v1. It answers "what does TT actually measure on the bike," the same question the vendor's own PDF answers with its own drawing — this one is generic and canonical instead of per-vendor. Its accessible text alternative is specified in Accessibility Floor.

## State Patterns

| State | Surface | Treatment |
|---|---|---|
| First run | Form | Empty fields, metric selected. One line above the form: "Three measurements. Then the table." |
| Returning | Fit | Remembered unit and values restored, and Results is shown directly (see IA). |
| Validating | Form | Inline errors per field, `{colors.error}` plus text, never color alone. Range hint: height 120–230 cm, inseam 50–120 cm. `[ASSUMPTION]` |
| Computing | Results | The table's skeleton (same column count) appears at once, then fills. The summary bar is shown immediately. |
| Loaded | Results | Count line, legend and table. |
| No fitting bikes | Results | "No bikes fit these measurements." Count of excluded bikes. Show-excluded toggle. Edit measurements action. |
| Unknown cell | Table | Dashed outline and `—`. The popover says "No data for this bike" and does not guess a value. |
| Not-evaluated column | Table | All cells unknown, the header's range line reads "not evaluated", and the popover says "No evaluation method for this parameter yet." Same look as unknown, different reason. |
| All columns unevaluated | Results | The table still renders. The In-Range Count is computed only over evaluated parameters and its cell shows `n / evaluated` (for example `3 / 4`); with none evaluated, it shows `—`. `[ASSUMPTION]` |
| Offline | App | The app shell and last remembered entry load. Computing needs the server: "Offline. Reconnect to compute fit." Never show stale results as current. |
| Load failure | Results | `{colors.error}` message with a retry action. |
| Long catalog | Table | Rows scroll inside the page with the header pinned. The count line shows the total. `[ASSUMPTION]` |
| Focus | Table, Form | Heat cells use the two-tone halo; everywhere else, a single ring (see Accessibility Floor for why). Focus always moves in reading order and, on a cell, opens the same popover as tap/hover. |

## Interaction Primitives

- **Keyboard (desktop):** Tab reaches the form, unit toggle, Show-excluded toggle, legend, and every sortable header. Enter or Space on a header sorts. Arrow keys move between cells. Enter on a cell opens its popover, and Esc closes it.
- **Touch (phone):** tap a header to sort, tap a cell for its popover. Minimum target `{spacing.tap-target}`. The table scrolls horizontally with the Bike column and header rows pinned. Landscape works best, and the legend hints at it once.
- **Hover:** desktop shows the cell popover on hover as an addition to click. Hover is never the only way to reach information.
- **Persistence:** unit choice and last-entered values are saved on this device only (local storage) and restored on next open. `[ASSUMPTION]` Values are never sent anywhere except to compute the fit. A "clear" action in the form resets them.
- **Banned:** infinite scroll that hides the total, hover-only affordances, drag-to-reorder columns, modal stacks.

## Accessibility Floor

Behavioral. Visual contrast and the heat palette live in `DESIGN.md`.

- **Colorblind:** fit meaning is never carried by color alone — the number, the tier glyph, and the popover text carry it too. The palette was checked under protanopia, deuteranopia, and tritanopia simulation, not just asserted; method and computed values are in `.working/heat-scale-cvd-check.md` and `DESIGN.md` § Colors.
- WCAG 2.2 AA target across the Fit surface.
- The table implements the ARIA `grid` pattern (roving `tabindex`, explicit `row`/`gridcell` roles) on top of real row/column headers. This is named explicitly because a plain HTML `<table>` doesn't support the arrow-key cell navigation in Interaction Primitives on its own — the grid pattern is what reconciles native table semantics with that keyboard behavior for screen-reader users. The sort state is announced (`aria-sort`).
- Each cell's accessible name includes the distance from range shown in the visual popover, for example "Reach, 39.4 centimeters, slightly long, 0.4 centimeters above your range of 38.5 to 40.0." Unknown/not-evaluated cells get their own pattern, for example "Reach, unknown, no data for this bike" / "Fork Length, not evaluated, no evaluation method for this parameter yet" (reusing the popover copy in State Patterns). Neither is announced as an empty cell.
- Focus order follows reading order. Heat cells use a two-tone halo (`focus-halo-inner` + `focus-halo-outer`), verified against all 5 heat fills; a single `{colors.focus-ring}` ring — sufficient everywhere else — fails WCAG 1.4.11's 3:1 minimum against most heat-tier colors (accessibility review finding; see `DESIGN.md` § Components → Heat cell).
- **Geometry Diagram text alternative** (explicit decision, not an oversight — accessibility review finding): `role="img"` with a summary `aria-label` naming it as a reference schematic and listing the 12 codes, for example "Reference diagram of a bicycle frame showing 12 geometry measurements, five of which appear in this table: HTA, STA, BB, S, R. The others are ST, HT, TT, CS, FL, FR, E." The diagram's real job — which line on the frame is which parameter, a spatial answer — has no text equivalent; the column headers' full names (already text, already present) are treated as a sufficient substitute for a rider who needs the mapping without the picture. If that turns out not to be enough in practice, revisit with a structured description (a definition list, one line per code) rather than leaving the image unlabeled.
- Form fields have visible labels, errors tied to fields, and numeric keypads on phones.
- Respects reduced motion. The interface animates only state changes.

## Responsive & Platform

| Width | Behavior |
|---|---|
| ≥ 1200px | Whole table visible without horizontal scroll (Size, In-Range Count and 5 Core Parameter columns, plus the pinned Bike column — 8 columns total). Form and summary bar left-aligned above it. |
| 768–1199px | Table scrolls horizontally. Bike column and header rows pinned. |
| < 768px (phone) | Form is one column. Table scrolls horizontally with a narrower pinned Bike column (vendor and model on two lines). Cell tap opens a bottom sheet for the popover. Legend collapses to a strip. Geometry Diagram also collapses to a tap-to-open strip beside the legend, since it can't stay always-visible next to a horizontally-scrolling table — it's a static image there too, same as desktop. `[ASSUMPTION]` |

Installable as a PWA on desktop and phone. `[ASSUMPTION]` The manifest sets a dark theme color from `{colors.background}` and a standalone display mode.

## Builder Review (CLI)

The pre-commit review (FR-7) is a terminal summary of what the Ingestion Pipeline (FR-4) extracted, not a screen. This section only specifies what it shows and how it reads. Decided in the architecture spine (AD-7): the approve or abort gate is in the terminal, and a report file with the same content is written alongside it for long catalogs.

- One row per extracted field: **field**, **value**, **unit**, **source**, **matched synonym**.
- **Conflict rows are flagged** when arbitration (FR-6) chose between sources, naming the losing source and value, not only the winner.
- **Unrecognized field names are flagged** and listed separately (FR-5). They are never dropped or guessed.
- **Blocked bikes are flagged** `MISSING CORE` with the missing parameter and size, and are not committed (FR-7); other bikes in the batch can still be approved.
- A header line gives counts: fields extracted, conflicts settled, unrecognized fields, blocked bikes.
- Ends with an explicit approve or abort prompt. Nothing is written before approval (FR-7).
- Plain text must be fully readable without color. Color, if used, follows `NO_COLOR`. Flags use words like `CONFLICT` and `UNRECOGNIZED`, not color alone.
- Re-running on an unchanged PDF reports "0 changes" (FR-4 idempotence).

## Inspiration & Anti-patterns

- **Aura (editor theme):** the mood reference for the dark, violet-tinted palette with neon emphasis. `[ASSUMPTION]` This means Aura Dark.
- **Lifted from 99spokes:** nothing visual. It is the problem statement (it describes bikes but doesn't answer "will it fit"), not a design reference.
- **Lifted from vendor spec sheets (Van Rysel RCR, `imports/rcr-geometry-source.png`):** the short codes (ST, HT, TT, HTA, STA, CS, FL, FR, BB, S, R, E) and the idea of a labeled schematic. The shipped artwork (`imports/BikeGeometry.svg`) is the user's own original drawing, not derived from Van Rysel's file.
- **Deferred, not rejected — header/diagram cross-highlight on hover.** Considered, and the technical approach is straightforward if picked up later (inline SVG, each dimension line as a separately-addressable element, CSS/JS toggle on hover/focus — no extra images needed). Held back for now because the diagram itself was still taking shape and the user wanted to see the finished artwork first. Revisit once `BikeGeometry.svg` is considered final.
- **Rejected: a single fit score or a red/yellow/green traffic light.** The product is deliberately a heatmap plus In-Range Count, and red/green fails colorblind users.
- **Rejected: hiding unknown or unevaluated columns.** Honest gaps are part of the promise. A column with no data still appears.
- **Rejected: size as a filter or category.** A suitable bike is never hidden because of its size.
- **Rejected: spec-sheet browsing.** No frame material, components or wheel size.

## Key Flows

### Flow 1: Shortlist check — realizes UJ-1 (Camille, 178 cm, Sunday evening on the couch with a laptop)

1. Camille opens Fit my Ride from the home screen. It is the first run, so metric is selected and the fields are empty.
2. Camille enters height 178 and cycling inseam 82, then picks "Road" from the riding-style list, which is loaded from the database.
3. Submit. The form collapses into the summary bar (`178 cm · Inseam 82 cm · Road`). The table skeleton appears, then fills: "31 of 47 bikes fit · 16 excluded".
4. Camille doesn't recognize "BB," so she glances at the Geometry Diagram above the table — the line showing how far the pedal axle sits below the wheel axles, labeled the same way.
5. The table is sorted by In-Range Count. Camille clicks the Reach header to see borderline bikes. Closest to range comes first, and unknown cells sink to the bottom.
6. **Climax:** Two Van Rysel rows and one KTM row show a light-neutral ideal cell in Reach and Stack, and their In-Range Counts stand out in neon. A KTM row shows an orange `▲ 74.6°` in Seat Tube Angle, so Camille can see exactly how far off it is without opening a PDF.
7. Camille notes the two bikes worth test riding.

Failure: the server is unreachable, so Results shows the offline message with a retry action and no stale table.

### Flow 2: Phone check with imperial input — realizes UJ-1 (Camille, standing in a shop)

1. Camille opens the installed PWA on a phone. Last time's metric entry is remembered, and Results shows the summary bar.
2. Camille taps Edit and switches the toggle to `ft·in`. The remembered values convert in place (5 ft 10 in, 32.3 in). Camille adjusts the inseam and resubmits.
3. The table appears with the Bike column pinned. Camille turns the phone to landscape and scrolls right across the columns.
4. **Climax:** Camille taps a Reach cell on the bike in front of them, and the bottom sheet says "Reach 39.4 cm · slightly long · your range 38.5–40.0". The decision is made in a few seconds, in the shop.

Failure: a value is out of range, so the inline error under the field says which range is accepted, and Submit stays disabled.

### Flow 3: Builder review before commit — realizes UJ-2 (Baptiste, a new vendor PDF ready)

1. Baptiste runs the ingestion command against the vendor's PDF page range.
2. The parser finishes and prints the review summary: counts up top, then a table of fields with value, unit, source and matched synonym.
3. Two rows are flagged `CONFLICT` (arbitration picked the newer official source) and one field is listed as `UNRECOGNIZED`.
4. **Climax:** One matched synonym is visibly wrong (the parser mapped a fork field to Wheel Base). Baptiste catches it in the summary, aborts, fixes the Synonym Map (PRD §3 — the vendor-to-canonical field dictionary, FR-5), and re-runs. Nothing wrong reached the database.
5. On the clean re-run, Baptiste approves and the data commits.

Failure: no approval is given, so nothing is written.

## Open Items

- **Geometry Diagram shows 12 parameters, the table 5.** Decide later whether to highlight the 5 Core Parameters on the diagram.
- **Hard exclusion vs. coloring.** FR-1 excludes bikes by Core Parameter geometry, but which of the 5 exclude a bike, and which only color a cell, depends on PRD Open Question 1 (evaluators are the first piece of build work).
- **"Aura" hex values** are from memory and need checking against the theme.
- **Phone treatment of the diagram** (collapsed strip) is an assumption, not confirmed with the user.
- **Header/diagram cross-highlight** — deferred, not decided against. See Inspiration & Anti-patterns.
