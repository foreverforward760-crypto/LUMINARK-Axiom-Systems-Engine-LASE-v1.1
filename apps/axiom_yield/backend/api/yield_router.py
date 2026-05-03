"""
backend/api/yield.py – Axiom Yield Broker Calculation Endpoint

POST /calculate — computes Axiom Yield Score from FMCSA + ELD telemetry.

CORRECTIONS APPLIED (vs submitted document):
  [6] NSDTBuilder and InversionAnalyzer now exist in backend/luminark/ —
      adapter modules written from scratch consistent with LUMINARK engine.
  [7] YieldRequest Pydantic model was missing — defined here.
  [8,9] Yield score formula now uses LUMINARK [0,10] scale consistently.
      tension and coherence are [0,10]; formula normalises explicitly.
"""

import logging
import time
from typing import Optional, Dict, Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.luminark.nsdt_calculator import NSDTBuilder
from backend.luminark.inversion_analyzer import InversionAnalyzer
from backend.luminark.sap_energy_layer import (
    SAPStage,
    evaluate_trap,
    evaluate_vessel_of_grounding_trap,
    evaluate_dynamo_of_will_bifurcation,
)
from backend.luminark.sap_signal_translator import build_api_response
from backend.eld.connectors import ELDClient

router = APIRouter()
logger = logging.getLogger(__name__)


# ── Request model ─────────────────────────────────────────────────────────────

class FMCSASnapshot(BaseModel):
    """FMCSA carrier / route data."""
    route_stops:              int   = Field(3,    ge=1,  le=50)
    route_volatility:         float = Field(30.0, ge=0,  le=100)
    recovery_debt:            float = Field(20.0, ge=0,  le=100)
    communication_coherence:  float = Field(70.0, ge=0,  le=100)
    on_time_pct:              float = Field(85.0, ge=0,  le=100)


class StateFlags(BaseModel):
    """State DOT / Florida supplemental data."""
    lane_entropy:    float = Field(30.0, ge=0, le=100)
    reroute_options: int   = Field(3,    ge=0, le=10)
    market_pressure: float = Field(40.0, ge=0, le=100)


class YieldRequest(BaseModel):
    """
    FIX [7]: YieldRequest was used in yield.py but never defined or imported.
    Defined here with all required fields.
    """
    carrier_id:      str
    driver_id:       Optional[str]  = None
    eld_provider:    Optional[str]  = None   # "samsara" | "motive" | "geotab"
    eld_api_key:     Optional[str]  = None
    fmcsa_snapshot:  FMCSASnapshot  = Field(default_factory=FMCSASnapshot)
    state_flags:     StateFlags     = Field(default_factory=StateFlags)


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.post("/calculate")
async def calculate_yield(request: YieldRequest):
    """
    Calculate Axiom Yield Score for a carrier/driver.

    Returns
    -------
    yield_score       : float [0–100] — higher = safer, more reliable
    sap_stage         : int [0–9]     — current SAP stage
    is_trap           : bool          — whether a trap condition is active
    trap_reason       : str | None    — human-readable trap explanation
    recommended_action: str           — logistics action to take
    eld_status        : str           — "live" | "degraded_fallback"
    eld_evasive       : bool          — True if HOS fraud signature detected
    confidence        : float [0–1]   — stage classification confidence
    """
    eld_data: Dict[str, Any] = {}
    eld_status = "no_eld"

    # 1. Fetch ELD data with graceful fallback to FMCSA averages
    if request.eld_provider and request.driver_id and request.eld_api_key:
        try:
            client   = ELDClient(request.eld_provider, request.eld_api_key)
            eld_data = await client.get_hos(request.driver_id)
            eld_status = "live"
            logger.info(f"ELD live data received for driver {request.driver_id}")

        except NotImplementedError as e:
            logger.warning(
                f"ELD provider '{request.eld_provider}' not implemented: {e}. "
                f"Falling back to FMCSA historicals."
            )
            eld_data   = {"error": "not_implemented", "is_evasive": False}
            eld_status = "degraded_fallback"

        except Exception as e:
            logger.warning(
                f"ELD connection failed for driver {request.driver_id}: {e}. "
                f"Falling back to FMCSA historicals."
            )
            eld_data   = {"error": "connection_failed", "is_evasive": False}
            eld_status = "degraded_fallback"

    # 2. Build NSDT vector from all available data
    nsdt = NSDTBuilder.from_fmcsa_and_eld(
        fmcsa_data=request.fmcsa_snapshot.dict(),
        state_data=request.state_flags.dict(),
        eld_data=eld_data,
    )

    # 3. Run SAP engine — stage classification + trap detection
    state = InversionAnalyzer.compute_stage(nsdt)

    # 4. Route through energy layer + signal translator
    #    NSDT values are [0,10] from NSDTBuilder; scale to [0,100] for energy layer
    nsdt_dict_100 = {
        "complexity":   nsdt.complexity * 10.0,
        "stability":    nsdt.stability  * 10.0,
        "tension":      nsdt.tension    * 10.0,
        "adaptability": nsdt.adaptability * 10.0,
        "coherence":    nsdt.coherence  * 10.0,
    }
    sap_stage = SAPStage(state.stage.value)
    trap_result = evaluate_trap(sap_stage, nsdt_dict_100, build="overwatch")

    engine_output = {
        "stage":          trap_result.stage.value,
        "trap_energy":    trap_result.trap_energy,
        "stage5_path":    trap_result.path,
        "stage8_chamber": trap_result.chamber_active,
    }
    signal = build_api_response(
        engine_output,
        carrier_id=request.carrier_id,
        build="overwatch",
    )

    # 5. Merge with operational metadata (ELD status, driver ID, NSDT internals)
    return {
        **signal,
        "driver_id":          request.driver_id,
        "confidence":         state.confidence,
        "eld_status":         eld_status,
        "eld_evasive":        eld_data.get("is_evasive", False),
        "nsdt": {
            "complexity":   nsdt.complexity,
            "stability":    nsdt.stability,
            "tension":      nsdt.tension,
            "adaptability": nsdt.adaptability,
            "coherence":    nsdt.coherence,
        },
    }
