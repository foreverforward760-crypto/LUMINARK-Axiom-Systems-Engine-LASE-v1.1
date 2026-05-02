"""
api_overwatch_v7.py – LUMINARK Active Defense API (v7 + Spore)
FastAPI server: Lyapunov analysis, OctoSpore vulnerability scanning.

INTEGRATED FEATURES (v8.1):
  /analyze              – v7 analysis + UI guidance + optional oracle signing
  /defense/action       – Lyapunov-based defense action
  /vulnerability/scan   – OctoSpore trace scan
  /edge/analyze         – offline zero-dependency edge analysis
  /oracle/sign          – HMAC-signed output for smart contract integration
  /omega/publish        – publish NSDT event to cross-domain Omega Loop
  /health               – health check
"""

import math
import os
import time
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import List, Optional

from nsdt_engine_v7 import NSDataTEngine, NSDataT
from octo_spore_v1 import OctoSpore, SporeConfig
from sap_edge_stub import EdgeAnalyzer
from sap_oracle import SAPOracle
from sap_ui_guidance import generate_ui_guidance

app = FastAPI(
    title="LUMINARK Active Defense",
    description="v7 Lyapunov + OctoSpore + Edge + Oracle + Omega Loop",
    version="7.1.0",
)

engine      = NSDataTEngine()
spore       = OctoSpore(SporeConfig(max_spore_depth=5, honey_pot_enabled=True))
edge        = EdgeAnalyzer()
_oracle_key = os.environb.get(b"LUMINARK_ORACLE_KEY", os.urandom(32))
oracle      = SAPOracle(_oracle_key, oracle_id="DEFENSE-ORACLE")

# Optional Omega Loop
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


class TraceInput(BaseModel):
    system_id: str = "default"
    trace: List[List[float]] = Field(
        ..., description="Rows of [C,S,T,A,Coh,unix_timestamp] — min 3 rows"
    )
    @validator("trace")
    def validate_trace(cls, v):
        if len(v) < 3:
            raise ValueError("trace must have at least 3 rows")
        for i, row in enumerate(v):
            if len(row) < 6:
                raise ValueError(f"row {i} needs 6 values: [C,S,T,A,Coh,timestamp]")
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
    """Full v7 analysis: stage, Lyapunov V, defense action, energy gradient + UI guidance."""
    nsdt   = NSDataT(complexity=inp.complexity, stability=inp.stability,
                     tension=inp.tension, adaptability=inp.adaptability,
                     coherence=inp.coherence, domain=inp.domain)
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
            "risk_level":      result.get("lyapunov", {}).get("recommended_action", "UNKNOWN"),
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


@app.post("/defense/action")
def defense_action(inp: NSDTInput):
    """Lyapunov-based defense action recommendation."""
    nsdt   = NSDataT(complexity=inp.complexity, stability=inp.stability,
                     tension=inp.tension, adaptability=inp.adaptability,
                     coherence=inp.coherence, domain=inp.domain)
    action = engine.recommend_defense_action(nsdt, inp.system_id)
    return {"system_id": inp.system_id, "recommended_action": action}


@app.post("/vulnerability/scan")
def vulnerability_scan(inp: TraceInput):
    """OctoSpore: Lyapunov scan + red-team + Stage 5 duality + honey-pot."""
    trace_arr = np.array([[r[0],r[1],r[2],r[3],r[4]] for r in inp.trace])
    ts_arr    = np.array([r[5] for r in inp.trace])
    return spore.run_defense_cycle(inp.system_id, trace_arr, ts_arr)


@app.post("/edge/analyze")
def edge_analyze(inp: NSDTInput):
    """Zero-dependency Lyapunov analysis — Wasm-identical output."""
    result = edge.analyze(inp.complexity, inp.stability, inp.tension,
                          inp.adaptability, inp.coherence)
    return {"system_id": inp.system_id, **result}


@app.post("/oracle/sign")
def oracle_sign(inp: NSDTInput):
    """HMAC-SHA256 signed output for smart contract / freight insurance integration."""
    nsdt   = NSDataT(complexity=inp.complexity, stability=inp.stability,
                     tension=inp.tension, adaptability=inp.adaptability,
                     coherence=inp.coherence, domain=inp.domain)
    result = engine.analyze_full(nsdt, inp.system_id)
    return oracle.sign({
        "system_id":       inp.system_id,
        "stage":           result["stage"],
        "trap_normalized": result["trap_normalized"],
        "risk_level":      result.get("lyapunov", {}).get("recommended_action", "UNKNOWN"),
        "timestamp":       time.strftime("%Y-%m-%dT%H:%M:%S"),
    })


@app.post("/omega/publish")
def omega_publish(inp: OmegaPublishInput):
    """Publish NSDT event to Omega Loop cross-domain router."""
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


@app.get("/health")
def health():
    return {
        "status":          "ok",
        "engine":          "LUMINARK Active Defense",
        "version":         "7.1.0",
        "edge_ready":      True,
        "oracle_ready":    True,
        "omega_available": OMEGA_AVAILABLE,
    }
