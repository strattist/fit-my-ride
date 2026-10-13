# Reconcile — imports/BikeGeometry.svg

**Source:** User-drawn original artwork (confirmed original, not traced or sourced from a stock/vendor asset — see `.memlog.md`).

## What it is

A full bike-frame line drawing (wheels with spokes, drop bars, saddle, crank) with all 12 canonical dimension codes (ST, HT, TT, HTA, STA, R, S, HT, FL, FR, CS, BB, E) as labeled dimension lines, in dark gray (`#424242`) strokes on a transparent/white ground.

## What was taken from it

- Used directly as the Geometry Diagram's shipped artwork — inlined verbatim into `mockups/key-results-desktop.html` and referenced by both spines (`DESIGN.md` § Components → Geometry Diagram; `EXPERIENCE.md` § Component Patterns → Geometry Diagram).
- Its dark-on-light coloring drove a real DESIGN.md decision: since it can't sit directly on the dark theme's `surface` background, it now has its own `{colors.diagram-card}` light card — documented as the one deliberate, isolated exception to the dark theme (DESIGN.md § Colors, § Do's and Don'ts).
- Its tight top-edge framing was checked (SVG `getBBox()`) and confirmed not to be a clipping bug — no fix needed, just verified.

## What was explicitly NOT taken (yet)

- **Per-parameter separability for a hover highlight.** The artwork is flat/unstructured (individual `<line>`/`<path>` elements without per-parameter grouping or ids). The header↔diagram cross-highlight interaction was discussed in depth (including the technical approach: inline SVG, named per-parameter elements, CSS/JS toggle, no extra images needed) but deliberately deferred for v1 at the user's explicit request, pending seeing the finished diagram. See `EXPERIENCE.md` § Inspiration & Anti-patterns and § Open Items. If picked up later, the SVG would need its parts separated and labeled — a rework of this file, not a new drawing.

## Dropped ideas

- An earlier, hand-coded placeholder diagram (abstract stick-figure lines, later a heavier-stroke attempt) was built and shown to the user across two iterations before this asset arrived. Both were explicitly rejected by the user as "not really representative" — fully superseded, not referenced further. No content from those attempts carried forward except the lesson that hand-coded SVG guesswork wasn't a good process for this asset.
