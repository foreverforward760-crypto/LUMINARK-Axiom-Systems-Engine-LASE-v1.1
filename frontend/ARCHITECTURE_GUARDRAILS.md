# Architecture Guardrails

1. Core modules must remain deterministic and side-effect free.
2. Adapters may transform source signals, but must output canonical telemetry.
3. Interfaces must expose numeric telemetry controls; avoid quiz/slider-only UX.
4. Alert matrix is fixed: NOMINAL → WATCH → WARNING → CRITICAL → EMERGENCY.
5. Text/AI-safety support remains in adapter layer (Ma'at + Guardian mapped to telemetry).
6. Signature matching must support lead-time forecasting metadata.
7. Tests must protect all core modules and core formulas.
