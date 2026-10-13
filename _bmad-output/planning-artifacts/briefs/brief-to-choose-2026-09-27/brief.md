---
title: Product Brief: Fit my Ride
status: final
created: 2026-09-27
updated: 2026-09-27
---

# Product Brief: Fit my Ride

## Executive Summary

A bike-fit matching platform: a rider enters a handful of body measurements and gets back a heatmap comparing candidate bikes' geometry against their body — one bike per row, one geometry parameter per column, colored by how close each parameter is to the rider's ideal range. Seeded from two vendors' PDF spec sheets, parsed and reconciled into one canonical schema.

This is a passion project built by two friends, with no monetization intent. The point is to build something you'd actually use to pick your own next bike, and to see what AI-assisted tooling (LLM/OCR extraction, schema reconciliation, coding itself) can do across the whole stack — data pipeline, fit logic, and UI. V1 is deliberately narrow: prove the fit-matching idea is worth using on its own, before any marketplace, map, or shop layer exists.

## The Problem

Existing bike-search tools (e.g. 99spokes) let you browse and filter by spec — frame material, wheel size, components — but they don't tell you whether a given bike actually *fits your body*. Geometry tables exist per vendor, in inconsistent units and naming (seat tube angle / STA / seat angle...), scattered across PDFs, so comparing fit across brands means manually reading spec sheets and doing the geometry-to-body translation yourself. That translation step — the part that actually answers "will this bike fit me" — is the part no one has made easy.

## The Solution

Two pieces, built together:

**Fit engine** — the rider supplies a required tier of measurements (height, cycling inseam, riding style/goals). The platform outputs a heatmap table: one bike per row, one geometry parameter per column, each cell colored on a diverging scale (too short / ideal / too long) relative to the rider's ideal range for that parameter. Ranking is done by heatmap interaction — sort by any column, or by count of in-range parameters — not a computed weighted score (no such formula exists yet, and inventing one is explicitly deferred).

**Data pipeline** — geometry data for a maximum of two vendors (chosen for contrasting PDF layouts, to stress-test the approach early), extracted via LLM/OCR from vendor PDF spec sheets. Extracted values are reconciled into one canonical schema: a small core parameter set (stack, reach, top tube, seat angle, standover), a per-vendor name-synonym map, and unit conversion to a single canonical unit (cm). Vendor category names are mapped onto a small fixed usage taxonomy (road, gravel, MTB, city/commute, touring, e-bike...). Every field carries provenance and date, so conflicting values are arbitrated (official vendor source beats scraped/community; most recent wins among official sources). Ingestion is one idempotent pipeline, manually triggered, with a mandatory pre-commit review summary showing what the parser extracted (value, unit, source, matched synonym) before anything lands in the database.

## What Makes This Different

This platform's bet is narrower and specific than existing spec-browsing tools: deep rider-measurement fit — tiered inputs, a heatmap against your actual body, honest handling of missing data — rather than another spec browser. The differentiator isn't more data, it's answering the fit question directly. If the fit layer alone isn't worth using before any shop/map/marketplace feature exists, the bet hasn't worked — which is why v1 deliberately excludes all of that.

## Who This Serves

Day one: you and your friend, as riders who want a better way to check whether a bike actually fits before buying — and as builders who want to use this as a vehicle for exploring AI-assisted data extraction and product-building. Designed for up to 5 users, self-hosted — not for public internet traffic. Longer term, it might move to the web for a wider audience, but that's a possible later step, not a v1 requirement — v1 should not pay a complexity tax (auth hardening, scaling, multi-tenant concerns) for a future that may not happen.

## Success Criteria

This is a fun/learning project, so success is personal and technical rather than commercial:

- You'd actually use it yourself to help decide on a real bike purchase.
- The pipeline cleanly ingests both vendors' PDFs into the canonical schema, with the parser-review step catching extraction errors before they land in the database.
- The heatmap makes a fit judgment easier and clearer than reading two vendors' spec sheets by hand.
- Along the way, you learn something concrete about using AI/LLM tooling for structured extraction and for building the product itself.

## Scope

**In (V1 Must-have):**
- Required-tier rider input only (height, cycling inseam, riding style/goals) — the only tier that hard-excludes non-fitting bikes.
- Heatmap table output, sortable by column or by in-range-parameter count. No weighted global score.
- Two vendors, full catalogs, PDF/OCR-seeded.
- Canonical geometry schema + per-vendor synonym map + unit normalization (cm) + usage taxonomy mapping — one reusable canonical-target-plus-dictionary pattern.
- Provenance + date per field for conflict arbitration.
- Manual-trigger, idempotent ingestion pipeline with mandatory pre-commit parser-review summary.
- Missing data shown honestly as "unknown," never silently excluded.
- Self-hosted, up to 5 users — no public-scale deployment concerns in v1.

**Out of V1 (deferred, see addendum for the full backlog):**
- The entire shop/map/dealer layer (list, badges, claim flow).
- User accounts (no auth layer to build against in v1).
- Any weighted global-score formula.
- Free-text prompt, height-only quick mode, and other input conveniences (Should-have, not core to the bet).

## What's Next

If the fit-only bet proves out, the natural fast-follows are the dealer list (with distance) and shop badges, then the input-precision spectrum's other end (geometry-target/expert mode) — see the addendum for the fuller set of deferred ideas and the reasoning already worked out for each. None of that needs deciding now; the PRD can pick it up when v1 is real.
