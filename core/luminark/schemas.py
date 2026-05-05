"""
LUMINARK OVERWATCH PRIME — Core Engine v1.0
schemas.py — Canonical data models

All inputs and outputs must conform to CANONICAL_INPUT_OUTPUT_SCHEMA.json.
Do not modify without incrementing Core Engine version.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class NSDTVector(BaseModel):
    """Five-dimensional system health vector. All values normalized 0.0–1.0."""
    complexity:   float = Field(ge=0.0, le=1.0, description="Rate of change, unpredictability, interaction density")
    stability:    float = Field(ge=0.0, le=1.0, description="Reserve capacity, operating margin, structural integrity")
    tension:      float = Field(ge=0.0, le=1.0, description="Demand-supply gap, stress load, pressure differential")
    adaptability: float = Field(ge=0.0, le=1.0, description="Flexibility, rerouting capacity, redundancy")
    coherence:    float = Field(ge=0.0, le=1.0, description="Communication integrity, coordination quality")

    @property
    def mean(self) -> float:
        return (self.complexity + self.stability + self.tension + self.adaptability + self.coherence) / 5.0

    def as_list(self) -> List[float]:
        return [self.complexity, self.stability, self.tension, self.adaptability, self.coherence]


class StageInfo(BaseModel):
    stage:       int = Field(ge=0, le=9, description="Health stage (0=worst, 9=transformational)")
    label:       str = Field(description="Stage name")
    description: str = Field(description="Stage characterization")
    risk:        Literal["LOW", "WATCH", "ELEVATED", "CRITICAL"]
    distance:    float = Field(description="Euclidean distance from centroid — lower = higher confidence")


class TrajectoryResult(BaseModel):
    state:      Literal["ASCENDING", "DESCENDING", "OSCILLATING", "STABLE"]
    confidence: float = Field(ge=0.0, le=1.0)
    window:     int   = Field(description="Number of readings analyzed")


class ConsensusResult(BaseModel):
    confidence:  float = Field(ge=0.0, le=1.0, description="Evaluator agreement 0–1")
    label:       Literal["HIGH CONSENSUS", "MODERATE CONSENSUS", "SPLIT VERDICT"]
    votes:       List[int] = Field(description="Stage vote from each evaluator")
    uncertainty: float = Field(ge=0.0, le=1.0, description="1 - confidence")


class FailureSignature(BaseModel):
    name:           str
    pattern:        List[float]
    example_events: List[str]
    distance:       float


class AlertResult(BaseModel):
    level:   int    = Field(ge=1, le=5, description="1=NOMINAL … 5=QUARANTINE")
    name:    Literal["NOMINAL", "OCTO-CAMOUFLAGE", "MYCELIAL CONTAINMENT", "HARROWING", "QUARANTINE"]
    color:   Literal["GREEN", "YELLOW", "ORANGE", "RED"]
    message: str
    fired:   bool   = Field(description="True if level >= 2 (alert condition active)")


class AnalysisResult(BaseModel):
    timestamp:              datetime
    system_id:              str
    domain:                 str
    nsdt:                   NSDTVector
    nsdt_mean:              float
    stage:                  StageInfo
    trapscore:              float = Field(ge=0.0, le=1.0)
    trajectory:             TrajectoryResult
    consensus:              ConsensusResult
    alert:                  AlertResult
    matched_signature:      Optional[FailureSignature] = None
    recommended_action:     str


class TelemetryInput(BaseModel):
    """Canonical input to the analysis engine."""
    timestamp:   datetime
    system_id:   str
    domain:      str
    nsdt:        NSDTVector
    source:      str
    raw_metrics: Optional[dict] = None
