# CHANGELOG

All notable changes to the **LUMINARK Axiom Systems Engine (LASE)** are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [LASE v1.1] — 2026-05-03

### Added
- Formal **Five-Step Integration** pipeline, now fully documented in README:
  Ingestion & Normalization → Stage Classification → Energy Layer Transformation → Signal Translation → Output & Adaptive Calibration.
- `engine/sap_energy_layer.py` v2.0 — canonical Stage 8 Dual-Chamber Trap (1.45× amplifier), Stage 5 bifurcation with Middle Path detection.
- `engine/sap_signal_translator.py` v1.0 — universal domain signal translator (logistics, grid, guardian, biometric, finance).
- `engine/axiom_yield_scenarios.py` — five buyer-facing demo scenarios including Cascade Failure.
- `apps/axiom_yield/main.py` v2.0 — wired to canonical luminark.core engine + sap_signal_translator.
- `apps/metatron/app/sap_stage_engine.py` v2.0 — deprecated hand-rolled heuristics replaced with canonical EngineFactory delegation.
- `runtime/calibration/axiom_calibration_bridge.py` v1.0 — adaptive centroid learning layer wired to EngineFactory.
- `docs/MONSTER_TO_LASE_TRANSITION.md` — migration guide from Monster v1.0.

### Changed
- **Rebranded** from Monster v1.0 to **LUMINARK Axiom Systems Engine (LASE)** v1.1.
- Repository tree root now documented as `LASE/` (previously `Monster/`).
- Version string updated from v1.0 → v1.1.
- `MONSTER_MANIFEST.md` header updated to LASE nomenclature.
- `runtime/OVERWATCH_PRIME_ULTRA.py` — deprecated label `FALSE HELL` (line 93) replaced with canonical `Permanence Trap`; `sap_origin` field updated to `VESSEL OF GROUNDING — Stage 8 Dual-Chamber Trap`.
- `runtime/CONSCIOUSNESS_ENGINE_OMEGA.py` — deprecated terms `False Heaven` / `False Hell` in Stage 8 prose replaced with canonical `Illusion of Arrival` / `Illusion of Permanence`.
- `core/calibration_bridge.py` — comment referencing "Monster/" updated to "LASE/".

### Fixed
- Constitutional compliance: all live code deprecated-term violations corrected. Zero occurrences of `FALSE_HELL`, `False Hell`, `False Heaven`, `FALSE_HEAVEN`, `F-HELL`, `PRIMA_MATERIA`, `FORMATION`, `EMERGENCE`, `CREATIVE_EXPANSION`, `CATALYZED_TENSION` in any `.py` file.
- Deepseek's Five-Step table corrected: `stage_classifier.py` does not exist in LASE; correct file references are `core/build1_overwatch_strict/nsdt_engine_v65.py` and `core/build4_unified_field/nsdt_engine_v8.py`.

### Deprecated
- The name "Monster" is superseded by "LASE". Monster v1.0 is considered frozen.

### Migration Notes
- All canonical SAP engine files (`core/`) are untouched — no refactor required.
- Constitutional Directives, deprecated term lists, and Stage 8 naming remain in full force.
- Users who cloned Monster should switch to the LASE repository for all future updates.

---

## [1.0.0] – 2026-04-14

### Added – Top-level `luminark/` package (factory & shared types)
- `luminark/sap_types.py` — Shared data structures across all four builds:
  - `NSDTVector` — five-axis input with validation, `to_list()`, `to_dict()`, `to_json()`, `from_dict()`, `from_json()`, `from_list()`
  - `SAPAnalysisResult` — uniform output envelope (stage, energy, posterior, Lyapunov, unified field, therapeutic note) with JSON round-trip
  - `LyapunovState` — Lyapunov sub-result (Build 3 & 4)
  - `UnifiedFieldState` — Unified field sub-result (Build 4 only)
  - `SAP_STAGE_NAMES` — canonical stage name registry (constitutional constant)
  - `NSDT_JSON_SCHEMA` — full JSON Schema for NSDTVector (for API validation / OpenAPI)
  - `stage_name(int)` — helper to look up a canonical name by stage number
- `luminark/config.py` — `EngineConfig` dataclass:
  - Selects build ("overwatch", "kairos", "defense", "unified") plus all hyperparameters
  - JSON and YAML round-trip (`to_json`, `from_json`, `to_yaml`, `from_yaml`)
  - String aliases: "strict"→"overwatch", "v8"→"unified", "active_defense"→"defense", "therapeutic"→"kairos"
  - `PRESETS` dict with four named ready-to-use configurations
- `luminark/engine_factory.py` — `create_engine()` factory:
  - Uniform `.analyze(nsdt, system_id) → SAPAnalysisResult` interface across all four builds
  - `_OverwatchAdapter` — wraps Build 1 (Overwatch Strict v6.5)
  - `_DefenseAdapter` — wraps Build 3 (Active Defense v7)
  - `_UnifiedAdapter` — wraps Build 4 (Unified Field v8)
  - `_KairosAdapter` — wraps Build 2 (Kairos HTTP API) with graceful fallback if server not running
- `luminark/__init__.py` — clean single-import public surface
- `luminark/version.py` — single source of truth for version, author, org

### Added – Tests
- `tests/test_cross_build.py` — Cross-build invariant suite:
  - 28 canonical NSDT vectors spanning all 10 SAP stages + edge cases
  - 12 invariant checks per build: stage range, posterior sum, posterior length, trap energy bounds, entropy non-negativity, canonical stage name, valid arc, valid risk level, expected stage range, serialisation round-trip, Lyapunov presence (Build 3 & 4), unified field presence (Build 4)
  - 2 cross-build agreement tests (all builds must agree on valid range and energy bounds)

### Added – Benchmarking
- `benchmark.py` — Inference latency + memory benchmark:
  - Measures mean, median, p95, min, max ms and peak KB for each build
  - Console table + relative bar chart
  - `--n`, `--json`, `--builds` CLI flags
  - Registered as `luminark-benchmark` entry point

### Added – CI/CD
- `.github/workflows/ci.yml` — GitHub Actions pipeline:
  - Matrix: Python 3.10, 3.11, 3.12
  - Jobs: `test` (Build 4 property tests + cross-build invariant tests), `lint` (ruff, advisory), `benchmark` (N=20 quick pass)
  - Triggers on push to main/dev and pull requests to main

### Added – Packaging
- `pyproject.toml` — Modern Python packaging:
  - `pip install -e .` installs the `luminark` package
  - Optional extras: `[api]`, `[tests]`, `[yaml]`, `[all]`
  - Dynamic version from `luminark.version.__version__`
  - pytest config: testpaths includes both `tests/` and `build4_unified_field/`

### Added – Examples
- `examples/quickstart.py` — Single-file demo: NSDT → analysis across 3 builds, extras, JSON round-trip, presets, JSON schema
- `examples/cross_build_comparison.py` — Side-by-side comparison table across all 10 stage territories