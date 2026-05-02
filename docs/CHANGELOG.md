# CHANGELOG

All notable changes to **LuminarkHybridEngine** are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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

---

## [0.4.0] – Build 4: Unified Field v8

### Added – `build4_unified_field/`
- `sap_unified_field.py` — Unified Field equation U = α·G + β·P + γ·E + δ·L:
  - G: geometric violation mass (fraction of posterior on adjacency-forbidden stages)
  - P: cross-entropy (negative log-posterior of dominant stage)
  - E: expected trap energy (Σ p(s)·trap_energy(s,x))
  - L: Lyapunov value (w_H·H + w_E·E + w_v·v²)
  - `gradient()`: real central finite-difference gradient ∇U (corrected from zeros stub)
  - `components()`: breakdown dict for debugging and logging
- `nsdt_engine_v8.py` — NSDataTEngineV8 inheriting v7:
  - `unified_field_value(NSDataT)` — NSDataT interface
  - `unified_field_raw(ndarray)` — array interface for test harness / optimisation
  - `unified_field_gradient(ndarray)` — ∇U
  - `unified_field_components(ndarray)` — component breakdown
  - `analyse_v8()` — full v7 analysis + unified field augmentation
- `test_harness_v8.py` — 14 property-based tests (Hypothesis):
  - Posterior, energy, Lyapunov, unified field, gradient self-consistency, geometry contracts
- `kairos_integration.py` — KairosClient + KairosRedTeamAdapter:
  - Timeout (10 s), error handling, 3-failure abort, max_steps cap
  - Gradient-ascent red-teaming of Kairos engine
  - Explicit numpy→list conversion for JSON safety

### Fixed (10 flaws from prior AI session)
1. test_harness_v8.py: Tests used NSDataT interface against raw-array engine → added `unified_field_raw()`
2. test_harness_v8.py: `test_lyapunov_decrease` was vacuous → tests real DAMPEN (energy×0.8, velocity→0)
3. test_harness_v8.py: Gradient test compared against zeros stub → Richardson extrapolation consistency check
4. sap_unified_field.py: `gradient()` returned `np.zeros(5)` → real finite-difference gradient
5. sap_unified_field.py: `_geometric_violation()` used supervised label vs prev_stage → uses adjacency matrix on posterior mass
6. nsdt_engine_v8.py: `datetime` not imported → NameError → added `import datetime`
7. nsdt_engine_v8.py: Single mixed interface → split `unified_field_value()` + `unified_field_raw()`
8. nsdt_engine_v8.py: Non-functional skeleton ("methods omitted") → proper v7 inheritance
9. kairos_integration.py: ndarray passed to `requests.post()` → TypeError → explicit float list conversion
10. kairos_integration.py: No timeout, unbounded HTTP calls → 10 s timeout, try/except, abort, cap

---

## [0.3.0] – Build 3: Active Defense v7

### Added – `build3_active_defense/`
- `sap_lyapunov.py` — Lyapunov stability controller (V = w_H·H + w_E·E + w_v·v²) with defense actions (HOLD / DAMPEN / INTERVENE / BREAK_PATTERN) and `LyapunovVulnerabilityScanner`
- `nsdt_engine_v7.py` — NSDataTEngine with Lyapunov layer (extends v6.5, drop-in compatible)
- `octo_spore_v1.py` — Active adversarial spore: Lyapunov instability scanning + honey-pot inversion
- `kairos_redteam.py` — Red-team simulation targeting strict engine
- `api_overwatch_v7.py` — FastAPI v7 endpoint (port 8001)

---

## [0.2.0] – Build 2: Kairos Therapeutic Engine

### Added – `build2_kairos/`
- `sap_kairos_geometry.py` — Permissive geometry (regression allowed, free choice at Stage 5)
- `sap_kairos_bayesian.py` — Therapeutic posterior with regression prior
- `sap_kairos_session.py` — Session tracking with journal entries and somatic invitations
- `api_kairos.py` — FastAPI endpoint (port 8002) with coaching response generation

---

## [0.1.0] – Build 1: Overwatch Strict v6.5

### Added – `build1_overwatch_strict/`
- `sap_geometry_engine.py` — Hard geometric transition law, adjacency matrix, Stage 5 point of no return, Stage 8 terminal branch, weighted centroid distances, micro-position projection
- `sap_energy_layer.py` — Trap energy field (Stage 3, 5, 7, 8 potentials), expected energy, finite-difference gradient, logit modulation
- `sap_constrained_bayesian.py` — Geometric-masked Bayesian posterior with softmax + temperature
- `sap_datastructures.py` — NSDataT, TrapScoreResult, TemporalSnapshot
- `nsdt_engine_v65.py` — Full inference engine: stage, micro-position, trap score, inversion check, history, trajectory prediction
- `api_overwatch.py` — FastAPI endpoint (port 8000)

---

## SAP Constitutional Constants (never modified)

| Stage | Canonical Name |
|-------|---------------|
| 0 | PLENARA |
| 1 | SPARK OF NAVIGATION |
| 2 | FORGE OF POLARITY |
| 3 | ENGINE OF EXPRESSION |
| 4 | CRUCIBLE OF EQUILIBRIUM |
| 5 | DYNAMO OF WILL |
| 6 | NEXUS OF HARMONY |
| 7 | LENS OF DISTILLATION |
| 8 | VESSEL OF GROUNDING |
| 9 | TRANSPARENCY OF THE GUIDE |

Torus cycles 0→9→0. Stage 5: point of no return forward. Stage 8: terminal branch (Illusion of Permanence, 1.45× amplifier). These constants are embedded in all builds and must never be renamed, abbreviated, or altered by any AI or implementation.

*LUMINARK™ — Meridian Axiom Alignment Technologies (MAAT) — Richard Stanfield*
