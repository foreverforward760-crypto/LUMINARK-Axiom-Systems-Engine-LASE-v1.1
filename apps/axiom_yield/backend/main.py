"""
backend/main.py – Axiom Yield Broker FastAPI Application

Entry point for the LUMINARK-powered logistics intelligence backend.

Start with:
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.yield_router import router as yield_router
from backend.eld.connectors import ELDClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage aiohttp session lifecycle — open on startup, close on shutdown."""
    logger.info("Axiom Yield Broker starting — initialising ELD connection pool")
    ELDClient.get_session()     # pre-warm the shared aiohttp session
    yield
    logger.info("Axiom Yield Broker shutting down — closing ELD connection pool")
    await ELDClient.close_session()


app = FastAPI(
    title="Axiom Yield Broker",
    description=(
        "SAP-powered predictive logistics intelligence. "
        "Detects carrier Stage 8 false-stability traps 24-48h before failure."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten to dashboard origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(yield_router, prefix="/api/yield", tags=["yield"])


@app.get("/health")
def health():
    return {
        "status":  "ok",
        "engine":  "Axiom Yield Broker",
        "version": "1.0.0",
    }
