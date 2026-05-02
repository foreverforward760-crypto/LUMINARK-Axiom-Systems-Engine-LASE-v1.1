# LUMINARK Overwatch Strict – Industrial SAP Engine (v6.5)

## Purpose
Hard-geometry, industrial-grade SAP analysis for infrastructure, power grid, corporate, and AI safety applications.

## Key Properties
- **Stage 5 is irreversible** — once crossed, the system cannot return to stages 0–4
- **Stage 8 is a terminal branch** — can only hold or advance to Stage 9
- **No stage skipping** — transitions are clamped to ±1 step
- **Energy field** — trap potentials at stages 3, 5, 7, 8 computed as true physics-derived energy
- **Posterior-driven trajectory** — expected stage velocity and entropy delta power early warning

## Files
| File | Purpose |
|---|---|
| `sap_geometry_engine.py` | Adjacency matrix, centroids, micro-position projection |
| `sap_energy_layer.py` | Trap energy field and gradient |
| `sap_constrained_bayesian.py` | Bayesian posterior with geometric masking |
| `sap_datastructures.py` | NSDataT, TrapScoreResult, TemporalSnapshot |
| `nsdt_engine_v65.py` | Full NSDataTEngine v6.5 |
| `api_overwatch.py` | FastAPI server |

## Running
```bash
pip install -r requirements.txt
uvicorn api_overwatch:app --host 0.0.0.0 --port 8000
```

## Example
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"system_id": "grid-node-01", "complexity": 6.2, "stability": 4.1,
       "tension": 7.3, "adaptability": 3.8, "coherence": 5.9}'
```
