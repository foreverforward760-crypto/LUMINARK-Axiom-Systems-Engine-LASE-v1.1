# LUMINARK Kairos – Therapeutic SAP Engine (v1.0)

**Kairos (καιρός)** – the opportune, critical moment for change.

## Purpose
Therapeutic, coaching, and consciousness-development applications where regression, oscillation, and voluntary choice are meaningful — not errors.

## Key Differences from Overwatch Strict
- **Stage 8 → 7 regression is allowed** — interpreted as refusal of dissolution
- **Stage 5 is a free choice point** — full adjacency, can return to any prior stage
- **Outputs include** therapeutic notes, somatic invitations, trickster wisdom, coaching responses, and journal prompts
- **Session tracking** remembers per-user stage history, detects cynical loops (7↔8 oscillation)

## Files
| File | Purpose |
|---|---|
| `sap_kairos_geometry.py` | Permissive adjacency, polyvagal states, trickster wisdom per stage |
| `sap_kairos_bayesian.py` | Soft Bayesian inference, therapeutic notes, Stage 8 release protocol |
| `sap_kairos_session.py` | Per-user session tracking, regression counting, cynical loop detection |
| `sap_energy_layer.py` | Shared energy field (identical to Overwatch) |
| `api_kairos.py` | FastAPI: /analyze /history /reset /health |

## Running
```bash
pip install -r requirements.txt
uvicorn api_kairos:app --host 0.0.0.0 --port 8002
```

## Example
```bash
curl -X POST http://localhost:8002/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "system_id": "client_001",
    "nsdt": [6.2, 4.5, 7.8, 3.2, 5.1],
    "allow_regression": true,
    "journal_entry": "I feel stuck and scared."
  }'
```

## Stage 5 — The Kairos Moment
At Stage 5, the user has full agency. The engine will not enforce irreversibility. Every path is available. The therapeutic output reflects this: *"No wrong choice — only honest choice."*
