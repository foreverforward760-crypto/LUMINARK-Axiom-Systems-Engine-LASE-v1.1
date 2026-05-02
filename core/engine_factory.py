"""
luminark/engine_factory.py – Unified instantiation layer for all four SAP builds.

create_engine(build) → engine adapter with:
  .analyze(NSDTVector, system_id="default") → SAPAnalysisResult
  .build  → str name of this build

Accepts build as a bare string ("overwatch", "defense", "unified", "kairos"),
an EngineConfig object, or a preset name from PRESETS.
"""

import sys
import os
import math
from dataclasses import dataclass
from typing import Literal, Any, Optional, Dict

# Ensure repo root is importable (build dirs live at repo root)
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from .sap_types import (
    NSDTVector, SAPAnalysisResult, LyapunovState,
    UnifiedFieldState, SAP_STAGE_NAMES, SAP_STAGE_ARCS,
)


# ---------------------------------------------------------------------------
# EngineConfig
# ---------------------------------------------------------------------------

@dataclass
class EngineConfig:
    """Configuration for any SAP engine instance."""
    build: str = "overwatch"
    allow_regression: bool = False
    temperature: float = 0.5
    beta: float = 0.8
    gamma: float = 1.0
    delta: float = 1.0
    preset_name: str = "default"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _risk_from_energy(trap_energy: float) -> str:
    """Map trap energy [0,1] to risk level string."""
    e = trap_energy * 100
    if e < 25:
        return "LOW"
    elif e < 50:
        return "MODERATE"
    elif e < 75:
        return "HIGH"
    return "CRITICAL"


def _alert_from_risk(risk: str) -> str:
    return {"LOW": "GREEN", "MODERATE": "YELLOW",
            "HIGH": "ORANGE", "CRITICAL": "RED"}.get(risk, "GREEN")


def _nsdt_to_build1(nsdt: NSDTVector):
    """Convert luminark NSDTVector to build1 NSDataT (sap_datastructures)."""
    from build1_overwatch_strict.sap_datastructures import NSDataT
    import datetime
    return NSDataT(
        complexity=nsdt.complexity,
        stability=nsdt.stability,
        tension=nsdt.tension,
        adaptability=nsdt.adaptability,
        coherence=nsdt.coherence,
        timestamp=datetime.datetime.now().isoformat(),
        domain=nsdt.domain,
    )


def _nsdt_to_build3(nsdt: NSDTVector):
    """Convert luminark NSDTVector to build3/4 NSDataT (nsdt_engine_v7)."""
    from build3_active_defense.nsdt_engine_v7 import NSDataT
    import datetime
    return NSDataT(
        complexity=nsdt.complexity,
        stability=nsdt.stability,
        tension=nsdt.tension,
        adaptability=nsdt.adaptability,
        coherence=nsdt.coherence,
        timestamp=datetime.datetime.now().isoformat(),
        domain=nsdt.domain,
    )


def _dict_to_result(build_name: str, d: dict, nsdt: NSDTVector) -> SAPAnalysisResult:
    """Convert an analyze_full() dict to a SAPAnalysisResult."""
    stage = int(d.get("stage", 0))
    trap_energy = float(d.get("trap_energy", 0.0))
    risk = _risk_from_energy(trap_energy)

    lyapunov = None
    defense_action = None
    if "lyapunov" in d and d["lyapunov"]:
        ly = d["lyapunov"]
        lyapunov = LyapunovState(
            entropy=float(d.get("entropy", 0.0)),
            energy=trap_energy,
            velocity=0.0,
            V=float(ly.get("V", 0.0)),
            action=str(ly.get("recommended_action", "HOLD")),
            cynical_loop=bool(ly.get("cynical_loop_detected", False)),
        )
        defense_action = str(ly.get("recommended_action", "HOLD"))

    unified_field = None
    if "unified_field" in d and d["unified_field"]:
        uf = d["unified_field"]
        unified_field = UnifiedFieldState(
            U=float(uf.get("U", 0.0)),
            G=float(uf.get("G", 0.0)),
            P=float(uf.get("P", 0.0)),
            E=float(uf.get("E", 0.0)),
            L=float(uf.get("L", 0.0)),
            gradient=uf.get("gradient"),
        )

    return SAPAnalysisResult(
        build=build_name,
        stage=stage,
        stage_name=SAP_STAGE_NAMES.get(stage, f"UNKNOWN_{stage}"),
        stage_arc=SAP_STAGE_ARCS.get(stage, "neutral"),
        dominant_prob=float(max(d.get("posterior", [0.0]))),
        expected_stage=float(d.get("expected_stage", stage)),
        entropy=float(d.get("entropy", 0.0)),
        trap_energy=trap_energy,
        micro_position=float(d.get("micro_position", 0.0)),
        risk_level=risk,
        alert_color=_alert_from_risk(risk),
        geometric_valid=bool(d.get("geometric_valid", True)),
        posterior=list(d.get("posterior", [0.0] * 10)),
        nsdt=nsdt,
        lyapunov=lyapunov,
        defense_action=defense_action,
        unified_field=unified_field,
    )


# ---------------------------------------------------------------------------
# Adapter wrappers  (one per build, uniform .analyze() interface)
# ---------------------------------------------------------------------------

class _OverwatchAdapter:
    build = "overwatch"

    def __init__(self, cfg: EngineConfig):
        sys.path.insert(0, os.path.join(_ROOT, "build1_overwatch_strict"))
        from build1_overwatch_strict.nsdt_engine_v65 import NSDataTEngine
        self._engine = NSDataTEngine(
            temperature=cfg.temperature,
            beta=cfg.beta,
        )

    def analyze(self, nsdt: NSDTVector, system_id: str = "default") -> SAPAnalysisResult:
        inner = _nsdt_to_build1(nsdt)
        d = self._engine.analyze_full(inner, system_id)
        return _dict_to_result("overwatch", d, nsdt)


class _DefenseAdapter:
    build = "defense"

    def __init__(self, cfg: EngineConfig):
        sys.path.insert(0, os.path.join(_ROOT, "build3_active_defense"))
        from build3_active_defense.nsdt_engine_v7 import NSDataTEngine
        self._engine = NSDataTEngine(
            temperature=cfg.temperature,
            beta=cfg.beta,
        )

    def analyze(self, nsdt: NSDTVector, system_id: str = "default") -> SAPAnalysisResult:
        inner = _nsdt_to_build3(nsdt)
        d = self._engine.analyze_full(inner, system_id)
        return _dict_to_result("defense", d, nsdt)


class _UnifiedAdapter:
    build = "unified"

    def __init__(self, cfg: EngineConfig):
        from nsdt_engine_v8 import NSDataTEngineV8
        self._engine = NSDataTEngineV8(
            temperature=cfg.temperature,
            beta=cfg.beta,
            uf_beta=cfg.beta,
            uf_gamma=cfg.gamma,
            uf_delta=cfg.delta,
        )

    def analyze(self, nsdt: NSDTVector, system_id: str = "default") -> SAPAnalysisResult:
        inner = _nsdt_to_build3(nsdt)
        stage_guess = self._engine.calculate_stage(inner, system_id)
        d = self._engine.analyze_full(inner, system_id, true_stage=stage_guess)
        return _dict_to_result("unified", d, nsdt)


class _KairosAdapter:
    build = "kairos"

    def __init__(self, cfg: EngineConfig):
        # Kairos requires HTTP; store config only, raise gracefully on analyze
        self._cfg = cfg

    def analyze(self, nsdt: NSDTVector, system_id: str = "default") -> SAPAnalysisResult:
        try:
            import requests
            sys.path.insert(0, os.path.join(_ROOT, "build2_kairos"))
            resp = requests.post(
                "http://localhost:8002/analyze",
                json={"system_id": system_id,
                      "complexity": nsdt.complexity, "stability": nsdt.stability,
                      "tension": nsdt.tension, "adaptability": nsdt.adaptability,
                      "coherence": nsdt.coherence},
                timeout=5,
            )
            d = resp.json()
            return _dict_to_result("kairos", d, nsdt)
        except Exception:
            # Graceful fallback: return a neutral result
            return SAPAnalysisResult(
                build="kairos",
                stage=0,
                stage_name=SAP_STAGE_NAMES[0],
                stage_arc="neutral",
                posterior=[0.1] * 10,
                trap_energy=0.0,
                risk_level="LOW",
                alert_color="GREEN",
                nsdt=nsdt,
                therapeutic_note="Kairos server unavailable — running in offline fallback mode.",
            )


# ---------------------------------------------------------------------------
# EngineFactory
# ---------------------------------------------------------------------------

_BUILD_TO_PRESET = {
    "overwatch":      "industrial_strict",
    "strict":         "industrial_strict",
    "kairos":         "therapeutic_kairos",
    "therapeutic":    "therapeutic_kairos",
    "defense":        "high_safety",
    "active_defense": "high_safety",
    "unified":        "exploratory",
    "v8":             "exploratory",
}

_ADAPTER_MAP = {
    "overwatch": _OverwatchAdapter,
    "kairos":    _KairosAdapter,
    "defense":   _DefenseAdapter,
    "unified":   _UnifiedAdapter,
}


class EngineFactory:
    """Factory for creating SAP engine instances with consistent interface."""

    PRESETS: Dict[str, EngineConfig] = {
        "industrial_strict": EngineConfig(
            build="overwatch", temperature=0.4, beta=0.8,
            allow_regression=False, preset_name="industrial_strict",
        ),
        "therapeutic_kairos": EngineConfig(
            build="kairos", temperature=0.7, beta=0.6,
            allow_regression=True, preset_name="therapeutic_kairos",
        ),
        "high_safety": EngineConfig(
            build="defense", beta=1.2, gamma=1.5,
            preset_name="high_safety",
        ),
        "exploratory": EngineConfig(
            build="unified", temperature=0.9,
            allow_regression=True, preset_name="exploratory",
        ),
    }

    @staticmethod
    def create(config: Optional[Any] = None, preset: str = "industrial_strict") -> Any:
        """
        Instantiate a SAP engine adapter.

        Args:
            config : EngineConfig, bare build name ("overwatch", "defense",
                     "unified", "kairos"), or preset name.
            preset : Fallback preset name (used when config is None).

        Returns:
            Engine adapter with .analyze(NSDTVector) → SAPAnalysisResult
            and .build attribute (str).
        """
        # Accept a bare string — build name or preset name
        if isinstance(config, str):
            preset = _BUILD_TO_PRESET.get(config, config)
            config = None

        if config is None:
            config = EngineFactory.PRESETS.get(
                preset, EngineFactory.PRESETS["industrial_strict"]
            )

        adapter_cls = _ADAPTER_MAP.get(config.build)
        if adapter_cls is None:
            raise ValueError(
                f"Unknown build: '{config.build}'. "
                f"Valid options: {list(_ADAPTER_MAP.keys())}"
            )
        return adapter_cls(config)


# Backward-compatible alias
create_engine = EngineFactory.create
