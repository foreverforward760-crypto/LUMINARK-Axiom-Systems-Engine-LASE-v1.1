"""
api_overwatch.py – LUMINARK Overwatch Strict API (v6.5)
Industrial SAP Engine: hard geometry, irreversible Stage 5 & 8.

INTEGRATED FEATURES (v8.1):
  /edge/analyze        – zero-dependency offline Lyapunov analysis (Wasm-ready)
  /oracle/sign         – HMAC-signed Trap Score for smart contract / escrow use
  /analyze             – full SAP analysis + UI guidance in every response
  /omega/publish       – cross-domain NSDT event publication to Omega Loop
  /trajectory/{id}     – posterior-driven trajectory prediction
  /health              – health check
"""

import math
import os
import time
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, List

from sap_datastructures import NSDataT, TrapScoreResult, TemporalSnapshot
from nsdt_engine_v65 import NSDataTEngine
from sap_edge_stub import EdgeAnalyzer
from sap_oracle import SAPOracle
from sap_ui_guidance import generate_ui_guidance

app = FastAPI(
    title="LUMINARK Overwatch Strict",
    description="Industrial SAP Engine v6.5 — edge-ready, oracle-signed, UI-guided",
    version="6.5.1",
)

engine      = NSDataTEngine()
edge        = EdgeAnalyzer()
_oracle_key = os.environb.get(b"LUMINARK_ORACLE_KEY", os.urandom(32))
oracle      = SAPOracle(_oracle_key, oracle_id="OVERWATCH-ORACLE")

# Optional Omega Loop — graceful fallback if luminark package not on path
try:
    import sys, os as _os
    sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
    from luminark.omega_loop import OmegaLoop, NSDTEvent, install_default_rules
    _omega = OmegaLoop(log=False)
    install_default_rules(_omega)
    OMEGA_AVAILABLE = True
except Exception:
    _omega = None
    OMEGA_AVAILABLE = False


class NSDTInput(BaseModel):
    system_id:    str   = "default"
    complexity:   float = Field(..., ge=0.0, le=10.0)
    stability:    float = Field(..., ge=0.0, le=10.0)
    tension:      float = Field(..., ge=0.0, le=10.0)
    adaptability: float = Field(..., ge=0.0, le=10.0)
    coherence:    float = Field(..., ge=0.0, le=10.0)
    domain:       str   = "power_grid"
    record:       bool  = True
    sign_output:  bool  = False

    @validator("complexity","stability","tension","adaptability","coherence",
               pre=True, each_item=False)
    def validate_finite(cls, v, field):
        if math.isnan(v) or math.isinf(v):
            raise ValueError(f"{field.name} must be finite")
        return v


class OmegaPublishInput(BaseModel):
    source_domain: str
    source_id:     str
    complexity:    float = Field(..., ge=0.0, le=10.0)
    stability:     float = Field(..., ge=0.0, le=10.0)
    tension:       float = Field(..., ge=0.0, le=10.0)
    adaptability:  float = Field(..., ge=0.0, le=10.0)
    coherence:     float = Field(..., ge=0.0, le=10.0)
    stage:         int   = Field(0, ge=0, le=9)
    trap_score:    float = Field(0.0, ge=0.0, le=100.0)


@app.post("/analyze")
def analyze(inp: NSDTInput):
    """Full SAP analysis with UI guidance embedded in every response."""
    nsdt = NSDataT(
        complexity=inp.complexity, stability=inp.stability,
        tension=inp.tension, adaptability=inp.adaptability,
        coherence=inp.coherence, domain=inp.domain,
    )
    result = engine.analyze_full(nsdt, inp.system_id)
    if inp.record:
        engine.record_snapshot(inp.system_id, nsdt)

    guidance = generate_ui_guidance(
        stage=result["stage"],
        entropy=result["entropy"],
        trap_energy=result["trap_energy"],
    )
    result["ui_guidance"] = guidance

    if inp.sign_output:
        signed = oracle.sign({
            "system_id":       inp.system_id,
            "stage":           result["stage"],
            "trap_normalized": result["trap_normalized"],
            "risk_level":      guidance["urgency"].upper(),
            "timestamp":       time.strftime("%Y-%m-%dT%H:%M:%S"),
        })
        result["oracle"] = {
            "signature":     signed["signature"],
            "abi_encoded":   signed["abi_encoded"],
            "contract_hint": signed["contract_hint"],
        }

    if OMEGA_AVAILABLE and _omega:
        _omega.publish(NSDTEvent(
            source_domain=inp.domain, source_id=inp.system_id,
            complexity=inp.complexity, stability=inp.stability,
            tension=inp.tension, adaptability=inp.adaptability,
            coherence=inp.coherence,
            stage=result["stage"], trap_score=result["trap_normalized"],
        ))

    return {"system_id": inp.system_id, **result}


@app.post("/edge/analyze")
def edge_analyze(inp: NSDTInput):
    """Zero-dependency Lyapunov analysis — identical to Wasm edge runtime output."""
    result = edge.analyze(
        inp.complexity, inp.stability, inp.tension,
        inp.adaptability, inp.coherence,
    )
    return {"system_id": inp.system_id, **result}


@app.post("/oracle/sign")
def oracle_sign(inp: NSDTInput):
    """HMAC-SHA256 signed Trap Score for smart contract / escrow integration."""
    nsdt = NSDataT(
        complexity=inp.complexity, stability=inp.stability,
        tension=inp.tension, adaptability=inp.adaptability,
        coherence=inp.coherence, domain=inp.domain,
    )
    result = engine.analyze_full(nsdt, inp.system_id)
    return oracle.sign({
        "system_id":       inp.system_id,
        "stage":           result["stage"],
        "trap_normalized": result["trap_normalized"],
        "risk_level":      "UNKNOWN",
        "timestamp":       time.strftime("%Y-%m-%dT%H:%M:%S"),
    })


@app.post("/omega/publish")
def omega_publish(inp: OmegaPublishInput):
    """Publish an NSDT event to the Omega Loop cross-domain router."""
    if not OMEGA_AVAILABLE or not _omega:
        raise HTTPException(503, "Omega Loop not available")
    from luminark.omega_loop import NSDTEvent
    dispatches = _omega.publish(NSDTEvent(
        source_domain=inp.source_domain, source_id=inp.source_id,
        complexity=inp.complexity, stability=inp.stability,
        tension=inp.tension, adaptability=inp.adaptability,
        coherence=inp.coherence, stage=inp.stage, trap_score=inp.trap_score,
    ))
    return {"dispatches": dispatches, "count": len(dispatches)}


@app.post("/trajectory/{system_id}")
def trajectory(system_id: str):
    history = engine.get_history(system_id)
    if len(history) < 2:
        return {"system_id": system_id, "error": "insufficient history"}
    return {"system_id": system_id, **engine.predict_trajectory(history)}


@app.get("/health")
def health():
    return {
        "status":          "ok",
        "engine":          "LUMINARK Overwatch Strict",
        "version":         "6.5.1",
        "edge_ready":      True,
        "oracle_ready":    True,
        "omega_available": OMEGA_AVAILABLE,
    }
