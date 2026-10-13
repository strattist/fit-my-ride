---
name: Fit my Ride
description: Sporty, technical, dark-first identity for a bike-fit heatmap PWA. Aura-inspired neutrals, one violet for interaction, one neon mint for emphasis, and a colorblind-safe blue-to-orange five-step heat scale.
status: final
updated: 2026-09-28
colors:
  # [ASSUMPTION] Neutrals and accents approximate the Aura Dark editor theme from memory — verify hex values against the theme before build.
  background: '#15141B'
  surface: '#1E1D27'
  surface-raised: '#29263C'
  border: '#3D3A52'
  text: '#EDECEE'
  text-muted: '#A19FB0'
  primary: '#A277FF'
  primary-foreground: '#15141B'
  neon: '#61FFCA'
  focus-ring: '#82E2FF'
  error: '#FF6767'
  # Deliberate, isolated exception to the dark theme: a light ground for the
  # Geometry Diagram, whose artwork is dark line art (see Components).
  diagram-card: '#EDEAF3'
  # Heat scale — exactly five tiers, told apart by hue (blue short side, orange long side, light neutral center).
  heat-too-short: '#3D6FE0'
  heat-too-short-text: '#FFFFFF'
  heat-slight-short: '#8FB8FF'
  heat-slight-short-text: '#15141B'
  heat-ideal: '#F1EEF7'
  heat-ideal-text: '#15141B'
  heat-slight-long: '#FFBF80'
  heat-slight-long-text: '#15141B'
  heat-too-long: '#F07028'
  heat-too-long-text: '#15141B'
  # Unknown is not a heat tier: no fill, dashed outline. Lightened from an
  # earlier #4A4760 (~1.9:1) to clear WCAG 1.4.11's 3:1 non-text minimum
  # against `surface` (computed ~3.5:1) — accessibility review finding.
  cell-unknown-border: '#726F8A'
typography:
  # [ASSUMPTION] Inter for UI, JetBrains Mono for numerals. Both bundled locally (self-hosted, offline-capable PWA); no CDN fonts.
  headline:
    fontFamily: 'Inter'
    fontSize: 22px
    fontWeight: '600'
    lineHeight: '1.25'
    letterSpacing: -0.01em
  body:
    fontFamily: 'Inter'
    fontSize: 15px
    fontWeight: '400'
    lineHeight: '1.5'
  label:
    fontFamily: 'Inter'
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.3'
    letterSpacing: 0.06em
  numeric:
    fontFamily: 'JetBrains Mono'
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.2'
    fontFeature: 'tnum'
  numeric-lg:
    fontFamily: 'JetBrains Mono'
    fontSize: 20px
    fontWeight: '600'
    lineHeight: '1.2'
    fontFeature: 'tnum'
rounded:
  sm: 4px
  md: 8px
  lg: 12px
  full: 9999px
spacing:
  '1': 4px
  '2': 8px
  '3': 12px
  '4': 16px
  '6': 24px
  '8': 32px
  gutter: 16px
  cell-gap: 2px
  cell-min-width: 64px
  cell-height: 40px
  tap-target: 44px
components:
  page:
    background: '{colors.background}'
    foreground: '{colors.text}'
  panel:
    background: '{colors.surface}'
    border: '{colors.border}'
    radius: '{rounded.lg}'
  button-primary:
    background: '{colors.primary}'
    foreground: '{colors.primary-foreground}'
    radius: '{rounded.md}'
    height: '{spacing.tap-target}'
  input:
    background: '{colors.surface-raised}'
    foreground: '{colors.text}'
    border: '{colors.border}'
    radius: '{rounded.md}'
    height: '{spacing.tap-target}'
    focus-ring: '{colors.focus-ring}'
  unit-toggle:
    background: '{colors.surface-raised}'
    foreground: '{colors.text-muted}'
    active-background: '{colors.primary}'
    active-foreground: '{colors.primary-foreground}'
    radius: '{rounded.full}'
  heat-cell:
    radius: '{rounded.sm}'
    typography: '{typography.numeric}'
    min-width: '{spacing.cell-min-width}'
    height: '{spacing.cell-height}'
    # See § Colors — a single {colors.focus-ring} ring fails 3:1 on 4/5 heat fills.
    focus-halo-inner: '{colors.background}'
    focus-halo-outer: '{colors.focus-ring}'
  heat-cell-unknown:
    background: 'transparent'
    foreground: '{colors.text-muted}'
    border: '{colors.cell-unknown-border}'
    radius: '{rounded.sm}'
  popover:
    background: '{colors.surface-raised}'
    foreground: '{colors.text}'
    border: '{colors.border}'
    radius: '{rounded.md}'
    typography: '{typography.body}'
  bottom-sheet:
    background: '{colors.surface-raised}'
    foreground: '{colors.text}'
    radius: '{rounded.lg}'
    typography: '{typography.body}'
  column-header:
    background: '{colors.surface}'
    foreground: '{colors.text-muted}'
    active-foreground: '{colors.neon}'
    typography: '{typography.label}'
  show-excluded-toggle:
    background: '{colors.surface-raised}'
    active-background: '{colors.primary}'
    foreground: '{colors.text-muted}'
    radius: '{rounded.full}'
  excluded-row-badge:
    background: 'transparent'
    foreground: '{colors.text-muted}'
    border: '{colors.border}'
    radius: '{rounded.sm}'
    typography: '{typography.label}'
  geometry-diagram:
    background: '{colors.surface}'
    card-background: '{colors.diagram-card}'
    caption: '{colors.text-muted}'
    label: '{typography.label}'
    radius: '{rounded.lg}'
    card-radius: '{rounded.md}'
  in-range-count:
    foreground: '{colors.neon}'
    typography: '{typography.numeric-lg}'
  summary-bar:
    background: '{colors.surface}'
    foreground: '{colors.text}'
    accent: '{colors.neon}'
    radius: '{rounded.lg}'
---

> **STALE — do not build from this copy.** It predates the 2026-10-11 architecture decisions (5 Core Parameters, bikes missing a Core Parameter blocked at ingestion, angles in degrees). The current version is `docs/ux/DESIGN.md`.


## Brand & Style

Fit my Ride should feel like a sport-science instrument: sporty and technical, precise rather than playful. It is a dark-first interface, close to the Aura editor theme in mood, with a touch of neon used only to make key text and numbers pop. Numbers are the product, so numerals are monospaced, tabular, and never decorated. There are no illustrations, photography, or bike imagery in v1.

Colorblind suitability is a hard requirement, not a polish item. The heat scale is built from hue (blue to orange) plus a lightness peak at the center, and every heat cell also carries a glyph. Neon is emphasis only and never carries fit meaning.

## Colors

- **Neutrals (`background`, `surface`, `surface-raised`, `border`)** are a deep violet-tinted charcoal. Surfaces separate by tone, not by shadow.
- **`text` / `text-muted`** are the two text levels. Muted is for labels, ranges, and secondary information. Both pass AA on every dark surface.
- **`primary` (violet)** marks interaction: buttons, the active unit toggle, links, and selected controls. It is never used for emphasis text or in the heat scale.
- **`neon` (mint)** is the emphasis accent: the In-Range Count number, the active sort column header, key figures in the summary bar. It is text-only. It never fills a cell, never serves as a status color, and never sits next to the heat scale as if it carried fit meaning.
- **`focus-ring` (light blue)** is the keyboard focus outline for controls on neutral surfaces (form fields, buttons, headers) — high contrast there. On heat cells, a single `focus-ring` ring fails WCAG 1.4.11's 3:1 minimum against 4 of the 5 fill colors (accessibility review finding), so heat cells use a two-tone halo instead: an inner ring in `{colors.background}`, an outer ring in `{colors.focus-ring}` (`focus-halo-inner`/`focus-halo-outer` — see Components → Heat cell). The inner ring reads against light fills, the outer ring against the dark table surface, whichever fill sits underneath.
- **`error`** is for form validation and offline or failure messages, always with a text label.

**Heat scale (five tiers).** Blue means the parameter is on the short side of the rider's range, orange means the long side, and the light neutral center means in range. Contrast was checked, not eyeballed: text on every fill is at least 4.5:1 (`heat-too-short-text` is the thinnest margin, ~4.62:1 — worth a re-check against real anti-aliased rendering once built). Adjacent tiers also stay separable under simulated protanopia, deuteranopia, and tritanopia (worst case ΔE ≈ 23, most pairs 35–48). Computed values and method are in `.working/heat-scale-cvd-check.md`, written after an accessibility review found the earlier "ΔE ≥ 27" claim asserted without saved evidence.

| Tier | Token | Meaning |
|---|---|---|
| Too short | `heat-too-short` | Well below the rider's ideal range |
| Slightly short | `heat-slight-short` | Just below the range |
| Ideal range | `heat-ideal` | Inside the range |
| Slightly long | `heat-slight-long` | Just above the range |
| Too long | `heat-too-long` | Well above the range |

**Unknown** is not a sixth tier. It has no fill, a dashed `cell-unknown-border` outline, and a muted `—`, so it can't be mistaken for "ideal" (light fill) or any other tier.

Avoid red/green pairs for any meaning. Never use the heat colors outside the table and its legend.

## Typography

Inter carries the interface. JetBrains Mono, with tabular figures, carries every number in the table, the summary bar, and range labels, so columns of values line up. `label` is small uppercase-tracked, for column headers and field labels. All fonts ship with the app, since it is self-hosted and installable.

## Layout & Spacing

A 4-based scale. The results view is a wide, dense table: cells are `{spacing.cell-min-width}` × `{spacing.cell-height}` with a `{spacing.cell-gap}` gap so the grid reads as a heatmap rather than a spreadsheet. Page gutter is `{spacing.gutter}`. On desktop, the form and the summary bar sit above the table, aligned to the table's left edge.

On phone, the table is the exception to the single-column rule: it scrolls horizontally inside its own container. The Bike column is sticky, the header rows are sticky, and controls keep a `{spacing.tap-target}` minimum touch size.

## Elevation & Depth

Tonal layering only: `background` → `surface` → `surface-raised`. The only shadow is on the sticky Bike column and sticky header while content scrolls under them, so the pinning reads clearly. There are no decorative glows. Neon is a text color, not a glow.

## Shapes

`rounded.sm` (4px) on heat cells, so the grid stays tight. `rounded.md` (8px) on inputs and buttons. `rounded.lg` (12px) on panels and the summary bar. Fully rounded (`rounded.full`) only on the unit toggle and the show-excluded toggle.

## Components

- **Heat cell.** Fill and text come from the tier's `heat-*` pair. Contents: a tier glyph, then the value in `{typography.numeric}` at 0.1 precision (for example `▽ 39.4`). Glyphs: `▼` too short, `▽` slightly short, `●` ideal, `△` slightly long, `▲` too long — rendered at the *same size* as the value, not smaller: a filled-vs-outline pair (`▼`/`▽`, `▲`/`△`) is hard to tell apart at small sizes, and the glyph is only the tertiary channel behind color and the printed number regardless of size. Focus/hover uses the two-tone halo, not a single ring — see § Colors. Cell height is fixed.
- **Unknown cell.** No fill, dashed `{colors.cell-unknown-border}` outline, muted `—`. The same treatment is used for a missing value and for a parameter with no evaluation method yet. Behavioral rules for each reason: `EXPERIENCE.md` § State Patterns ("Unknown cell", "Not-evaluated column").
- **Popover / bottom sheet.** The Heat cell's tap/hover detail (value, tier, range, distance from range — behavior: `EXPERIENCE.md` § Component Patterns → Heat cell). Desktop: a `popover` card — `{colors.surface-raised}` background, `{colors.border}` outline, `{rounded.md}` corners, `{typography.body}` text, anchored near the cell. Phone: a `bottom-sheet` — same background, `{rounded.lg}` top corners only, full width, slides from the bottom.
- **Column header.** `label` type in muted color, showing the short code (for example `TT`) with the full parameter name and unit underneath. A second sticky line shows the rider's range for that column (`numeric`, muted), or `not evaluated`. The active sort column turns `{colors.neon}` and shows a direction arrow.
- **Show-excluded toggle.** Same switch mechanism as `unit-toggle`: `{colors.surface-raised}` track, `{colors.primary}` fill when on.
- **Excluded row badge.** When the show-excluded toggle is on, an excluded row carries a visible text badge (`{colors.text-muted}` on transparent, `{colors.border}` outline, `label` type — for example "Excluded — outside your range"), never a dimming/opacity treatment alone.
- **Geometry Diagram.** A static reference: a labeled bike schematic showing all 12 Canonical Schema parameters as dimension lines with their short codes, in Canonical Schema order (ST, HT, TT, HTA, STA, CS, FL, FR, BB, S, R, E — see `EXPERIENCE.md` § Inspiration & Anti-patterns for the artwork's sourcing). It sits inside its own `{colors.diagram-card}` light card (`{rounded.md}` corners) within the darker `geometry-diagram.background` panel, since the artwork's dark-gray strokes need a light ground to read — the one deliberate exception to the dark theme (see Do's and Don'ts). The panel's caption stays in `{colors.text-muted}` on the dark ground outside the card. One diagram covers every Usage Taxonomy type. v1 has no interaction with the table — see `EXPERIENCE.md` § Open Items.
- **In-Range Count cell.** `{typography.numeric-lg}` in `{colors.neon}`, shown as `n / 12`.
- **Bike cell.** Vendor in `label` type over model name in `body`. It is pinned on scroll.
- **Size cell.** Plain muted text (`54`, `M`). It is information only, with no fill and no sort affordance.
- **Form fields.** `input` and `unit-toggle`. The riding-style field is a select fed from the database. The `cm` / `ft·in` toggle is a two-segment pill.
- **Summary bar.** A `panel` that replaces the form after submit: `178 cm · Inseam 82 cm · Road`, with values in `{colors.neon}` and an edit control in `{colors.primary}`.
- **Legend.** A row of five swatches with glyph and label, always visible above the table. On phone it collapses to a tap-to-open strip.

## Do's and Don'ts

| Do | Don't |
|---|---|
| Show a glyph and a number in every colored cell | Rely on color alone for fit meaning |
| Keep the heat scale blue ↔ orange with a light center | Use red/green, or add a sixth heat color |
| Use neon for text emphasis only | Fill cells or badges with neon, or use it as a status color |
| Use tabular monospace for every numeral | Mix proportional and mono numerals in the table |
| Render unknown as dashed outline + `—` | Fill unknown with a "neutral" heat color or leave it blank |
| Separate layers by tone | Add glows, gradients or drop shadows for decoration |
| Bundle fonts and assets locally | Load fonts or icons from a CDN |
| Host the Geometry Diagram on its own `{colors.diagram-card}` light card | Otherwise introduce light surfaces into the dark theme, or force the diagram's dark line art onto a dark ground |
| Use the two-tone focus halo on heat cells | Rely on a single `{colors.focus-ring}` outline on a colored fill |
| Mark an excluded row with a text badge | Mark it with dimming/opacity alone |
