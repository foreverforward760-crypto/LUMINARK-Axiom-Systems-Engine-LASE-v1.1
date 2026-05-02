# LUMINARK Active Defense – v7 + Spore

## Purpose
High-stakes autonomous defense for systems requiring active vulnerability hunting, adversarial simulation, and honey-pot inversion. Extends the strict industrial engine with a Lyapunov stability layer and an active adversarial spore module.

## Key Capabilities

| Capability | Description |
|---|---|
| **Lyapunov stability** | V(H, E, v) = w_H·H + w_E·E + w_v·v² governs defense action selection |
| **Vulnerability scanning** | LyapunovVulnerabilityScanner detects dV/dt > 0 windows in NSDT traces |
| **Kairos red-teaming** | KairosRedTeam chains energy-gradient exploits toward Stage 8 trap |
| **Stage 5 duality detection** | High stability + low coherence = hidden compromise signature |
| **Honey-pot inversion** | Compromised nodes isolated and flipped to decoy state |
| **Cynical loop detection** | 7↔8 oscillation triggers BREAK_PATTERN defense action |

## Files
| File | Purpose |
|---|---|
| `sap_geometry_engine.py` | Hard geometry — strict adjacency, irreversible Stage 5 & 8 |
| `sap_energy_layer.py` | Trap energy field and gradient |
| `sap_constrained_bayesian.py` | Bayesian posterior with geometric masking |
| `nsdt_engine_v7.py` | NSDataTEngine v7: v6.5 core + Lyapunov layer |
| `sap_lyapunov.py` | LyapunovController + LyapunovVulnerabilityScanner |
| `kairos_redteam.py` | KairosRedTeam adversarial exploit chain simulator |
| `octo_spore_v1.py` | OctoSpore + OctoMycelialChipV7 active defense cycle |
| `api_overwatch_v7.py` | FastAPI: /analyze /defense/action /vulnerability/scan /health |

## Running
```bash
pip install -r requirements.txt
uvicorn api_overwatch_v7:app --host 0.0.0.0 --port 8001
```

## API Endpoints

### POST `/analyze`
Full v7 NSDataT analysis. Returns stage, Lyapunov V, recommended action, energy gradient, inversion check.

### POST `/defense/action`
Lyapunov-based action recommendation only (`HOLD` / `DAMPEN` / `INTERVENE` / `BREAK_PATTERN`).

### POST `/vulnerability/scan`
OctoSpore full defense cycle over a submitted NSDT trace.

**Request body:**
```json
{
  "system_id": "node-001",
  "trace": [
    [5.2, 4.1, 6.3, 3.8, 7.0, 1700000000.0],
    [6.1, 3.9, 7.1, 3.2, 7.4, 1700000060.0]
  ]
}
```
Each row: `[complexity, stability, tension, adaptability, coherence, unix_timestamp]`

**Response includes:**
- `vulnerabilities_found` — count of dV/dt > threshold windows
- `spore_simulations` — exploit chain results per vulnerability
- `honey_pot_action` — whether a node was flipped to honey-pot

## Lyapunov Action Thresholds

| Condition | Action |
|---|---|
| Cynical loop detected (7↔8 oscillation) | `BREAK_PATTERN` |
| V > 5.0 | `INTERVENE` |
| V > 2.0 | `DAMPEN` |
| V ≤ 2.0 | `HOLD` |

## Relationship to Other Builds
- Uses the same strict geometry as **Build 1** (Overwatch Strict) — Stage 5 and 8 hard rules apply
- Red-team module uses Kairos fluid logic internally for exploit chaining, but the **defense system itself is strict**
