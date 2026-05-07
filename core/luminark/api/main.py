"""
luminark/api/main.py
────────────────────
LASE SDK — FastAPI Application Entry Point v1.0
Stanfield's Axiom of Perpetuity (SAP) Framework

Start the server:
    uvicorn luminark.api.main:app --host 0.0.0.0 --port 8080

Environment variables:
    LASE_API_KEY     — Required. Your private API key.
    LASE_DEMO_KEY    — Optional. Public demo key (default: lase-demo-public).
    LASE_RATE_LIMIT  — Optional. Rate limit string (default: 120/minute).

© 2026 Richard L. Stanfield / Meridian Axiom Alignment Technologies LLC
Contact: LuminarkMeridian@gmail.com
"""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .classify import router as classify_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)

# ── Rate limiter ───────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "LASE SDK API",
    description = (
        "LUMINARK Axiom Systems Engine — SAP Classification as a Service.\n\n"
        "Classifies any five-dimensional NSDT vector (complexity, stability, "
        "tension, adaptability, coherence) through the canonical Stanfield's "
        "Axiom of Perpetuity (SAP) engine and returns the behavioral stage, "
        "trap energy, risk level, and stage-specific intelligence.\n\n"
        "**Stage names are constitutionally locked** — the 10 canonical SAP "
        "stage names are enforced at the schema level and cannot drift.\n\n"
        "© 2026 Richard L. Stanfield / Meridian Axiom Alignment Technologies LLC  \n"
        "Contact: LuminarkMeridian@gmail.com"
    ),
    version     = "1.1.0",
    contact     = {
        "name":  "Richard L. Stanfield — MAAT",
        "email": "LuminarkMeridian@gmail.com",
    },
    license_info = {
        "name": "Proprietary — All rights reserved",
    },
    docs_url    = "/docs",
    redoc_url   = "/redoc",
    openapi_url = "/openapi.json",
)

# ── Middleware ─────────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],   # Tighten to specific origins in production
    allow_credentials = False,
    allow_methods     = ["GET", "POST"],
    allow_headers     = ["X-LASE-API-KEY", "Content-Type"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(classify_router)


# ── Root ───────────────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": "LASE SDK API",
        "version": "1.1.0",
        "docs":    "/docs",
        "health":  "/v1/health",
        "classify": "/v1/classify",
    }


# ── Global error handler ───────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "code": 500},
    )
