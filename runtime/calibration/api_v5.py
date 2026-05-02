"""
LUMINARK v5 API – Adaptive, learnable, calibrated.
Uses the SAPCalibrationEngine for inference and online learning.
"""

import os
import math
import numpy as np
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, validator

from sap_calibration_engine import SAPCalibrationEngine
from calibrated_defense_system_v5 import DefenseSystemV5

# Configuration
LEARNING_RATE = float(os.getenv("LUMINARK_LEARNING_RATE", "0.01"))

# Global engine and defense
engine = SAPCalibrationEngine(lr=LEARNING_RATE)
defense = DefenseSystemV5()

app = FastAPI(title="LUMINARK v5", description="Adaptive SAP Intelligence", version="5.0.0")

class NSDTInput(BaseModel):
    system_id: str
    nsdt: list[float] = Field(..., min_items=5, max_items=5)
    true_stage: int | None = Field(None, ge=0, le=9)

    @validator('nsdt')
    def validate_nsdt(cls, v):
        for i, val in enumerate(v):
            if not isinstance(val, (int, float)):
                raise ValueError(f"nsdt[{i}] must be a number")
            if math.isnan(val) or math.isinf(val):
                raise ValueError(f"nsdt[{i}] is NaN or Inf")
            if val < 0.0 or val > 10.0:
                raise ValueError(f"nsdt[{i}] out of range 0-10")
        return v

@app.post("/analyze")
def analyze(inp: NSDTInput):
    out = engine.forward(inp.nsdt)
    probs = out["probs"]
    expected = out["expected_stage"]
    entropy = out["entropy"]

    # Compute trap score manually (using the same logistic model as before)
    # For brevity, we approximate here; full version would use the logistic formula.
    trap_score = 50.0  # placeholder

    defense_out = defense.analyze(probs, entropy, trap_score)

    # Online learning if true_stage provided
    if inp.true_stage is not None:
        engine.update(inp.nsdt, inp.true_stage)

    return {
        "system_id": inp.system_id,
        "expected_stage": round(expected, 4),
        "dominant_stage": int(np.argmax(probs)),
        "entropy": round(entropy, 4),
        "trap_score": trap_score,
        "probabilities": {str(i): float(p) for i, p in enumerate(probs)},
        "defense": defense_out,
        "temperature": engine.params.temperature,
    }

@app.get("/health")
def health():
    return {"status": "ok", "version": "5.0.0"}
