# LUMINARK OVERWATCH PRIME — Architecture Guardrails

**Non-Negotiable System Rules | Version 1.0 | March 2026**

---

## THE ANCHOR SENTENCE

Before any AI model, developer, or contributor touches this codebase, they must read this:

> LUMINARK Overwatch PRIME is a predictive monitoring engine for complex systems.
> Do NOT simplify it into a self-help tool, personality quiz, slider app, or symbolic toy.
> Preserve these fixed modules exactly:
> 1. NSDT Engine
> 2. Stage Classifier
> 3. TrapScore Engine
> 4. Temporal State Engine
> 5. Consensus Engine
> 6. Pattern Recurrence Engine
> 7. Alert Engine
>
> All new work must fit into one of four layers only:
> Core Engine | Domain Adapter | Application | Interface
>
> Do not rewrite the architecture.
> Do not replace telemetry-driven inputs with subjective user inputs.

---

## THE FOUR LOCKED LAYERS

### Layer A — Core Engine (`luminark/core/`)
**PROTECTED. Never casually rewritten.**

Files: `nsdt.py`, `trapscore.py`, `temporal.py`, `consensus.py`, `recurrence.py`, `alerts.py`, `schemas.py`, `__init__.py`

Rules:
- No UI logic inside core
- No branding or marketing language inside core
- No therapy, self-help, or spiritual language inside core
- No slider-based or subjective inputs — only structured telemetry
- All functions must have type hints
- All functions must be independently testable
- Stage math, trajectory math, and risk logic must be versioned and pass tests before deployment

### Layer B — Domain Adapters (`luminark/adapters/`)
**One job: map source telemetry to the 5 NSDT dimensions.**

Files: `grid.py`, `vehicle.py`, `hvac.py`, `network.py`, `human.py`

Rules:
- Each adapter receives domain-specific raw metrics
- Each adapter returns exactly one `NSDTVector`
- No business logic inside adapters — only mapping
- No direct calls to alert or stage engines from adapters
- Adapters may be updated freely as long as output schema is preserved

### Layer C — Applications (`luminark/apps/`)
**Products built on top of the engine using adapters.**

Rules:
- Each app calls the core engine — it does not contain core logic
- Each app uses exactly one adapter (or explicitly combines adapters with documented rationale)
- App-level versioning is independent of core engine versioning
- A new domain use case = a new app + a new adapter, NOT a rewrite of the core

### Layer D — Interfaces (`luminark/interfaces/` and `apps/*/`)
**Views only. The interface never defines the logic.**

Rules:
- Dashboards may display results but cannot redefine scoring
- If the UI disappears tomorrow, the engine must still work
- API endpoints are interfaces — they call the engine, they don't replace it
- No calculation logic in React/JS/HTML — all computation happens server-side

---

## FORBIDDEN TRANSFORMATIONS

The following changes are prohibited without a formal version increment and documented rationale:

| What | Why Forbidden |
|---|---|
| Replacing NSDT telemetry inputs with user sliders | Destroys predictive validity |
| Moving stage classification to the UI layer | Engine must be authoritative |
| Adding spiritual/consciousness language to core outputs | Undermines commercial credibility |
| Merging adapter logic into core modules | Destroys domain-agnosticism |
| Changing TrapScore formula without versioning | Breaks validated performance claims |
| Removing the Temporal State Engine | Eliminates trajectory prediction capability |
| Replacing the Consensus Engine with single-evaluator scoring | Eliminates uncertainty quantification |
| Hardcoding domain-specific behavior into core | Locks the engine to one use case |

---

## VERSIONING RULES

Use two independent version streams:

**Core Engine versioning** — changes when any core module logic changes:
- `Core Engine v1.0` → initial production release
- `Core Engine v1.1` → minor logic refinement
- `Core Engine v2.0` → stage centroid recalibration or new module

**Product versioning** — changes when app or UI changes:
- `Grid Overwatch App v1.0`
- `Fleet Monitor v1.0`
- `Personal SAP Tool v1.0`

A UI redesign does NOT increment the core engine version.
A core centroid recalibration does NOT require a new product version.

---

## VOCABULARY RULES

Use two vocabularies. Keep them strictly separate:

**Technical vocabulary** (for code, patent, utilities, investors):
- stage classifier, telemetry vector, trajectory state, failure mode, alert level,
- NSDT vector, TrapScore, centroid distance, consensus confidence, recurrence match

**Symbolic vocabulary** (for books, brand storytelling, consumer products — downstream only):
- SAP stages, star names, trickster pedagogy, Ma'at principles, healing frameworks

The symbolic layer can explain the system to a general audience.
It must NEVER appear in core engine code, API responses, or technical documentation.

---

## PROMPT HEADER FOR AI WORK

Prepend this to any AI session that touches LUMINARK code:

```
LUMINARK is a predictive monitoring engine for complex systems.
Core Engine v1.0. Do not simplify, rebrand, or drift.
Protected modules (do not rewrite logic):
1. NSDT Engine (nsdt.py)
2. Stage Classifier (nsdt.py)
3. TrapScore Engine (trapscore.py)
4. Temporal State Engine (temporal.py)
5. Consensus Engine (consensus.py)
6. Pattern Recurrence Engine (recurrence.py)
7. Alert Engine (alerts.py)

Four layers only: Core Engine | Domain Adapter | Application | Interface
All inputs must be structured telemetry, not subjective sliders.
All outputs must conform to CANONICAL_INPUT_OUTPUT_SCHEMA.json.
```

---

## PROTECTED TEST SUITE

These tests must pass before any core engine deployment:

```
tests/
  test_nsdt.py          — stage classification from known vectors
  test_trapscore.py     — formula validation at boundary conditions
  test_temporal.py      — trajectory detection with known histories
  test_consensus.py     — evaluator agreement and disagreement cases
  test_recurrence.py    — pattern matching against validated event library
  test_alerts.py        — alert level escalation logic
  test_grid_adapter.py  — EIA-930 telemetry → NSDT mapping validation
```

If any test fails, the deployment is blocked. No exceptions.

---

*This document is the architectural constitution of LUMINARK Overwatch PRIME.
Richard L. Stanfield | Meridian Axiom Alignment Technologies | March 2026*
