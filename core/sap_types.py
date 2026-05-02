"""
luminark/sap_types.py  –  Shared data structures for all four LUMINARK builds.

Provides:
  NSDTVector          – The five-dimensional input, with validation + serialisation.
  SAPStage            – Canonical SAP stage constants (names never change).
  SAPAnalysisResult   – Uniform output envelope across all four builds.
  LyapunovState       – Lyapunov-specific sub-result (Build 3 & 4).
  UnifiedFieldState   – Unified-field sub-result (Build 4 only).
  JSON_SCHEMA         – Full JSON Schema for NSDTVector (for API validation).

All types support:
  obj.to_dict()         →  plain dict  (JSON-serialisable)
  Type.from_dict(d)     →  typed object
"""

import datetime
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any


# ---------------------------------------------------------------------------
# Canonical SAP Stage Registry
# Names are non-negotiable constitutional constants – never rename or shorten.
# ---------------------------------------------------------------------------

SAP_STAGE_NAMES: Dict[int, str] = {
    0: "PLENARA",
    1: "SPARK OF NAVIGATION",
    2: "FORGE OF POLARITY",
    3: "ENGINE OF EXPRESSION",
    4: "CRUCIBLE OF EQUILIBRIUM",
    5: "DYNAMO OF WILL",
    6: "NEXUS OF HARMONY",
    7: "LENS OF DISTILLATION",
    8: "VESSEL OF GROUNDING",
    9: "TRANSPARENCY OF THE GUIDE",
}

SAP_STAGE_ARCS: Dict[int, str] = {
    0: "neutral",
    1: "descending", 2: "descending", 3: "descending", 4: "descending",
    5: "bifurcation",
    6: "ascending", 7: "ascending", 8: "ascending", 9: "ascending",
}


def stage_name(stage: int) -> str:
    """Return canonical name for a SAP stage (0–9)."""
    return SAP_STAGE_NAMES.get(stage, f"UNKNOWN_STAGE_{stage}")


# ---------------------------------------------------------------------------
# NSDTVector
# ---------------------------------------------------------------------------

@dataclass
class NSDTVector:
    """
    Five-dimensional NSDT input vector.

    All five axes are floats in [0.0, 10.0]:
      complexity    – structural / operational complexity
      stability     – current stability level
      tension       – internal / external tension
      adaptability  – capacity to adapt
      coherence     – internal alignment / coherence

    Optional metadata (not used in computation):
      timestamp – ISO-8601 string; auto-filled if omitted
      source    – data origin tag (e.g. 'sensor', 'manual', 'api')
      domain    – operational domain (e.g. 'power_grid', 'hr_tech')
    """
    complexity:    float = 5.0
    stability:     float = 5.0
    tension:       float = 5.0
    adaptability:  float = 5.0
    coherence:     float = 5.0
    timestamp:     str   = field(default_factory=lambda: datetime.datetime.now().isoformat())
    source:        str   = "manual"
    domain:        str   = "general"

    def validate(self) -> "NSDTVector":
        """Raise ValueError if any axis is outside [0, 10]."""
        for name in ("complexity", "stability", "tension", "adaptability", "coherence"):
            v = getattr(self, name)
            if not (0.0 <= v <= 10.0):
                raise ValueError(f"{name}={v} is outside [0, 10]")
        return self

    def to_list(self) -> List[float]:
        """Return [C, S, T, A, Coh] as a plain Python list."""
        return [self.complexity, self.stability, self.tension,
                self.adaptability, self.coherence]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "NSDTVector":
        return cls(
            complexity=float(d.get("complexity", 5.0)),
            stability=float(d.get("stability", 5.0)),
            tension=float(d.get("tension", 5.0)),
            adaptability=float(d.get("adaptability", 5.0)),
            coherence=float(d.get("coherence", 5.0)),
            timestamp=d.get("timestamp", datetime.datetime.now().isoformat()),
            source=d.get("source", "manual"),
            domain=d.get("domain", "general"),
        )

    @classmethod
    def from_list(cls, values: List[float], **meta) -> "NSDTVector":
        """Construct from a 5-element list [C, S, T, A, Coh]."""
        if len(values) != 5:
            raise ValueError(f"Expected 5 values, got {len(values)}")
        return cls(
            complexity=values[0], stability=values[1], tension=values[2],
            adaptability=values[3], coherence=values[4], **meta
        )

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, s: str) -> "NSDTVector":
        return cls.from_dict(json.loads(s))


# JSON Schema for NSDTVector (for API validation / OpenAPI docs)
NSDT_JSON_SCHEMA: Dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "NSDTVector",
    "description": "Five-dimensional NSDT input for LUMINARK engines (all axes in [0, 10]).",
    "type": "object",
    "required": ["complexity", "stability", "tension", "adaptability", "coherence"],
    "properties": {
        "complexity":   {"type": "number", "minimum": 0.0, "maximum": 10.0,
                         "description": "Structural/operational complexity"},
        "stability":    {"type": "number", "minimum": 0.0, "maximum": 10.0,
                         "description": "Current stability level"},
        "tension":      {"type": "number", "minimum": 0.0, "maximum": 10.0,
                         "description": "Internal/external tension"},
        "adaptability": {"type": "number", "minimum": 0.0, "maximum": 10.0,
                         "description": "Capacity to adapt"},
        "coherence":    {"type": "number", "minimum": 0.0, "maximum": 10.0,
                         "description": "Internal alignment/coherence"},
        "timestamp":    {"type": "string", "format": "date-time",
                         "description": "ISO-8601 observation timestamp"},
        "source":       {"type": "string", "description": "Data origin tag"},
        "domain":       {"type": "string", "description": "Operational domain"},
    },
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# LyapunovState  (Build 3 & 4)
# ---------------------------------------------------------------------------

@dataclass
class LyapunovState:
    """Lyapunov stability snapshot."""
    entropy:          float = 0.0
    energy:           float = 0.0
    velocity:         float = 0.0
    V:                float = 0.0   # Lyapunov function value
    action:           str   = "HOLD"
    cynical_loop:     bool  = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "LyapunovState":
        return cls(**{k: d[k] for k in d if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------------
# UnifiedFieldState  (Build 4 only)
# ---------------------------------------------------------------------------

@dataclass
class UnifiedFieldState:
    """Unified field output (U = αG + βP + γE + δL)."""
    U:          float = 0.0
    G:          float = 0.0   # geometric violation mass
    P:          float = 0.0   # cross-entropy
    E:          float = 0.0   # expected energy
    L:          float = 0.0   # Lyapunov value
    gradient:   Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "UnifiedFieldState":
        return cls(**{k: d[k] for k in d if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------------
# SAPAnalysisResult  –  uniform output envelope across all four builds
# ---------------------------------------------------------------------------

@dataclass
class SAPAnalysisResult:
    """
    Uniform analysis result returned by all four LUMINARK engines
    (via the luminark.engine_factory adapter layer).

    Core fields are always populated.
    Optional fields are populated only by builds that support them.
    """
    # Always present
    build:           str   = "overwatch"
    stage:           int   = 0
    stage_name:      str   = "PLENARA"
    stage_arc:       str   = "neutral"
    dominant_prob:   float = 0.0
    expected_stage:  float = 0.0
    entropy:         float = 0.0
    trap_energy:     float = 0.0
    micro_position:  float = 0.0
    risk_level:      str   = "LOW"
    alert_color:     str   = "GREEN"
    geometric_valid: bool  = True
    posterior:       List[float] = field(default_factory=lambda: [0.0]*10)
    nsdt:            Optional[NSDTVector] = None
    timestamp:       str   = field(default_factory=lambda: datetime.datetime.now().isoformat())

    # Build 3 & 4 only
    lyapunov:        Optional[LyapunovState] = None
    defense_action:  Optional[str] = None

    # Build 4 only
    unified_field:   Optional[UnifiedFieldState] = None

    # Build 2 only
    therapeutic_note: Optional[str] = None
    regression_risk:  Optional[float] = None

    # Arbitrary extras (build-specific)
    extras:          Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Flatten nested dataclass dicts for cleaner JSON
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SAPAnalysisResult":
        # Reconstruct nested objects if present
        if "nsdt" in d and d["nsdt"] is not None and isinstance(d["nsdt"], dict):
            d = dict(d)
            d["nsdt"] = NSDTVector.from_dict(d["nsdt"])
        if "lyapunov" in d and d["lyapunov"] is not None and isinstance(d["lyapunov"], dict):
            d = dict(d)
            d["lyapunov"] = LyapunovState.from_dict(d["lyapunov"])
        if "unified_field" in d and d["unified_field"] is not None and isinstance(d["unified_field"], dict):
            d = dict(d)
            d["unified_field"] = UnifiedFieldState.from_dict(d["unified_field"])
        return cls(**{k: d[k] for k in d if k in cls.__dataclass_fields__})

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def summary(self) -> str:
        """One-line human-readable summary."""
        lyap = f" | V={self.lyapunov.V:.3f}" if self.lyapunov else ""
        uf   = f" | U={self.unified_field.U:.3f}" if self.unified_field else ""
        return (
            f"[{self.build.upper()}] Stage {self.stage} ({self.stage_name}) "
            f"| Arc={self.stage_arc} | Energy={self.trap_energy:.3f} "
            f"| Risk={self.risk_level}{lyap}{uf}"
        )


# ---------------------------------------------------------------------------
# SAPStage  –  Legacy enum alias (used by dissolution.py, inversion_analyzer.py)
# Maps named constants to integer SAP stage indices.
# Constitutional stage numbers never change.
# ---------------------------------------------------------------------------

from enum import IntEnum

class SAPStage(IntEnum):
    VOID        = 0   # PLENARA
    NAVIGATION  = 1   # SPARK OF NAVIGATION
    POLARITY    = 2   # FORGE OF POLARITY
    EXPRESSION  = 3   # ENGINE OF EXPRESSION
    EQUILIBRIUM = 4   # CRUCIBLE OF EQUILIBRIUM
    THRESHOLD   = 5   # DYNAMO OF WILL  (bifurcation / point of no return)
    HARMONY     = 6   # NEXUS OF HARMONY
    FOUNDATION  = 7   # LENS OF DISTILLATION
    INTEGRATION = 8   # VESSEL OF GROUNDING
    RELEASE     = 9   # TRANSPARENCY OF THE GUIDE
    # Semantic aliases used in inversion_analyzer / dissolution
    UNITY    = 6      # Nexus of Harmony → coherent synthesis
    ANALYSIS = 3      # Engine of Expression → active discernment


# ---------------------------------------------------------------------------
# SystemState  –  Legacy state carrier used by dissolution.py / inversion_analyzer.py
# Wraps a scalar SAPStage integer with context fields.
# ---------------------------------------------------------------------------

@dataclass
class SystemState:
    """
    Legacy state object for InversionAnalyzer / DissolutionEngine.
    Thin wrapper kept for backward compatibility with pre-v1.0.0 modules.
    
    Extended fields for Stages 6-8 philosophical architecture:
      - stage_5_gateway: Whether Stage 5 Middle Path was accessed (True) or default tumble (False)
      - revealed_self: What the system projects externally (0-10 scale)
      - concealed_self: What the system actually contains beneath projection (0-10 scale)
      - consciousness_stability: Inverse of physical stability per Tumbling Inversion Principle
      - extra: Classifier results for Stages 6-8
    """
    stage:                   SAPStage = SAPStage.VOID
    nsdt:                    Optional[NSDTVector] = None
    is_trap:                 bool  = False
    trap_reason:             str   = ""
    recommended_action:      str   = "HOLD"
    unified_field_value:     float = 0.0
    recalibration_recommended: bool = False
    extra:                   Dict[str, Any] = field(default_factory=dict)
    
    # Stage 5 & 6-8 Architecture
    stage_5_gateway:         bool  = False  # True if Middle Path accessed at Stage 5
    middle_path_accessed:    bool  = False  # Alias for stage_5_gateway
    witness_position_active: bool  = False  # Whether witness consciousness is maintained
    revealed_self:           float = 5.0    # External projection (0-10)
    concealed_self:          float = 5.0    # Internal reality (0-10)
    consciousness_stability: float = 5.0    # Inverse of physical stability (0-10)
    nsdt_vector:             Optional[List[float]] = None  # Raw NSDT as list
    nsdt_history:            Optional[List[List[float]]] = None  # Last N vectors
    inversion_state:         Optional[Dict[str, Any]] = None  # Tumbling inversion result
    arc_direction:           str  = "indeterminate"  # ascending, descending, plateau
    gratitude_mechanism_engaged: bool = False  # Whether gratitude mechanism is active
    flow_analysis:           Optional[Dict[str, Any]] = None  # Stage 6 flow quality
    crucible_analysis:       Optional[Dict[str, Any]] = None  # Stage 7 crucible mode
    crystallization_analysis: Optional[Dict[str, Any]] = None  # Stage 8 crystallization

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage":                   int(self.stage),
            "stage_name":              SAP_STAGE_NAMES.get(int(self.stage), "UNKNOWN"),
            "nsdt":                    self.nsdt.to_dict() if self.nsdt else None,
            "nsdt_vector":             self.nsdt_vector,
            "is_trap":                 self.is_trap,
            "trap_reason":             self.trap_reason,
            "recommended_action":      self.recommended_action,
            "unified_field_value":     self.unified_field_value,
            "recalibration_recommended": self.recalibration_recommended,
            "extra":                   self.extra,
            "stage_5_gateway":         self.stage_5_gateway,
            "middle_path_accessed":    self.middle_path_accessed,
            "witness_position_active": self.witness_position_active,
            "revealed_self":           self.revealed_self,
            "concealed_self":          self.concealed_self,
            "consciousness_stability": self.consciousness_stability,
            "inversion_state":         self.inversion_state,
            "arc_direction":           self.arc_direction,
            "gratitude_mechanism_engaged": self.gratitude_mechanism_engaged,
            "flow_analysis":           self.flow_analysis,
            "crucible_analysis":       self.crucible_analysis,
            "crystallization_analysis": self.crystallization_analysis,
        }
