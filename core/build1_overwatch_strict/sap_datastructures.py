"""
sap_datastructures.py – Shared dataclasses for Build 1 (Overwatch Strict v6.5)
NSDataT, TrapScoreResult, TemporalSnapshot
"""
import datetime
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class NSDataT:
    complexity:   float = 5.0
    stability:    float = 5.0
    tension:      float = 5.0
    adaptability: float = 5.0
    coherence:    float = 5.0
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    source: str = "manual"
    domain: str = "power_grid"

    def to_dict(self) -> Dict:
        return {
            "complexity":   self.complexity,
            "stability":    self.stability,
            "tension":      self.tension,
            "adaptability": self.adaptability,
            "coherence":    self.coherence,
            "timestamp":    self.timestamp,
            "source":       self.source,
            "domain":       self.domain,
        }


@dataclass
class TrapScoreResult:
    raw_score:         float = 0.0
    normalized_score:  float = 0.0
    rigidity_index:    float = 0.0
    adaptability_norm: float = 0.0
    stage:             int   = 0
    risk_level:        str   = "LOW"

    @property
    def alert_color(self) -> str:
        return {"LOW": "GREEN", "MODERATE": "YELLOW",
                "HIGH": "ORANGE", "CRITICAL": "RED"}.get(self.risk_level, "GRAY")


@dataclass
class TemporalSnapshot:
    timestamp:  str
    nsdt:       NSDataT
    stage:      int
    trap_score: float
    domain:     str
    event_tag:  str = ""
