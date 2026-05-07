"""
api_kairos.py – LUMINARK Kairos Engine v1.1
SAP pattern intelligence API with session tracking and adaptive guidance.

SECURITY (v1.1):
  All POST endpoints require X-KAIROS-API-KEY header.
  Rate limited: 30 req/min per IP on analysis endpoints.

ENDPOINTS:
  /analyze       – SAP analysis + adaptive guidance + polyvagal UI guidance
  /edge/analyze  – offline Lyapunov edge analysis (zero-dependency, Wasm-ready)
  /history/{id}  – retrieve session snapshot history
  /reset/{id}    – clear session (requires auth)
  /health        – health check with feature flags

DISCLAIMER:
  LUMINARK Kairos is a pattern intelligence and systems analysis tool built on
  Stanfield's Axiom of Perpetuity (SAP). It is NOT clinical care, therapy,
  psychiatric treatment, or medical advice. It does not diagnose, treat, or
  monitor any health condition. If you are experiencing a mental health crisis,
  contact a licensed professional or call 988 (Suicide & Crisis Lifeline).
"""

import os
import time
import math
import numpy as np
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from pydantic import BaseModel, Field, validator
from typing import Optional
from dataclasses import asdict
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from sap_kairos_bayesian import KairosBayesian
from sap_kairos_session import KairosSession, KairosSnapshot
from sap_edge_stub import EdgeAnalyzer
from sap_ui_guidance import generate_ui_guidance

# ── Auth ──────────────────────────────────────────────────────────────────────
KAIROS_API_KEY  = os.getenv("KAIROS_API_KEY",  "kairos-key-change-me")
KAIROS_DEMO_KEY = os.getenv("KAIROS_DEMO_KEY", "kairos-demo-public")

NOT_CLINICAL_DISCLAIMER = (
    "MAAT pattern intelligence output. Not clinical care, therapy, or medical advice. "
    "Contact a licensed professional for mental health support. "
    "Crisis line: 988 (US Suicide & Crisis Lifeline)."
)


def verify_api_key(x_kairos_api_key: Optional[str] = Header(None)) -> str:
    if x_kairos_api_key not in (KAIROS_API_KEY, KAIROS_DEMO_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing X-KAIROS-API-KEY")
    return x_kairos_api_key


# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="LUMINARK Kairos Engine",
    version="1.1",
    description=(
        "SAP pattern intelligence with session tracking and adaptive guidance. "
        "NOT clinical care or medical advice. See /health for full disclaimer."
    ),
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_sessions: dict[str, KairosSession] = {}
edge = EdgeAnalyzer()

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


class KairosInput(BaseModel):
    system_id:        str
    nsdt:             list[float] = Field(..., min_items=5, max_items=5)
    allow_regression: bool        = True
    temperature:      float       = 0.7
    beta:             float       = 0.6
    journal_entry:    Optional[str] = None

    @validator("nsdt")
    def validate_nsdt(cls, v):
        for i, val in enumerate(v):
            if not isinstance(val, (int, float)):
                raise ValueError(f"nsdt[{i}] must be a number")
            if math.isnan(val) or math.isinf(val):
                raise ValueError(f"nsdt[{i}] is NaN or Inf")
            if val < 0.0 or val > 10.0:
                raise ValueError(f"nsdt[{i}] out of range 0-10")
        return v


class EdgeInput(BaseModel):
    system_id:    str   = "default"
    complexity:   float = Field(..., ge=0.0, le=10.0)
    stability:    float = Field(..., ge=0.0, le=10.0)
    tension:      float = Field(..., ge=0.0, le=10.0)
    adaptability: float = Field(..., ge=0.0, le=10.0)
    coherence:    float = Field(..., ge=0.0, le=10.0)


def get_or_create_session(system_id: str) -> KairosSession:
    if system_id not in _sessions:
        _sessions[system_id] = KairosSession(system_id, storage_backend="memory")
    return _sessions[system_id]


# ── Field rename map: clinical → neutral ──────────────────────────────────────
# These renames prevent regulatory misclassification as a clinical tool.
# Internal engine fields are preserved; only the API response layer is renamed.
_CLINICAL_RENAMES = {
    "therapeutic_note":  "guidance_note",
    "somatic_invitation": "body_signal",
    "trickster_wisdom":  "pattern_wisdom",
}


def _sanitize_response(result: dict) -> dict:
    """
    Rename clinical-sounding fields to neutral equivalents and inject disclaimer.
    Called on every /analyze response before returning to client.
    """
    for old_key, new_key in _CLINICAL_RENAMES.items():
        if old_key in result:
            result[new_key] = result.pop(old_key)
    result["disclaimer"] = NOT_CLINICAL_DISCLAIMER
    return result


def generate_decision_prompt(stage: int, trap_energy: float,
                              journal_entry: Optional[str]) -> str:
    """
    Generate stage-aware decision prompt from journal context.
    Renamed from generate_coaching_response to avoid clinical framing.
    These are pattern-based prompts, not therapeutic interventions.
    """
    if journal_entry:
        jl = journal_entry.lower()
        if "stuck" in jl or "can't move" in jl:
            return "The pattern shows low adaptability. What one variable could shift?"
        if "scared" in jl or "fear" in jl:
            return "High tension is present in the signal. What is the smallest next step?"
        if "angry" in jl:
            return "Tension is elevated. What underlying stability factor is being compressed?"
    if stage == 8:
        if trap_energy > 0.7:
            return (
                "High TrapScore detected. The Dual-Chamber Trap is active. "
                "What assumption could be released to reduce coherence deficit?"
            )
        return (
            "Stage 8 (VESSEL OF GROUNDING): The system is in the Dual-Chamber Trap. "
            "Acknowledge both Illusion of Arrival and Illusion of Permanence "
            "to activate the Gratitude Mechanism."
        )
    if stage == 7:
        return "Stage 7 (LENS OF DISTILLATION): Integration requires external signal input."
    if stage == 5:
        return (
            "Stage 5 (DYNAMO OF WILL): Bifurcation point active. "
            "ADVANCE, RETREAT, or FREEZE — coherence level determines the path."
        )
    return "Continue monitoring. Current stage is within expected SAP progression."


@app.post("/analyze")
@limiter.limit("30/minute")
def analyze_kairos(
    request: Request,
    inp: KairosInput,
    api_key: str = Depends(verify_api_key),
):
    """
    SAP pattern analysis with polyvagal UI guidance embedded in response.
    Requires X-KAIROS-API-KEY header.
    NOT clinical care or medical advice.
    """
    engine = KairosBayesian(
        temperature=inp.temperature,
        beta=inp.beta,
        allow_regression=inp.allow_regression,
    )
    session = get_or_create_session(inp.system_id)
    prev = session.get_previous_stage()
    if prev is not None:
        engine.previous_stage = prev

    x = np.array(inp.nsdt)
    result = engine.forward(x)

    guidance = generate_ui_guidance(
        stage=result["dominant_stage"],
        entropy=result["entropy"],
        trap_energy=result["trap_energy"],
        polyvagal_override=result.get("polyvagal"),
        duality_detected=(
            result["dominant_stage"] == 5 and
            inp.nsdt[1] > 7.0 and
            inp.nsdt[4] < 3.0
        ),
    )
    result["ui_guidance"] = guidance

    snapshot = KairosSnapshot(
        timestamp=time.time(),
        dominant_stage=result["dominant_stage"],
        expected_stage=result["expected_stage"],
        entropy=result["entropy"],
        trap_energy=result["trap_energy"],
        therapeutic_note=result.get("therapeutic_note", ""),
        somatic_invitation=result.get("somatic_invitation", ""),
        trickster_wisdom=result.get("trickster_wisdom", ""),
    )
    session.add_snapshot(snapshot)

    regression_count = session.get_regression_count()
    cynical_loop     = session.detect_cynical_loop()
    decision_prompt  = generate_decision_prompt(
        result["dominant_stage"], result["trap_energy"], inp.journal_entry
    )

    reflection_prompt = None
    if result["dominant_stage"] == 8:
        reflection_prompt = "What would shift if the current state were acknowledged as temporary?"
    elif result["dominant_stage"] == 7:
        reflection_prompt = "What pattern insight has not yet been shared with the system?"
    elif result["dominant_stage"] == 5:
        reflection_prompt = "What is the bifurcation variable — what would tip ADVANCE vs RETREAT?"

    if OMEGA_AVAILABLE and _omega:
        _omega.publish(NSDTEvent(
            source_domain="kairos",
            source_id=inp.system_id,
            complexity=inp.nsdt[0], stability=inp.nsdt[1],
            tension=inp.nsdt[2], adaptability=inp.nsdt[3],
            coherence=inp.nsdt[4],
            stage=result["dominant_stage"],
            trap_score=result["trap_energy"] * 100.0,
        ))

    result.update({
        "system_id": inp.system_id,
        "session": {
            "total_snapshots":         len(session.snapshots),
            "regression_count_8_to_7": regression_count,
            "cynical_loop_detected":   cynical_loop,
        },
        "decision_prompt":   decision_prompt,
        "reflection_prompt": reflection_prompt,
    })

    return _sanitize_response(result)


@app.post("/edge/analyze")
@limiter.limit("60/minute")
def edge_analyze(
    request: Request,
    inp: EdgeInput,
    api_key: str = Depends(verify_api_key),
):
    """Offline Lyapunov analysis — zero dependencies, Wasm-identical output."""
    result = edge.analyze(
        inp.complexity, inp.stability, inp.tension,
        inp.adaptability, inp.coherence,
    )
    return {"system_id": inp.system_id, **result, "disclaimer": NOT_CLINICAL_DISCLAIMER}


@app.get("/history/{system_id}")
@limiter.limit("60/minute")
def get_history(
    request: Request,
    system_id: str,
    limit: int = 20,
    api_key: str = Depends(verify_api_key),
):
    session = get_or_create_session(system_id)
    history = session.get_history(limit)
    return {"system_id": system_id, "history": [asdict(s) for s in history]}


@app.post("/reset/{system_id}")
@limiter.limit("20/minute")
def reset_session(
    request: Request,
    system_id: str,
    api_key: str = Depends(verify_api_key),
):
    if system_id in _sessions:
        del _sessions[system_id]
    return {"status": "reset", "system_id": system_id}


@app.get("/health")
def health():
    return {
        "status":          "ok",
        "engine":          "LUMINARK Kairos",
        "version":         "1.1",
        "active_sessions": len(_sessions),
        "edge_ready":      True,
        "omega_available": OMEGA_AVAILABLE,
        "auth_required":   True,
        "rate_limited":    True,
        "disclaimer":      NOT_CLINICAL_DISCLAIMER,
    }
