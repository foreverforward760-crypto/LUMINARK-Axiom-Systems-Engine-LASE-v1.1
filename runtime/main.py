"""
================================================================================
 LUMINARK UNIFIED MASTER API — main.py
 Meridian Axiom Alignment Technologies (MAAT)
 Framework: Stanfield's Axiom of Perpetuity (SAP) | 10 Stages
 Author: Richard L. Stanfield | LuminarkMeridian@gmail.com
 Confidential — Proprietary IP
================================================================================

 FastAPI server exposing both engines:
   • LUMINARK CONSCIOUSNESS ENGINE OMEGA  (human / organizational intelligence)
   • LUMINARK OVERWATCH PRIME ULTRA       (infrastructure / industrial intelligence)

 Usage:
   pip install fastapi uvicorn
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload

 Endpoints:
   GET  /                              → version + engine status
   POST /omega/assess_individual       → personal SAP assessment
   POST /omega/assess_company          → corporate consciousness analysis
   POST /omega/assess_portfolio        → financial portfolio behavior
   POST /omega/scan_ai_content         → AI content safety scan
   GET  /omega/family_dashboard        → family overwatch (demo data)
   GET  /omega/session_trajectory      → session trajectory metrics
   POST /omega/yunus_scan              → Yunus Protocol humility check
   GET  /omega/harrowing_status        → Harrowing Protocol restoration state
   POST /overwatch/analyze             → infrastructure system analysis
   POST /overwatch/container_rule      → Container Rule / Digit Vessel
   GET  /overwatch/validate            → historical hurricane validation
   GET  /overwatch/trajectory/{id}     → system trajectory metrics
   POST /overwatch/yunus_scan          → infrastructure report humility check
   GET  /overwatch/harrowing_status/{id} → system restoration state
   GET  /health                        → liveness probe

 Author : Richard L. Stanfield / Meridian Axiom Alignment Technologies (MAAT)
 Version: 1.2 — April 2026 | v13.0 Systemic Sovereignty Update
================================================================================
"""

import sys
import os

# ── ensure local engine files are importable ───────────────────────────────────
# When deployed, place both engine .py files in the same directory as main.py.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
except ImportError:
    raise ImportError(
        "FastAPI not installed. Run: pip install fastapi uvicorn"
    )


# ── lazy-load engines so the API starts even if one has an issue ───────────────
_omega = None
_overwatch = None


def get_omega():
    global _omega
    if _omega is None:
        from LUMINARK_CONSCIOUSNESS_ENGINE_OMEGA import LuminarkConsciousnessEngineOmega
        _omega = LuminarkConsciousnessEngineOmega()
    return _omega


def get_overwatch():
    global _overwatch
    if _overwatch is None:
        # Try the latest consolidated version first, fall back to original
        try:
            from LatestLUMINARK_OVERWATCH_PRIME_ULTRA import LuminarkOverwatchPrimeUltra
        except ImportError:
            from LUMINARK_OVERWATCH_PRIME_ULTRA import LuminarkOverwatchPrimeUltra
        _overwatch = LuminarkOverwatchPrimeUltra()
    return _overwatch


# ── FastAPI app ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="LUMINARK Unified API",
    description=(
        "Meridian Axiom Alignment Technologies (MAAT) — "
        "Predictive stage intelligence for human consciousness, "
        "organizational health, and physical infrastructure. "
        "Powered by Stanfield's Axiom of Perpetuity (SAP). "
        "v13.0: Geometric Tumbling Law | Inversion Principle | Cynical Loop (8→7→8) Detector."
    ),
    version="1.2.0",
    contact={"name": "Richard L. Stanfield", "email": "LuminarkMeridian@gmail.com"},
    license_info={"name": "Proprietary — Meridian Axiom Alignment Technologies (MAAT)"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── request / response models ─────────────────────────────────────────────────

class SPATInput(BaseModel):
    """5-dimensional NSDT input vector. All values 0.0–10.0."""
    complexity:   float = Field(..., ge=0.0, le=10.0, description="System complexity / load")
    stability:    float = Field(..., ge=0.0, le=10.0, description="Operational stability")
    tension:      float = Field(..., ge=0.0, le=10.0, description="Internal stress / tension")
    adaptability: float = Field(..., ge=0.0, le=10.0, description="Capacity to adapt / respond")
    coherence:    float = Field(..., ge=0.0, le=10.0, description="Cross-subsystem alignment")
    life_vector:  Optional[str] = Field("growth", description="Domain context (growth/finances/health/infra)")


class CompanyInput(BaseModel):
    name:                   str   = Field(..., description="Company name")
    ticker:                 str   = Field(..., description="Ticker symbol or identifier")
    revenue_growth_pct:     float = Field(10.0, description="Revenue growth %")
    operating_margin:       float = Field(15.0, description="Operating margin %")
    debt_to_equity:         float = Field(1.0,  description="Debt-to-equity ratio")
    rd_spend_pct:           float = Field(5.0,  description="R&D as % of revenue")
    employee_turnover_pct:  float = Field(15.0, description="Annual employee turnover %")
    cash_burn_rate:         float = Field(0.0,  description="Cash burn (0=positive CF, 10=extreme)")
    market_cap_change_yoy:  float = Field(0.0,  description="Market cap change YoY %")
    leadership_changes_12m: int   = Field(0,    description="Leadership changes in last 12 months")


class PortfolioInput(BaseModel):
    win_rate_pct:           float = Field(50.0, description="Win rate %")
    avg_hold_days:          float = Field(30.0, description="Average hold time in days")
    top3_concentration_pct: float = Field(40.0, description="% assets in top 3 positions")
    max_drawdown_pct:       float = Field(15.0, description="Maximum drawdown %")
    leverage_ratio:         float = Field(1.0,  description="Leverage multiplier (1.0 = no leverage)")
    plan_overrules_30d:     int   = Field(2,    description="Times investor broke own rules in 30 days")
    portfolio_correlation:  float = Field(0.5,  description="Portfolio correlation (0=diversified, 1=all same)")


class AIScanInput(BaseModel):
    text:       str = Field(..., description="Text to analyze for AI safety / manipulation")
    user_stage: int = Field(4, ge=0, le=9, description="Operator's current SAP stage (0–9)")


class InfraInput(BaseModel):
    system_id:    str   = Field(..., description="Unique system identifier")
    system_type:  str   = Field("generic", description="System type (power_grid, water, vehicle, etc.)")
    complexity:   float = Field(..., ge=0.0, le=10.0)
    stability:    float = Field(..., ge=0.0, le=10.0)
    tension:      float = Field(..., ge=0.0, le=10.0)
    adaptability: float = Field(..., ge=0.0, le=10.0)
    coherence:    float = Field(..., ge=0.0, le=10.0)


class ContainerRuleInput(BaseModel):
    content_digit:   int          = Field(..., ge=1, le=9, description="Inner Drive / Load digit (1–9)")
    container_digit: int          = Field(..., ge=1, le=9, description="Outer Form / Capacity digit (1–9)")
    current_sap_stage: Optional[int] = Field(None, ge=0, le=9, description="Current SAP stage for cross-validation")


class YunusScanInput(BaseModel):
    text:      str   = Field(..., description="Text or health report to scan for arrogance / overconfidence")
    stage:     int   = Field(5, ge=0, le=9, description="Current SAP stage (0–9)")
    coherence: float = Field(5.0, ge=0.0, le=10.0, description="Current coherence (0–10) — used for False Light detection")


class OverwatchYunusScanInput(BaseModel):
    text:           str   = Field(..., description="Health report or text to scan for arrogance / False Light")
    system_id:      str   = Field("default", description="Infrastructure system ID for context")
    stage:          int   = Field(5, ge=0, le=9, description="Current SAP stage (0–9)")
    nsdt_coherence: float = Field(5.0, ge=0.0, le=10.0, description="Current coherence (0–10)")


# ── utility ────────────────────────────────────────────────────────────────────

def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _wrap(data: Any, endpoint: str) -> dict:
    return {"timestamp": _ts(), "endpoint": endpoint, "data": data}


# ── root ───────────────────────────────────────────────────────────────────────

@app.get("/", summary="API root — version and engine status")
async def root():
    omega_ok = True
    ow_ok = True
    try:
        get_omega()
    except Exception:
        omega_ok = False
    try:
        get_overwatch()
    except Exception:
        ow_ok = False

    return _wrap({
        "api": "LUMINARK Unified API v1.1",
        "company": "Meridian Axiom Alignment Technologies (MAAT)",
        "framework": "Stanfield's Axiom of Perpetuity (SAP)",
        "contact": "LuminarkMeridian@gmail.com",
        "engines": {
            "CONSCIOUSNESS_ENGINE_OMEGA": "OK" if omega_ok else "ERROR — check engine file",
            "OVERWATCH_PRIME_ULTRA":      "OK" if ow_ok    else "ERROR — check engine file",
        },
        "docs": "/docs",
    }, "/")


@app.get("/health", summary="Liveness probe for Docker/K8s")
async def health():
    return {"status": "ok", "timestamp": _ts()}


# ══════════════════════════════════════════════════════════════════════════════
# OMEGA ENDPOINTS — Consciousness Intelligence
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/omega/assess_individual",
          summary="Personal SAP stage assessment from SPAT vector")
async def assess_individual(spat: SPATInput):
    try:
        result = get_omega().assess_individual(spat.dict())
        return _wrap(result, "/omega/assess_individual")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/omega/assess_company",
          summary="Corporate consciousness analysis")
async def assess_company(company: CompanyInput):
    try:
        payload = company.dict()
        name = payload.pop("name")
        ticker = payload.pop("ticker")
        result = get_omega().assess_company(name, ticker, payload)
        return _wrap(result, "/omega/assess_company")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/omega/assess_portfolio",
          summary="Financial portfolio behavioral analysis (MERIDIAN)")
async def assess_portfolio(portfolio: PortfolioInput):
    try:
        result = get_omega().assess_portfolio_behavior(portfolio.dict())
        return _wrap(result, "/omega/assess_portfolio")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/omega/scan_ai_content",
          summary="AI content safety scan (manipulation / Stage 8 permanence detection)")
async def scan_ai_content(payload: AIScanInput):
    try:
        result = get_omega().scan_ai_content(payload.text, payload.user_stage)
        return _wrap(result, "/omega/scan_ai_content")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/omega/family_dashboard",
         summary="Family Overwatch demo dashboard")
async def family_dashboard(members: str = "Rick,Daughter,Son"):
    try:
        member_list = [m.strip() for m in members.split(",") if m.strip()]
        result = get_omega().family_dashboard(member_list)
        return _wrap(result, "/omega/family_dashboard")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── OMEGA: Trajectory + Yunus + Harrowing ─────────────────────────────────────

@app.get("/omega/session_trajectory",
         summary="Session trajectory metrics — stage velocity, risk momentum, rigidity & recovery index")
async def omega_session_trajectory():
    """
    Returns trajectory analytics across all assess_individual() calls in this session:
    - stage_velocity: dS/dt rate of consciousness stage change
    - risk_momentum: change in TrapScore trend
    - rigidity_index: sustained Stage 7–8 fraction (0-1)
    - recovery_index: fraction of trap events resolved
    - trajectory_label: human-readable direction summary
    - harrowing_active: True if session is in critical trap
    - last_stable_stage: preserved Stage 4–6 restoration target

    Requires at least 2 prior /omega/assess_individual calls.
    """
    try:
        result = get_omega().get_session_trajectory()
        return _wrap(result, "/omega/session_trajectory")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/omega/yunus_scan",
          summary="Yunus Protocol: scan text for arrogance markers and False Light")
async def omega_yunus_scan(payload: YunusScanInput):
    """
    Runs the Yunus Protocol humility check on any text, AI output, or assessment:
    - Detects overconfidence language (YUNUS_STAGE8_TRAP, YUNUS_NO_WORST_CASE)
    - At Stage 8 + low coherence: detects False Light (collapse to Stage 5 recommended)
    - Returns output_safe flag, yunus_score (0-100), flags, recommended action
    """
    try:
        result = get_omega().scan_humility(payload.text, payload.stage, payload.coherence)
        return _wrap(result, "/omega/yunus_scan")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/omega/harrowing_status",
         summary="Harrowing Protocol status — last stable snapshot and restoration path")
async def omega_harrowing_status():
    """
    Returns Harrowing Protocol state for the current session:
    - harrowing_active: True if TrapScore > 0.90 or Stage 0 collapse
    - last_stable_stage: Stage 4–6 preserved as restoration baseline
    - restoration_action: specific restore directive
    - quarantine_risk: True if multiple trap events + high rigidity
    """
    try:
        result = get_omega().get_harrowing_status()
        return _wrap(result, "/omega/harrowing_status")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════════════════════════
# OVERWATCH ENDPOINTS — Infrastructure Intelligence
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/overwatch/analyze",
          summary="Infrastructure system SAP stage analysis")
async def overwatch_analyze(infra: InfraInput):
    try:
        payload = {
            "complexity":   infra.complexity,
            "stability":    infra.stability,
            "tension":      infra.tension,
            "adaptability": infra.adaptability,
            "coherence":    infra.coherence,
        }
        result = get_overwatch().analyze_system(
            infra.system_type, infra.system_id, payload
        )

        # v13.0: Inject Geometric Tumbling Law fields into response
        try:
            from LatestLUMINARK_OVERWATCH_PRIME_ULTRA import USSM_STAGES_ULTRA
        except ImportError:
            from LUMINARK_OVERWATCH_PRIME_ULTRA import USSM_STAGES_ULTRA

        stage = result.get("stage") or result.get("sap_stage", 0)
        stage_meta = USSM_STAGES_ULTRA.get(stage, {})
        result["tumbling_mechanism"]   = stage_meta.get("tumbling_mechanism", "")
        result["universal_attributes"] = stage_meta.get("universal_attributes", "")
        result["physical_stability"]   = stage_meta.get("physical_stability")
        result["conscious_stability"]  = stage_meta.get("conscious_stability")
        result["inversion_active"]     = (stage % 2 == 0)  # Even = physically stable / consciously unstable

        return _wrap(result, "/overwatch/analyze")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/overwatch/container_rule",
          summary="Container Rule / Digit Vessel analysis")
async def container_rule(cr: ContainerRuleInput):
    try:
        # Try latest engine first, fall back to original
        try:
            from LatestLUMINARK_OVERWATCH_PRIME_ULTRA import InfraContainerRuleEngine
        except ImportError:
            from LUMINARK_OVERWATCH_PRIME_ULTRA import InfraContainerRuleEngine
        engine = InfraContainerRuleEngine()
        result = engine.analyze(
            content_digit=cr.content_digit,
            container_digit=cr.container_digit,
            current_sap_stage=cr.current_sap_stage,
        )
        return _wrap(result, "/overwatch/container_rule")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/overwatch/validate",
         summary="Historical hurricane / grid validation (Milton + Helene + Uri)")
async def overwatch_validate():
    try:
        result = get_overwatch().run_historical_validation()
        return _wrap(result, "/overwatch/validate")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── OVERWATCH: Trajectory + Yunus + Harrowing ─────────────────────────────────

@app.get("/overwatch/trajectory/{system_id}",
         summary="Trajectory metrics for an infrastructure system — velocity, momentum, rigidity & recovery")
async def overwatch_trajectory(system_id: str):
    """
    Returns trajectory analytics across all analyze_system() calls for the given system_id:
    - stage_velocity: dS/dt rate of SAP stage change
    - risk_momentum: change in TrapScore trend
    - rigidity_index: sustained Stage 7–8 fraction (0-1)
    - recovery_index: fraction of trap events resolved
    - trajectory_label: human-readable direction summary
    - harrowing_active: True if system is in critical trap
    - last_stable_stage: preserved Stage 4–6 restoration target

    Requires at least 2 prior /overwatch/analyze calls for this system_id.
    """
    try:
        result = get_overwatch().get_trajectory_summary(system_id)
        return _wrap(result, f"/overwatch/trajectory/{system_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/overwatch/yunus_scan",
          summary="Yunus Protocol: scan infrastructure health report for arrogance and False Light")
async def overwatch_yunus_scan(payload: OverwatchYunusScanInput):
    """
    Runs the Yunus Protocol humility check on any infrastructure health report or text:
    - Detects overconfidence language (YUNUS_STAGE8_TRAP, YUNUS_NO_WORST_CASE)
    - At Stage 8 + low coherence: detects False Light (collapse to Stage 5 recommended)
    - Returns output_safe flag, yunus_score (0-100), flags, recommended action
    """
    try:
        result = get_overwatch().scan_report_humility(
            payload.text, payload.system_id, payload.stage, payload.nsdt_coherence
        )
        return _wrap(result, "/overwatch/yunus_scan")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/overwatch/harrowing_status/{system_id}",
         summary="Harrowing Protocol status — last stable snapshot and restoration path for an infrastructure system")
async def overwatch_harrowing_status(system_id: str):
    """
    Returns Harrowing Protocol state for the specified infrastructure system:
    - harrowing_active: True if TrapScore > 0.90 or Stage 0 collapse
    - last_stable_stage: Stage 4–6 preserved as restoration baseline
    - restoration_action: specific restore directive
    - quarantine_risk: True if multiple trap events + high rigidity
    """
    try:
        result = get_overwatch().get_harrowing_status(system_id)
        return _wrap(result, f"/overwatch/harrowing_status/{system_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/overwatch/cynical_loop",
          summary="Cynical Loop (8→7→8) detector — infrastructure Permanence Trap oscillation")
async def overwatch_cynical_loop(payload: dict):
    """
    Detects the 8→7→8 Cynical Loop in an infrastructure system's stage history.

    The Cynical Loop is the primary failure mode of the ascending arc in physical systems:
    Stage 8 (Rigidity Risk / Octagon — Peak Consolidation) retreats to Stage 7 (Scaled /
    analysis/distillation mode) to avoid the dissolution demanded by Stage 9, then
    re-ascends to Stage 8 without genuine structural transformation.

    This oscillation is physically invisible to conventional monitoring — the system
    LOOKS optimal at both Stage 7 and Stage 8. The 8→7→8 pattern provides predictive
    lead-time on system failure unavailable to any other model.

    POST body: {"stage_sequence": [int, ...], "system_id": "optional-string"}
    """
    try:
        try:
            from LatestLUMINARK_OVERWATCH_PRIME_ULTRA import TemporalStateEngine
        except ImportError:
            from LUMINARK_OVERWATCH_PRIME_ULTRA import TemporalStateEngine

        stage_sequence = payload.get("stage_sequence", [])
        system_id = payload.get("system_id", "unknown")

        if not stage_sequence:
            raise ValueError("stage_sequence must be a non-empty list of integers (0–9).")

        engine = TemporalStateEngine()
        # Populate history with provided sequence for analysis
        for s in stage_sequence:
            engine.record_state(
                stage=int(s),
                adaptability=0.3,  # conservative default for detection purposes
                rigidity=0.7,
                coherence=0.5,
            )

        result = engine._detect_cynical_loop([int(s) for s in stage_sequence])
        result["system_id"] = system_id
        result["stage_sequence_length"] = len(stage_sequence)
        return _wrap(result, "/overwatch/cynical_loop")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/overwatch/geometric_validate",
          summary="Geometric Trajectory Validator — enforce Tumbling Law on stage sequence")
async def overwatch_geometric_validate(payload: dict):
    """
    Validates a stage sequence against the Geometric Tumbling Law.

    Rules enforced:
      • Sequential transitions (n→n+1 or n→n-1) are geometrically valid.
      • Stage 5 (Pentagon) is a hard bifurcation — regression is a structural violation.
      • Skip-transitions (|Δstage| > 1) are Structural Anomalies that reduce confidence
        by 20 points per stage skipped.

    Returns: valid (bool), anomaly list, confidence_score (0–100).
    POST body: {"stage_sequence": [int, ...]}
    """
    try:
        try:
            from LatestLUMINARK_OVERWATCH_PRIME_ULTRA import validate_geometric_trajectory_ultra
        except ImportError:
            from LUMINARK_OVERWATCH_PRIME_ULTRA import validate_geometric_trajectory_ultra

        stage_sequence = payload.get("stage_sequence", [])
        if not stage_sequence:
            raise ValueError("stage_sequence must be a non-empty list of integers (0–9).")

        result = validate_geometric_trajectory_ultra([int(s) for s in stage_sequence])
        return _wrap(result, "/overwatch/geometric_validate")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/omega/cynical_loop",
          summary="Cynical Loop (8→7→8) detector — consciousness domain")
async def omega_cynical_loop(payload: dict):
    """
    Detects the 8→7→8 Cynical Loop in a consciousness or organisational assessment history.

    In conscious entities and organisations, Stage 8 (VESSEL OF GROUNDING — Permanence Trap)
    retreats to Stage 7 (LENS OF DISTILLATION — Analysis/Cynicism) to avoid the ego-dissolution
    of Stage 9, then re-ascends without genuine transformation. This pattern is the primary
    failure mode of the ascending arc for conscious substrates.

    POST body: {"stage_sequence": [int, ...]}
    """
    try:
        from LUMINARK_CONSCIOUSNESS_ENGINE_OMEGA import ConsciousnessTemporalEngine

        stage_sequence = payload.get("stage_sequence", [])
        if not stage_sequence:
            raise ValueError("stage_sequence must be a non-empty list of integers (0–9).")

        engine = ConsciousnessTemporalEngine()
        for s in stage_sequence:
            engine.record_assessment(stage=int(s), adaptability=0.3, rigidity=0.7, coherence=0.5)

        result = engine._detect_cynical_loop([int(s) for s in stage_sequence])
        return _wrap(result, "/omega/cynical_loop")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/omega/geometric_validate",
          summary="Geometric Trajectory Validator — consciousness domain")
async def omega_geometric_validate(payload: dict):
    """
    Validates a consciousness stage sequence against the Geometric Tumbling Law.
    POST body: {"stage_sequence": [int, ...]}
    """
    try:
        from LUMINARK_CONSCIOUSNESS_ENGINE_OMEGA import validate_geometric_trajectory

        stage_sequence = payload.get("stage_sequence", [])
        if not stage_sequence:
            raise ValueError("stage_sequence must be a non-empty list of integers (0–9).")

        result = validate_geometric_trajectory([int(s) for s in stage_sequence])
        return _wrap(result, "/omega/geometric_validate")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/overwatch/stage_profile/{stage}",
         summary="Full stage profile — universal + tumbling mechanism (substrate-aware)")
async def overwatch_stage_profile(stage: int, substrate: str = "physical_system"):
    """
    Returns the full SAP stage metadata for a given stage (0–9).
    For physical_system substrate: returns universal_attributes + tumbling_mechanism only.
    For conscious_entity substrate: returns full profile including observer_attributes.

    Query params:
      stage     — integer 0–9
      substrate — 'physical_system' (default) or 'conscious_entity'
    """
    if stage < 0 or stage > 9:
        raise HTTPException(status_code=400, detail="Stage must be 0–9.")
    try:
        try:
            from LatestLUMINARK_OVERWATCH_PRIME_ULTRA import USSM_STAGES_ULTRA
        except ImportError:
            from LUMINARK_OVERWATCH_PRIME_ULTRA import USSM_STAGES_ULTRA

        profile = dict(USSM_STAGES_ULTRA.get(stage, {}))
        # Suppress observer_attributes for physical systems (Substrate-Independent Claim)
        if substrate == "physical_system":
            profile.pop("observer_attributes", None)

        return _wrap({
            "stage": stage,
            "substrate": substrate,
            "profile": profile,
            "tumbling_mechanism": profile.get("tumbling_mechanism", ""),
            "universal_attributes": profile.get("universal_attributes", ""),
            "physical_stability": profile.get("physical_stability"),
            "conscious_stability": profile.get("conscious_stability"),
            "inversion_principle": (
                "Even stages (0,2,4,6,8): Physically Stable / Consciously Unstable. "
                "Odd stages (1,3,5,7,9): Physically Unstable / Consciously Stable."
                if stage % 2 == 0 else
                "Odd stage: Physically Unstable / Consciously Stable."
            ),
        }, f"/overwatch/stage_profile/{stage}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── error handler ──────────────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "path": str(request.url)},
    )


# ── dev runner ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
