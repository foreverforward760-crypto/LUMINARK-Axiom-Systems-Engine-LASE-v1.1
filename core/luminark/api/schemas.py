"""
luminark/api/schemas.py
───────────────────────
LASE SDK — Canonical I/O Schemas v1.0
Stanfield's Axiom of Perpetuity (SAP) Framework

These Pydantic models are the PUBLIC API CONTRACT for the LASE /classify
endpoint.  Stage names in output are locked to SAP_STAGE_NAMES and enforced
at validation time.  No downstream code may rename, truncate, or redefine
canonical stage names.

NSDT VECTOR INPUT CONTRACT:
    All five axes: float on [0.0, 10.0]
    Axes: complexity, stability, tension, adaptability, coherence

OUTPUT CONTRACT:
    stage_index  : int  [0–9]
    stage_name   : str  — one of the 10 canonical SAP names (immutable)
    trap_energy  : float [0.0, 1.0]
    risk_level   : str  — LOW | MODERATE | HIGH | CRITICAL
    ...

© 2026 Richard L. Stanfield / Meridian Axiom Alignment Technologies LLC
Contact: LuminarkMeridian@gmail.com
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from luminark.sap_types import SAP_STAGE_NAMES


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────

class BuildPreset(str, Enum):
    OVERWATCH = "overwatch"   # Industrial — logistics, infrastructure, FMCSA
    KAIROS    = "kairos"      # Therapeutic — human behavior, consciousness
    DEFENSE   = "defense"     # High-safety critical systems
    UNIFIED   = "unified"     # Research / exploratory


class RiskLevel(str, Enum):
    LOW      = "LOW"
    MODERATE = "MODERATE"
    HIGH     = "HIGH"
    CRITICAL = "CRITICAL"


class AlertColor(str, Enum):
    GREEN  = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED    = "RED"


# ─────────────────────────────────────────────────────────────────────────────
# NSDT Input — the five-dimensional vector
# ─────────────────────────────────────────────────────────────────────────────

class NSDTInput(BaseModel):
    """
    Five-dimensional NSDT input vector.
    All axes must be on the [0.0, 10.0] scale — no exceptions.
    """
    complexity:    float = Field(..., ge=0.0, le=10.0,
                                 description="Structural/operational complexity")
    stability:     float = Field(..., ge=0.0, le=10.0,
                                 description="Current stability level")
    tension:       float = Field(..., ge=0.0, le=10.0,
                                 description="Internal/external tension")
    adaptability:  float = Field(..., ge=0.0, le=10.0,
                                 description="Capacity to adapt to change")
    coherence:     float = Field(..., ge=0.0, le=10.0,
                                 description="Internal alignment/coherence")

    model_config = {"json_schema_extra": {
        "example": {
            "complexity": 7.2,
            "stability": 3.1,
            "tension": 8.5,
            "adaptability": 2.8,
            "coherence": 3.4,
        }
    }}


# ─────────────────────────────────────────────────────────────────────────────
# Classify Request
# ─────────────────────────────────────────────────────────────────────────────

class ClassifyRequest(BaseModel):
    """
    Full classification request sent to POST /classify.
    """
    nsdt:    NSDTInput
    build:   BuildPreset = Field(
        BuildPreset.OVERWATCH,
        description="Engine preset. Use 'overwatch' for logistics/industrial, "
                    "'kairos' for therapeutic/consciousness, "
                    "'defense' for high-safety systems, "
                    "'unified' for research."
    )
    domain:  str = Field(
        "general",
        max_length=64,
        pattern=r"^[a-z0-9_\-]+$",
        description="Operational domain tag (e.g. 'logistics', 'power_grid', 'hr_tech'). "
                    "Used for telemetry only — does not alter classification math."
    )
    system_id: Optional[str] = Field(
        None,
        max_length=128,
        description="Optional entity identifier (carrier ID, asset ID, etc.). "
                    "Echoed in response for correlation."
    )

    model_config = {"json_schema_extra": {
        "example": {
            "nsdt": {
                "complexity": 7.2,
                "stability": 3.1,
                "tension": 8.5,
                "adaptability": 2.8,
                "coherence": 3.4,
            },
            "build": "overwatch",
            "domain": "logistics",
            "system_id": "carrier-MC-882341",
        }
    }}


# ─────────────────────────────────────────────────────────────────────────────
# Stage 5 Bifurcation Output
# ─────────────────────────────────────────────────────────────────────────────

class BifurcationResult(BaseModel):
    """Stage 5 (DYNAMO OF WILL) three-way bifurcation output."""
    path:        str   = Field(..., description="'advance' | 'retreat' | 'freeze'")
    path_energy: float = Field(..., description="Path selection confidence [0.0–1.0]")
    lock_active: bool  = Field(..., description="True if bifurcation lock detected")


# ─────────────────────────────────────────────────────────────────────────────
# Stage 8 Trap Output
# ─────────────────────────────────────────────────────────────────────────────

class TrapResult(BaseModel):
    """Stage 8 (VESSEL OF GROUNDING) dual-chamber trap output."""
    chamber_active: Optional[str] = Field(
        None,
        description="'Illusion of Arrival' | 'Illusion of Permanence' | null"
    )
    amplifier_applied: bool = Field(
        ...,
        description="True if the 1.45× TrapScore amplifier was applied"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Classify Response — LOCKED OUTPUT CONTRACT
# ─────────────────────────────────────────────────────────────────────────────

class ClassifyResponse(BaseModel):
    """
    LASE classification result.

    stage_name is always one of the 10 canonical SAP stage names.
    This field is validated at the model level — no drift possible.
    """
    # ── Identity ──────────────────────────────────────────────────────────────
    system_id:   Optional[str] = Field(None, description="Echoed from request")
    build:       str           = Field(..., description="Engine build used")
    domain:      str           = Field(..., description="Domain tag from request")

    # ── Core Classification ───────────────────────────────────────────────────
    stage_index: int   = Field(..., ge=0, le=9,
                               description="SAP stage integer [0–9]")
    stage_name:  str   = Field(...,
                               description="Canonical SAP stage name — one of the 10 "
                                           "constitutional names. Never truncated or renamed.")
    stage_arc:   str   = Field(...,
                               description="'ascending' | 'descending' | 'bifurcation' | 'neutral'")

    # ── Probability Distribution ───────────────────────────────────────────────
    dominant_probability: float = Field(..., ge=0.0, le=1.0,
                                        description="Posterior probability of assigned stage")
    expected_stage:       float = Field(..., ge=0.0, le=9.0,
                                        description="Probability-weighted expected stage value")
    posterior:            List[float] = Field(..., min_length=10, max_length=10,
                                             description="Full 10-stage posterior distribution")
    entropy:              float = Field(..., ge=0.0,
                                       description="Classification entropy (lower = more confident)")

    # ── Energy & Risk ─────────────────────────────────────────────────────────
    trap_energy:  float      = Field(..., ge=0.0, le=1.0,
                                     description="Trap energy [0.0–1.0]. Stage 8 applies 1.45× amplifier.")
    risk_level:   RiskLevel  = Field(..., description="LOW | MODERATE | HIGH | CRITICAL")
    alert_color:  AlertColor = Field(..., description="GREEN | YELLOW | ORANGE | RED")

    # ── Stage-Specific Intelligence ───────────────────────────────────────────
    stage_5_bifurcation: Optional[BifurcationResult] = Field(
        None, description="Populated only when stage_index == 5 (DYNAMO OF WILL)"
    )
    stage_8_trap:        Optional[TrapResult]         = Field(
        None, description="Populated only when stage_index == 8 (VESSEL OF GROUNDING)"
    )

    # ── Inversion Principle Flag ───────────────────────────────────────────────
    inversion_active: bool = Field(
        ...,
        description="True when Tumbling Inversion condition detected "
                    "(even stages physically stable/consciously unstable; "
                    "odd stages physically unstable/consciously stable)"
    )

    # ── Meta ──────────────────────────────────────────────────────────────────
    geometric_valid: bool  = Field(..., description="True if NSDT vector passes geometric constraints")
    timestamp:       str   = Field(..., description="ISO-8601 classification timestamp")
    lase_version:    str   = Field("1.1.0", description="LASE engine version")

    # ── Locked Stage Name Validator ───────────────────────────────────────────
    @field_validator("stage_name")
    @classmethod
    def stage_name_must_be_canonical(cls, v: str) -> str:
        """
        Enforce constitutional stage names.
        This validator makes stage name drift IMPOSSIBLE at the API layer.
        """
        canonical = set(SAP_STAGE_NAMES.values())
        if v not in canonical:
            raise ValueError(
                f"'{v}' is not a canonical SAP stage name. "
                f"Valid names: {sorted(canonical)}"
            )
        return v

    @model_validator(mode="after")
    def stage_index_name_coherence(self) -> "ClassifyResponse":
        """Stage index and name must agree with the constitutional registry."""
        expected_name = SAP_STAGE_NAMES.get(self.stage_index)
        if expected_name and self.stage_name != expected_name:
            raise ValueError(
                f"stage_index={self.stage_index} requires stage_name='{expected_name}', "
                f"got '{self.stage_name}'"
            )
        return self


# ─────────────────────────────────────────────────────────────────────────────
# Error Response
# ─────────────────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    error:   str
    detail:  Optional[str] = None
    code:    int
