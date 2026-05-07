"""
luminark/api/classify.py
────────────────────────
LASE SDK — Classification Router v1.0
Stanfield's Axiom of Perpetuity (SAP) Framework

POST /classify   — classify any NSDT vector through the SAP engine
GET  /health     — liveness probe
GET  /schema     — return the canonical NSDT JSON Schema

Authentication:
    Header: X-LASE-API-KEY: <key>
    Set env var LASE_API_KEY (required) and LASE_DEMO_KEY (optional public key).

Rate limiting:
    Default 120 requests/minute per IP via slowapi.
    Override with env var LASE_RATE_LIMIT (e.g. "60/minute").

© 2026 Richard L. Stanfield / Meridian Axiom Alignment Technologies LLC
Contact: LuminarkMeridian@gmail.com
"""

from __future__ import annotations

import datetime
import logging
import os
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from luminark.sap_types import (
    NSDTVector,
    SAP_STAGE_NAMES,
    SAP_STAGE_ARCS,
    NSDT_JSON_SCHEMA,
)
from luminark.engine_factory import EngineFactory
from luminark.sap_energy_layer import (
    SAPStage,
    evaluate_trap,
    VESSEL_OF_GROUNDING_CHAMBER_A,
    VESSEL_OF_GROUNDING_CHAMBER_B,
)

from .schemas import (
    ClassifyRequest,
    ClassifyResponse,
    BifurcationResult,
    TrapResult,
    RiskLevel,
    AlertColor,
    ErrorResponse,
)

logger    = logging.getLogger(__name__)
router    = APIRouter(prefix="/v1", tags=["classify"])
limiter   = Limiter(key_func=get_remote_address)

# ── Auth ──────────────────────────────────────────────────────────────────────

_LASE_API_KEY  = os.getenv("LASE_API_KEY",  "")
_LASE_DEMO_KEY = os.getenv("LASE_DEMO_KEY", "lase-demo-public")
_RATE_LIMIT    = os.getenv("LASE_RATE_LIMIT", "120/minute")


def _verify_api_key(x_lase_api_key: Optional[str] = Header(None)) -> str:
    """Validate API key from X-LASE-API-KEY header."""
    valid_keys = {k for k in (_LASE_API_KEY, _LASE_DEMO_KEY) if k}
    if not x_lase_api_key or x_lase_api_key not in valid_keys:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing X-LASE-API-KEY header.",
        )
    return x_lase_api_key


# ── Internal helpers ───────────────────────────────────────────────────────────

def _nsdt_input_to_vector(nsdt_in, domain: str) -> NSDTVector:
    """Convert Pydantic NSDTInput → canonical NSDTVector ([0, 10] scale)."""
    return NSDTVector(
        complexity=nsdt_in.complexity,
        stability=nsdt_in.stability,
        tension=nsdt_in.tension,
        adaptability=nsdt_in.adaptability,
        coherence=nsdt_in.coherence,
        source="lase_api",
        domain=domain,
    )


def _nsdt_to_energy_dict(nsdt: NSDTVector) -> dict:
    """Convert NSDTVector ([0, 10]) → energy layer dict ([0, 100])."""
    return {
        "complexity":   nsdt.complexity   * 10.0,
        "stability":    nsdt.stability    * 10.0,
        "tension":      nsdt.tension      * 10.0,
        "adaptability": nsdt.adaptability * 10.0,
        "coherence":    nsdt.coherence    * 10.0,
    }


def _inversion_active(stage: int) -> bool:
    """
    Tumbling Inversion Principle:
      Even stages (0,2,4,6,8): Physically Stable / Consciously Unstable
      Odd stages  (1,3,5,7,9): Physically Unstable / Consciously Stable
      Stage 9: exception (both resolved)
    Returns True when the inversion tension is active (not resolved).
    """
    if stage == 9:
        return False   # Stage 9 — both dimensions resolved
    return True        # All other stages carry inversion tension


def _build_response(
    req: ClassifyRequest,
    result,           # SAPAnalysisResult from engine_factory
    trap_eval,        # EvaluationResult from sap_energy_layer
) -> ClassifyResponse:
    """Assemble the locked ClassifyResponse from engine and energy outputs."""

    stage_idx  = result.stage
    stage_name = SAP_STAGE_NAMES[stage_idx]
    stage_arc  = SAP_STAGE_ARCS.get(stage_idx, "neutral")

    # ── Stage 5 bifurcation ───────────────────────────────────────────────────
    bifurcation: Optional[BifurcationResult] = None
    if stage_idx == 5:
        path_map = {"A": "advance", "B": "retreat", "C": "freeze"}
        raw_path = trap_eval.path or "C"
        bifurcation = BifurcationResult(
            path        = path_map.get(raw_path, "freeze"),
            path_energy = trap_eval.trap_energy,
            lock_active = trap_eval.trap_active,
        )

    # ── Stage 8 dual-chamber trap ─────────────────────────────────────────────
    stage8_trap: Optional[TrapResult] = None
    if stage_idx == 8:
        chamber_raw = trap_eval.chamber_active  # 'A', 'B', or None
        chamber_label = None
        if chamber_raw == "A":
            chamber_label = VESSEL_OF_GROUNDING_CHAMBER_A   # "Illusion of Arrival"
        elif chamber_raw == "B":
            chamber_label = VESSEL_OF_GROUNDING_CHAMBER_B   # "Illusion of Permanence"

        stage8_trap = TrapResult(
            chamber_active     = chamber_label,
            amplifier_applied  = trap_eval.trap_energy > 0.0,
        )

    return ClassifyResponse(
        system_id             = req.system_id,
        build                 = req.build.value,
        domain                = req.domain,
        stage_index           = stage_idx,
        stage_name            = stage_name,
        stage_arc             = stage_arc,
        dominant_probability  = round(result.dominant_prob, 4),
        expected_stage        = round(result.expected_stage, 4),
        posterior             = [round(p, 4) for p in result.posterior],
        entropy               = round(result.entropy, 4),
        trap_energy           = round(trap_eval.trap_energy, 4),
        risk_level            = RiskLevel(result.risk_level),
        alert_color           = AlertColor(result.alert_color),
        stage_5_bifurcation   = bifurcation,
        stage_8_trap          = stage8_trap,
        inversion_active      = _inversion_active(stage_idx),
        geometric_valid       = result.geometric_valid,
        timestamp             = datetime.datetime.utcnow().isoformat() + "Z",
        lase_version          = "1.1.0",
    )


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.post(
    "/classify",
    response_model=ClassifyResponse,
    summary="Classify an NSDT vector through the SAP engine",
    description=(
        "Accepts a five-dimensional NSDT vector and returns the canonical SAP "
        "stage classification, trap energy, risk level, and stage-specific "
        "intelligence (Stage 5 bifurcation, Stage 8 dual-chamber trap).  "
        "The `stage_name` field always returns one of the 10 constitutional "
        "SAP stage names — drift is enforced impossible at the schema level."
    ),
    responses={
        200: {"model": ClassifyResponse},
        401: {"model": ErrorResponse, "description": "Invalid API key"},
        422: {"description": "Validation error (NSDT vector out of [0, 10] range)"},
        500: {"model": ErrorResponse, "description": "Engine error"},
    },
)
@limiter.limit(_RATE_LIMIT)
async def classify(
    request:  Request,
    body:     ClassifyRequest,
    api_key:  str = Depends(_verify_api_key),
) -> ClassifyResponse:
    """
    Classify any NSDT vector through the canonical SAP engine.

    The five NSDT axes (complexity, stability, tension, adaptability, coherence)
    must each be on the [0.0, 10.0] scale.  The engine normalises internally.

    Use the `build` parameter to select the appropriate domain preset:
    - `overwatch` — logistics, infrastructure, industrial systems
    - `kairos`    — therapeutic, human behavior, consciousness mapping
    - `defense`   — high-safety, critical systems, active defense
    - `unified`   — research, cross-domain exploratory analysis
    """
    try:
        # Build canonical NSDTVector
        nsdt_vec = _nsdt_input_to_vector(body.nsdt, body.domain)

        # Run classification through engine factory
        engine = EngineFactory.create(body.build.value)
        result = engine.analyze(nsdt_vec, system_id=body.system_id or "lase_sdk")

        # Run canonical energy layer (separate from classifier for auditability)
        sap_stage  = SAPStage(result.stage)
        nsdt_100   = _nsdt_to_energy_dict(nsdt_vec)
        trap_eval  = evaluate_trap(sap_stage, nsdt_100, build=body.build.value)

        response = _build_response(body, result, trap_eval)

        logger.info(
            "classify | system_id=%s build=%s stage=%d(%s) risk=%s energy=%.3f",
            body.system_id, body.build.value,
            response.stage_index, response.stage_name,
            response.risk_level, response.trap_energy,
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("classify error | system_id=%s error=%s", body.system_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail="Engine classification failed.")


@router.get(
    "/health",
    summary="Liveness probe",
    response_model=dict,
)
async def health() -> dict:
    """Returns OK if the API is running. No auth required."""
    return {
        "status":       "ok",
        "service":      "LASE SDK API",
        "version":      "1.1.0",
        "framework":    "Stanfield's Axiom of Perpetuity (SAP)",
        "author":       "Richard L. Stanfield / MAAT",
        "contact":      "LuminarkMeridian@gmail.com",
        "timestamp":    datetime.datetime.utcnow().isoformat() + "Z",
    }


@router.get(
    "/schema",
    summary="NSDT vector JSON Schema",
    response_model=dict,
)
async def nsdt_schema(api_key: str = Depends(_verify_api_key)) -> dict:
    """
    Returns the canonical JSON Schema for the NSDTVector input.
    Use this to validate your domain data before submitting to /classify.
    """
    return NSDT_JSON_SCHEMA
