# Luminark Core Definition

Luminark is a 4-layer engineering system:
1. **Core**: deterministic inference kernel.
2. **Adapters**: domain-to-telemetry translators.
3. **Apps**: domain workflows composed from adapters + core.
4. **Interfaces**: API and monitoring dashboard.

Canonical telemetry contract uses 0-10 numeric values for:
- Severity (S)
- Turbulence (T)
- Adaptability (A)

Core formulas:
- Stage inference: Euclidean distance against NSDT centroids.
- TrapScore: `S × T × (1 − A/10) × stage_multiplier`.
- Consensus: weighted 3-evaluator score (Sigma/Delta/Omega).
