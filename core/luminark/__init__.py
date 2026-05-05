"""
luminark – Unified public surface for the LUMINARK engine ecosystem.

Primary imports:
  create_engine(build)  → engine with .analyze(NSDTVector) → SAPAnalysisResult
  NSDTVector            → 5-D input [0.0 – 10.0] per axis
  SAPAnalysisResult     → uniform output envelope across all four builds
  SAP_STAGE_NAMES       → constitutional stage name registry (dict[int, str])
  EngineConfig          → full hyperparameter config (with JSON/YAML round-trip)

Extended imports (domain utilities):
  FrequencyAdapter      → acoustic/resonance metrics → NSDTVector
  NSDTBuilder           → generic metrics dict → NSDTVector
  DissolutionEngine     → Stage-9 → Stage-0 cycle closure
  InversionAnalyzer     → stage detection + trap identification (legacy)
  RecalibrationEngine   → corrective nudge for stuck/trapped states (legacy)
  UnifiedField          → U = β·P + γ·E + δ·L field equation
  OmegaLoop             → cross-build telemetry router
"""

# ── Core types ────────────────────────────────────────────────────────────────
from .sap_types import (
    NSDTVector,
    SAPAnalysisResult,
    LyapunovState,
    UnifiedFieldState,
    SAP_STAGE_NAMES,
    SAP_STAGE_ARCS,
    NSDT_JSON_SCHEMA,
    stage_name,
    # Legacy types (used by inversion_analyzer, dissolution)
    SAPStage,
    SystemState,
)

# ── Config & factory ──────────────────────────────────────────────────────────
from .config import EngineConfig, PRESETS
from .engine_factory import EngineFactory, create_engine

# ── Domain utilities ──────────────────────────────────────────────────────────
from .frequency_calculator import FrequencyAdapter
from .nsdt_calculator import NSDTBuilder
from .dissolution import DissolutionEngine
from .inversion_analyzer import InversionAnalyzer
from .recalibration import RecalibrationEngine
from .unified_field import UnifiedField
from .omega_loop import OmegaLoop, NSDTEvent, RoutingRule

# ── Version ───────────────────────────────────────────────────────────────────
from .version import __version__, __author__, __org__

__all__ = [
    # Core types
    "NSDTVector",
    "SAPAnalysisResult",
    "LyapunovState",
    "UnifiedFieldState",
    "SAP_STAGE_NAMES",
    "SAP_STAGE_ARCS",
    "NSDT_JSON_SCHEMA",
    "stage_name",
    "SAPStage",
    "SystemState",
    # Config & factory
    "EngineConfig",
    "PRESETS",
    "EngineFactory",
    "create_engine",
    # Domain utilities
    "FrequencyAdapter",
    "NSDTBuilder",
    "DissolutionEngine",
    "InversionAnalyzer",
    "RecalibrationEngine",
    "UnifiedField",
    "OmegaLoop",
    "NSDTEvent",
    "RoutingRule",
    # Version
    "__version__",
    "__author__",
    "__org__",
]
