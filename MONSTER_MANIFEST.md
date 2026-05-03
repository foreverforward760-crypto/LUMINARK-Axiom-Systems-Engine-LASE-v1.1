# MONSTER_MANIFEST.md
## LUMINARK Axiom Systems Engine (LASE) — Component Inventory
### Generated: May 2, 2026

---

## Build Integrity Checklist

- [x] Canonical SAP engine (luminark/ package) — 090LuminarkHybridEngine090 v8.2.1
- [x] All four build presets — overwatch_strict, kairos, active_defense, unified_field
- [x] Full test suite — tests/test_cross_build.py, test_tumbling_inversion.py, etc.
- [x] Stage 8 dual-chamber trap — sap_energy_layer.py (canonical, tested, zero deprecated terms)
- [x] Stage 5 three-way bifurcation — sap_energy_layer.py
- [x] Signal translation layer — sap_signal_translator.py
- [x] Five buyer demo scenarios — axiom_yield_scenarios.py
- [x] ULTRA runtime — OVERWATCH_PRIME_ULTRA.py (284KB, v1-v11 lineage)
- [x] OMEGA consciousness engine — CONSCIOUSNESS_ENGINE_OMEGA.py (272KB)
- [x] Adaptive calibration layer — UpdateAndRestoredOverwatch v5 (7 files)
- [x] Guardian FastAPI service — luminark-guardian v2.0
- [x] Metatron SAP Copilot backend — Plaid, threat intel, user behavior
- [x] Axiom Yield logistics app — FastAPI backend + HTML frontend
- [x] Overwatch Demo UI — React/TS investor-ready frontend (full Shadcn stack)
- [x] Next.js frontend v2.0 — with domain adapters (grid, hvac, network, org, vehicle)
- [x] All canonical markdown documentation
- [x] Patent specification docs (OMEGA + ULTRA amended)
- [x] SBIR Phase I narrative
- [x] 28-region classified grid results (EIA-930 data)
- [x] NYIS forensic audit + patent evidence

---

## Deprecated Terms — Confirmed Absent

The following terms must not exist anywhere in this repo.
Run: `grep -r "false_hell\|False Hell\|FALSE_HELL\|False Heaven\|F-HELL" LASE/`
Expected result: zero matches (excluding documentation flagging them as deprecated).

---

## Key File Locations

### Start Here (Engine)
```
core/luminark/engine_factory.py     ← factory layer, creates build instances
core/luminark/sap_types.py          ← SAPStage enum, NSDTVector, SystemState
engine/sap_energy_layer.py          ← Stage 5 + Stage 8 trap logic (canonical)
engine/sap_signal_translator.py     ← broker-facing signal output
```

### Start Here (API)
```
apps/guardian/api/main.py           ← Guardian FastAPI entry point
apps/axiom_yield/backend/           ← Axiom Yield FastAPI backend
apps/metatron/backend/app/main.py   ← Metatron Copilot entry point
runtime/calibration/api_v5.py       ← Calibrated defense system API
```

### Start Here (Frontend)
```
apps/overwatch_demo/client/         ← React/TS investor demo (most production-ready)
frontend/app/page.tsx               ← Next.js v2 entry point
apps/axiom_yield/index.html         ← Axiom Yield broker dashboard (zero deps)
```

### Start Here (Demo)
```
engine/axiom_yield_scenarios.py     ← Run 5 scenarios: python axiom_yield_scenarios.py
engine/axiom_yield_demo_scenarios.json  ← Buyer-facing JSON output
```

### Start Here (Docs)
```
docs/LUMINARK_SYSTEM_OVERVIEW_v8.2.1.md   ← System architecture overview
docs/MATHEMATICAL_FOUNDATIONS.md           ← SAP mathematical spec
docs/TUMBLING_INVERSION_v8.2.md            ← Inversion principle formal doc
docs/INDUSTRIAL_CLASSIFIERS.md             ← Stage 6-8 classifier detail
docs/patent/                               ← Patent specification documents
```

---

## Next Build Priorities

1. Wire `engine/sap_signal_translator.py` into `apps/axiom_yield/backend/main.py`
2. Replace placeholder `sap_energy_layer.py` in `apps/guardian/` with canonical version
3. Connect `apps/metatron/backend/app/sap_stage_engine.py` to `core/luminark/` package
4. Run retroactive stress test: point `engine/axiom_yield_scenarios.py` at historical logistics datasets
5. Wire `runtime/calibration/sap_calibration_engine.py` into `core/luminark/engine_factory.py`
