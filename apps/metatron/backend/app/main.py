"""
SAP Co-Pilot Companion App – FastAPI backend entry point.

Endpoints
─────────
POST /link/       Exchange Plaid public token for access token
POST /analyze/    Full portfolio analysis (SAP + Behavior + Threat Intel)
GET  /stage/{n}   Return SAP stage description for stage n (0-9)
GET  /health      Liveness probe
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from .luminark_core import LuminarkAI
from .plaid_client import PlaidClient

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sap_copilot")

app = FastAPI(
    title="SAP Co-Pilot Companion App",
    description=(
        "LUMINARK AI – Stanfields Axiom of Perpetuity stage engine, "
        "SAP user behaviour analysis, and cybersecurity threat intelligence."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Singletons
# ---------------------------------------------------------------------------

ai_engine = LuminarkAI()
plaid = PlaidClient()

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class LinkRequest(BaseModel):
    public_token: str = Field(..., description="Plaid public token from Link UI")


class LinkResponse(BaseModel):
    status: str
    access_token: str


class AnalyzeRequest(BaseModel):
    access_token: str = Field(..., description="Plaid access token")
    notes: Optional[List[str]] = Field(
        default=[], description="User trading journal entries"
    )


class HoldingAnalysis(BaseModel):
    ticker: str
    stage: int
    description: str
    physical_stability: float
    conscious_stability: float
    inversion_type: str


class UserAnalysis(BaseModel):
    user_stage: int
    trap_risk: bool
    trap_keyword_hits: int
    uncertainty_awareness: bool
    diversification_score: float
    holding_period_score: float
    description: str


class ThreatAlert(BaseModel):
    ticker: str
    threat_type: str
    severity: str
    pattern_description: str
    raw_mention: str


class AnalysisResponse(BaseModel):
    overall_stage: int
    overall_description: str
    holdings: List[HoldingAnalysis]
    user: UserAnalysis
    threats: List[ThreatAlert]
    recommendations: List[str]


class StageInfo(BaseModel):
    stage: int
    description: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health", tags=["Meta"])
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/link/", response_model=LinkResponse, tags=["Plaid"])
async def link_account(req: LinkRequest):
    """
    Exchange a Plaid Link public token for a permanent access token.
    Store the returned access_token securely (encrypted) per user.
    """
    try:
        access_token = plaid.exchange_public_token(req.public_token)
        logger.info("Plaid account linked successfully.")
        return LinkResponse(status="linked", access_token=access_token)
    except Exception as exc:
        logger.error("Plaid link failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Plaid error: {exc}") from exc


@app.post("/analyze/", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze(req: AnalyzeRequest):
    """
    Full portfolio analysis:
    1. Fetch holdings & transactions from Plaid
    2. Run SAP Stage Engine on each asset (Brain)
    3. Analyse user behaviour for cognitive traps (Heart)
    4. Scan for external threats per ticker (Body)
    5. Return consolidated LUMINARK report with recommendations
    """
    try:
        holdings = plaid.get_holdings(req.access_token)
        transactions = plaid.get_transactions(req.access_token)
    except Exception as exc:
        logger.error("Failed to fetch Plaid data: %s", exc)
        raise HTTPException(status_code=502, detail=f"Plaid data fetch failed: {exc}") from exc

    user_data: Dict[str, Any] = {
        "holdings": holdings,
        "transactions": transactions,
        "notes": req.notes or [],
    }

    try:
        result = ai_engine.analyze_portfolio(user_data)
    except Exception as exc:
        logger.error("Analysis engine error: %s", exc)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc

    return result


@app.get("/stage/{stage_number}", response_model=StageInfo, tags=["SAP"])
async def get_stage_info(stage_number: int):
    """Return the description for a specific SAP stage (0-9)."""
    if stage_number < 0 or stage_number > 9:
        raise HTTPException(status_code=400, detail="Stage must be 0-9.")
    description = ai_engine.brain.STAGE_DESCRIPTIONS.get(stage_number, "")
    return StageInfo(stage=stage_number, description=description)


@app.get("/stages/", response_model=List[StageInfo], tags=["SAP"])
async def get_all_stages():
    """Return descriptions for all SAP stages."""
    return [
        StageInfo(stage=n, description=desc)
        for n, desc in ai_engine.brain.STAGE_DESCRIPTIONS.items()
    ]
