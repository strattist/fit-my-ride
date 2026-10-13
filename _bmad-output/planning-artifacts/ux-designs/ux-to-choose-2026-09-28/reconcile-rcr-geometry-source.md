# Reconcile — imports/rcr-geometry-source.png

**Source:** Van Rysel RCR geometry sheet (vendor PDF page, user-supplied, converted from AVIF).

## What it is

A labeled bike-frame diagram (ST, HT, TT, HTA, STA, CS, FL, FR, BB, S, R, E) paired with a per-size (XXS–XL) measurement table in mm/degrees.

## What was taken from it

- The 12 short codes and their meanings — confirmed as matching the PRD's 12 Geometry Parameters and its Canonical Schema baseline (PRD §3: "Naming and units follow Van Rysel's own geometry table").
- The idea of a labeled schematic as the way to explain what each code measures — became the Geometry Diagram.
- Confirmation that the vendor stores values in mm/degrees per size, while the Canonical Schema normalizes to cm (PRD FR-5) — no spine change needed, just a consistency check that passed.

## What was explicitly NOT taken

- The image itself. It is Van Rysel's own copyrighted illustration — flagged early in the session, resolved by treating it as reference-only, never embedded or traced. The shipped Geometry Diagram artwork (`imports/BikeGeometry.svg`) is the user's independent original drawing.

## Dropped ideas

None. Nothing qualitative from this source was discussed and set aside — its only role was as a naming/layout reference, and that role was fully absorbed into the spines.
