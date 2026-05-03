"""
================================================================================
 LUMINARK UNIFIED API — main.py  v12.1 (Ω-9 Integration)
 Meridian Axiom Alignment Technologies (MAAT)
 Framework: Stanfield's Axiom of Perpetuity (SAP) | 10 Stages
 Author: Richard L. Stanfield | LuminarkMeridian@gmail.com
 Confidential — Proprietary IP
================================================================================

 FastAPI application exposing both LUMINARK engines:
   - OVERWATCH PRIME ULTRA  (infrastructure intelligence)
   - CONSCIOUSNESS ENGINE OMEGA  (human/organizational intelligence)
   - Ω-9 ENGINE  (fractal addressing, inversion oscillator, action classification)

 Endpoints:  23 REST endpoints across 6 categories
 Auth:       API key via X-API-Key header
 Docs:       http://localhost:8000/docs  (Swagger UI)
================================================================================
"""

import os
import secrets
import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ── Import LUMINARK Engines ──────────────────────────────────────────────────
import LatestLUMINARK_OVERWATCH_PRIME_ULTRA as ultra_engine
import LUMINARK_CONSCIOUSNESS_ENGINE_OMEGA as omega_engine

# ── Ω-9 classes (added by APPLY_LUMINARK_PATCHES.py to ULTRA engine) ─────────
try:
    FractalAddress       = ultra_engine.FractalAddress
    InversionOscillator  = ultra_engine.InversionOscillator
    compute_omega9_action = ultra_engine.compute_omega9_action
    get_omega9_report    = ultra_engine.get_omega9_report
    _update_entropy_well = ultra_engine._update_entropy_well_ultra
    _ENTROPY_WELL        = ultra_engine._ENTROPY_WELL_ULTRA
    OMEGA9_AVAILABLE     = True
except AttributeError:
    OMEGA9_AVAILABLE = False
    # Minimal stubs — should not happen with patched engine
    class FractalAddress:
        def __init__(self, macro, micro, pico):
            self.macro, self.micro, self.pico = macro, micro, pico
        def to_label(self): return f"{self.macro}.{self.micro}.{self.pico}"
        def to_scalar(self): return self.macro + self.micro/10 + self.pico/100
        def to_729_index(self): return self.macro*81 + self.micro*9 + self.pico
    def compute_omega9_action(s, ts, addr, inv): return {"action": "NAVIGATE", "diagnosis": "Stub"}
    def get_omega9_report(sid, stage, nsdt, ts): return {"error": "Ω-9 not patched"}
    def _update_entropy_well(sid, stage, harrowing): return 0.0
    _ENTROPY_WELL = {}

# ── App Config ───────────────────────────────────────────────────────────────
APP_VERSION = "12.1.0"
API_KEY = os.getenv("LUMINARK_API_KEY", "dev-key-change-in-production")

app = FastAPI(
    title="LUMINARK Unified API",
    description=(
        "Meridian Axiom Alignment Technologies (MAAT) — "
        "Predictive Stage Intelligence powered by Stanfield's Axiom of Perpetuity (SAP). "
        "Infrastructure + Consciousness + Ω-9 Fractal Engine via unified REST interface."
    ),
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# ── Engine Instances ─────────────────────────────────────────────────────────
nsdt_engine          = ultra_engine.NSDataTEngine()
consciousness_engine = omega_engine.ConsciousnessEngine()
stage_library        = omega_engine.StageLibrary()
corporate_analyzer   = omega_engine.CorporateConsciousnessAnalyzer()
meridian_adapter     = omega_engine.MERIDIANAdapter()

request_count = {"total": 0, "by_endpoint": {}}


# ── Ω-9 Helper ────────────────────────────────────────────────────────────────
def _omega9(system_id: str, stage: int, nsdt_dict: dict, trap_raw: float) -> dict:
    """Compute full Ω-9 report for any analysis response."""
    return get_omega9_report(system_id, stage, nsdt_dict, trap_raw)


# ── Auth ─────────────────────────────────────────────────────────────────────
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


# ── Request counter middleware ────────────────────────────────────────────────
@app.middleware("http")
async def count_requests(request: Request, call_next):
    request_count["total"] += 1
    path = request.url.path
    request_count["by_endpoint"][path] = request_count["by_endpoint"].get(path, 0) + 1
    return await call_next(request)


# ── Pydantic Models ──────────────────────────────────────────────────────────

class NSDTInput(BaseModel):
    complexity:   float = Field(5.0, ge=0.0, le=10.0)
    stability:    float = Field(5.0, ge=0.0, le=10.0)
    tension:      float = Field(5.0, ge=0.0, le=10.0)
    adaptability: float = Field(5.0, ge=0.0, le=10.0)
    coherence:    float = Field(5.0, ge=0.0, le=10.0)

class SPATInput(BaseModel):
    complexity:   float = Field(5.0, ge=0.0, le=10.0)
    stability:    float = Field(5.0, ge=0.0, le=10.0)
    tension:      float = Field(5.0, ge=0.0, le=10.0)
    adaptability: float = Field(5.0, ge=0.0, le=10.0)
    coherence:    float = Field(5.0, ge=0.0, le=10.0)
    life_vector:  str   = Field("growth")

class CompanyInput(BaseModel):
    company:               str   = Field(...)
    ticker:                str   = Field(...)
    revenue_growth_pct:    float = Field(10.0)
    operating_margin:      float = Field(15.0)
    debt_to_equity:        float = Field(1.0)
    rd_spend_pct:          float = Field(5.0)
    employee_turnover_pct: float = Field(15.0)
    cash_burn_rate:        float = Field(0.0)
    market_cap_change_yoy: float = Field(0.0)
    leadership_changes_12m: int  = Field(0)

class PortfolioInput(BaseModel):
    win_rate_pct:           float = Field(50.0)
    avg_hold_days:          float = Field(30.0)
    top3_concentration_pct: float = Field(40.0)
    max_drawdown_pct:       float = Field(15.0)
    leverage_ratio:         float = Field(1.0)
    plan_overrules_30d:     int   = Field(2)
    portfolio_correlation:  float = Field(0.5)

class AIScanInput(BaseModel):
    text:       str = Field(...)
    user_stage: int = Field(4, ge=0, le=9)

class Omega9AddressRequest(BaseModel):
    system_id:    str   = Field("default")
    complexity:   float = Field(5.0, ge=0.0, le=10.0)
    stability:    float = Field(5.0, ge=0.0, le=10.0)
    tension:      float = Field(5.0, ge=0.0, le=10.0)
    adaptability: float = Field(5.0, ge=0.0, le=10.0)
    coherence:    float = Field(5.0, ge=0.0, le=10.0)
    stage:        int   = Field(5, ge=0, le=9)

class Omega9ActionRequest(BaseModel):
    system_id:   str   = Field("default")
    stage:       int   = Field(5, ge=0, le=9)
    trap_score:  float = Field(0.0, ge=0.0, le=10.0)
    complexity:  float = Field(5.0, ge=0.0, le=10.0)
    stability:   float = Field(5.0, ge=0.0, le=10.0)
    tension:     float = Field(5.0, ge=0.0, le=10.0)
    adaptability:float = Field(5.0, ge=0.0, le=10.0)
    coherence:   float = Field(5.0, ge=0.0, le=10.0)

class ContainerRuleInput(BaseModel):
    content_digit:     int = Field(..., ge=1, le=9)
    container_digit:   int = Field(..., ge=1, le=9)
    current_sap_stage: Optional[int] = Field(None, ge=0, le=9)


# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "operational",
        "platform": "LUMINARK Unified API",
        "company": "Meridian Axiom Alignment Technologies (MAAT)",
        "author": "Richard L. Stanfield",
        "contact": "LuminarkMeridian@gmail.com",
        "framework": "Stanfield's Axiom of Perpetuity (SAP) v4.1",
        "version": APP_VERSION,
        "engines": {
            "ultra": "LUMINARK OVERWATCH PRIME ULTRA v12.0",
            "omega": "LUMINARK CONSCIOUSNESS ENGINE OMEGA v12.0",
        },
        "omega9_available": OMEGA9_AVAILABLE,
        "timestamp": datetime.datetime.now().isoformat(),
    }


@app.get("/metrics", tags=["System"], dependencies=[Depends(verify_api_key)])
async def get_metrics():
    return {
        "total_requests": request_count["total"],
        "by_endpoint": request_count["by_endpoint"],
        "entropy_wells_active": len(_ENTROPY_WELL),
        "timestamp": datetime.datetime.now().isoformat(),
    }


# ══════════════════════════════════════════════════════════════════════════════
# INFRASTRUCTURE ENDPOINTS  (ULTRA Engine)
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/infra/analyze", tags=["Infrastructure"], dependencies=[Depends(verify_api_key)])
async def analyze_infrastructure(data: NSDTInput, system_id: str = "default"):
    """Full infrastructure stage analysis with Ω-9 fractal report included."""
    nsdt = ultra_engine.NSDataT(
        complexity=data.complexity, stability=data.stability,
        tension=data.tension, adaptability=data.adaptability, coherence=data.coherence,
    )
    stage    = nsdt_engine.calculate_stage(nsdt)
    micro    = nsdt_engine.calculate_micro_position(nsdt, stage)
    trap     = nsdt_engine.calculate_trap_score(nsdt, stage)
    inversion = nsdt_engine.check_inversion_principle(nsdt, stage)
    stage_info = ultra_engine.STAGE_LABELS.get(stage, ("UNKNOWN", "", ""))
    nsdt_dict  = data.dict()
    omega9     = _omega9(system_id, stage, nsdt_dict, trap.raw_score)

    return {
        "system_id": system_id,
        "stage": {"value": stage, "name": stage_info[0],
                  "description": stage_info[1], "detail": stage_info[2]},
        "micro_position": round(micro, 3),
        "trap_score": {"raw": trap.raw_score, "normalized": trap.normalized_score,
                       "rigidity_index": trap.rigidity_index, "risk_level": trap.risk_level},
        "inversion": inversion,
        "omega9": omega9,
        "input": nsdt_dict,
        "timestamp": datetime.datetime.now().isoformat(),
    }


@app.get("/api/infra/stages", tags=["Infrastructure"])
async def get_infra_stages():
    return {
        "framework": "Stanfield's Axiom of Perpetuity (SAP) — Infrastructure",
        "stages": {str(k): {"name": v[0], "description": v[1], "detail": v[2]}
                   for k, v in ultra_engine.STAGE_LABELS.items()},
    }


@app.get("/api/infra/validate", tags=["Infrastructure"], dependencies=[Depends(verify_api_key)])
async def validate_historical():
    """Run historical hurricane + Uri validation suite."""
    validator = ultra_engine.HurricaneValidationEngine()
    return validator.run_all_validations()


@app.post("/api/infra/container-rule", tags=["Infrastructure"], dependencies=[Depends(verify_api_key)])
async def container_rule(cr: ContainerRuleInput):
    engine = ultra_engine.InfraContainerRuleEngine()
    return engine.analyze(cr.content_digit, cr.container_digit, cr.current_sap_stage)


# ══════════════════════════════════════════════════════════════════════════════
# CONSCIOUSNESS ENDPOINTS  (OMEGA Engine)
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/consciousness/analyze", tags=["Consciousness"], dependencies=[Depends(verify_api_key)])
async def analyze_consciousness(data: SPATInput, system_id: str = "default"):
    """Full consciousness stage analysis with Ω-9 fractal report included."""
    spat = omega_engine.SPATVector(
        complexity=data.complexity, stability=data.stability,
        tension=data.tension, adaptability=data.adaptability,
        coherence=data.coherence, life_vector=data.life_vector,
    )
    stage    = consciousness_engine.calculate_stage(spat)
    micro    = consciousness_engine.calculate_micro_position(spat, stage)
    trap     = consciousness_engine.calculate_trap_score(spat, stage)
    inversion = consciousness_engine.check_inversion_principle(spat, stage)
    meta     = omega_engine.STAGE_METADATA.get(stage, {})
    content  = stage_library.get_stage_content(stage, data.life_vector)
    nsdt_dict = data.dict()
    omega9   = _omega9(system_id, stage, nsdt_dict, trap.get("raw", 0.0))

    return {
        "system_id": system_id,
        "stage": {"value": stage, "name": meta.get("name", ""), "subtitle": meta.get("subtitle", ""),
                  "geometry": meta.get("geometry", ""), "polyvagal": meta.get("polyvagal", "")},
        "micro_position": round(micro, 3),
        "trap_score": trap,
        "inversion": inversion,
        "stage_content": content,
        "resonance_369": spat.check_resonance(),
        "omega9": omega9,
        "input": nsdt_dict,
        "timestamp": datetime.datetime.now().isoformat(),
    }


@app.get("/api/consciousness/stages", tags=["Consciousness"])
async def get_consciousness_stages():
    return {
        "framework": "Stanfield's Axiom of Perpetuity (SAP) — Consciousness",
        "stages": {str(k): v for k, v in omega_engine.STAGE_METADATA.items()},
        "resonance_369": omega_engine.RESONANCE_369,
    }


@app.post("/api/consciousness/corporate", tags=["Consciousness"], dependencies=[Depends(verify_api_key)])
async def analyze_corporate(data: CompanyInput):
    payload = data.dict()
    name   = payload.pop("company")
    ticker = payload.pop("ticker")
    return corporate_analyzer.analyze_company(name, ticker, payload)


@app.post("/api/consciousness/portfolio", tags=["Consciousness"], dependencies=[Depends(verify_api_key)])
async def analyze_portfolio(data: PortfolioInput):
    return meridian_adapter.analyze_portfolio_behavior(data.dict())


@app.post("/api/consciousness/ai-scan", tags=["Consciousness"], dependencies=[Depends(verify_api_key)])
async def scan_ai_content(data: AIScanInput):
    guardian = omega_engine.LuminarkGuardian()
    return guardian.scan_content(data.text, data.user_stage)


@app.get("/api/consciousness/family-dashboard", tags=["Consciousness"], dependencies=[Depends(verify_api_key)])
async def family_dashboard(members: str = "Rick,Member2,Member3"):
    guardian = omega_engine.LuminarkGuardian()
    return guardian.get_family_status_mock([m.strip() for m in members.split(",") if m.strip()])


# ══════════════════════════════════════════════════════════════════════════════
# Ω-9 ENGINE ENDPOINTS  (NEW — v12.1)
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/omega9/address", tags=["Ω-9 Engine"], dependencies=[Depends(verify_api_key)])
async def omega9_address(req: Omega9AddressRequest):
    """
    Compute the 729-point FractalAddress (macro.micro.pico) from an NSDT vector + stage.
    Returns scalar, 729-index, and spherical coordinates.
    """
    nsdt = ultra_engine.NSDataT(
        complexity=req.complexity, stability=req.stability,
        tension=req.tension, adaptability=req.adaptability, coherence=req.coherence,
    )
    raw_micro = (nsdt.coherence - nsdt.tension + 9) / 18
    micro = max(1, min(9, round(raw_micro * 8) + 1))
    raw_pico  = (nsdt.stability + nsdt.adaptability) / 20.0
    pico  = max(1, min(9, round(raw_pico * 8) + 1))
    addr  = FractalAddress(macro=req.stage, micro=micro, pico=pico)

    return {
        "system_id":    req.system_id,
        "stage":        req.stage,
        "fractal_address": addr.to_label(),
        "scalar":       round(addr.to_scalar(), 3),
        "index_729":    addr.to_729_index(),
        "macro":        addr.macro,
        "micro":        addr.micro,
        "pico":         addr.pico,
        "timestamp":    datetime.datetime.now().isoformat(),
    }


@app.post("/api/omega9/action", tags=["Ω-9 Engine"], dependencies=[Depends(verify_api_key)])
async def omega9_action(req: Omega9ActionRequest):
    """
    Classify the Ω-9 action for a system:
    NAVIGATE | HARROWING_TRIGGERED | RELEASE_AND_TRANSMIT
    Includes InversionOscillator profile and Entropy Well level.
    """
    raw_micro = (req.coherence - req.tension + 9) / 18
    micro = max(1, min(9, round(raw_micro * 8) + 1))
    raw_pico = (req.stability + req.adaptability) / 20.0
    pico = max(1, min(9, round(raw_pico * 8) + 1))
    addr = FractalAddress(macro=req.stage, micro=micro, pico=pico)
    inversion = InversionOscillator.calculate_tension(req.stage)
    action = compute_omega9_action(req.stage, req.trap_score, addr, inversion)
    entropy_cost = _update_entropy_well(req.system_id, req.stage, action["harrowing"])
    entropy_level = _ENTROPY_WELL.get(req.system_id, 0.0)

    return {
        "system_id":      req.system_id,
        "action":         action["action"],
        "harrowing":      action["harrowing"],
        "reset_address":  action.get("reset_address"),
        "diagnosis":      action["diagnosis"],
        "polarity":       action["polarity"],
        "fractal_address": addr.to_label(),
        "inversion_profile": inversion,
        "entropy_well_level": entropy_level,
        "entropy_cost_applied": entropy_cost if action["harrowing"] else 0.0,
        "contraindicated": action.get("contraindicated"),
        "indicated":       action.get("indicated"),
        "timestamp":       datetime.datetime.now().isoformat(),
    }


@app.get("/api/omega9/report/{system_id}", tags=["Ω-9 Engine"], dependencies=[Depends(verify_api_key)])
async def omega9_report(system_id: str):
    """
    Retrieve accumulated Ω-9 state for a system: entropy well level,
    last known fractal address, harrowing history. Requires prior /api/omega9/action calls.
    """
    entropy_level = _ENTROPY_WELL.get(system_id, 0.0)
    if entropy_level == 0.0 and system_id not in _ENTROPY_WELL:
        return {
            "system_id": system_id,
            "message": "No Ω-9 data yet. Submit a /api/omega9/action request first.",
            "entropy_well_level": 0.0,
            "omega9_available": OMEGA9_AVAILABLE,
        }
    return {
        "system_id": system_id,
        "entropy_well_level": entropy_level,
        "omega9_available": OMEGA9_AVAILABLE,
        "note": "Use /api/omega9/action for full per-call Ω-9 report with fractal address.",
        "timestamp": datetime.datetime.now().isoformat(),
    }


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/admin/rotate-key", tags=["Admin"], dependencies=[Depends(verify_api_key)])
async def rotate_api_key():
    global API_KEY
    new_key = secrets.token_urlsafe(32)
    API_KEY = new_key
    return {"message": "API key rotated", "new_key": new_key,
            "warning": "Save this key — it cannot be retrieved again"}


# ── Startup banner ────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    print("=" * 72)
    print("  LUMINARK Unified API — v12.1 with Ω-9 Engine")
    print("  Meridian Axiom Alignment Technologies (MAAT)")
    print("  Richard L. Stanfield | LuminarkMeridian@gmail.com")
    print(f"  Ω-9 available: {OMEGA9_AVAILABLE}")
    print(f"  Docs: http://localhost:{os.getenv('PORT', '8000')}/docs")
    print("=" * 72)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
