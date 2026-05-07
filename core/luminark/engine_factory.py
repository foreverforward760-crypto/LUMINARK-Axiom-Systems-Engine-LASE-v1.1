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


    @staticmethod
    def create_calibrated(
        build: str = "overwatch",
        learned_path: str = None,
    ):
        """
        Create a SAP engine adapter with the calibration bridge attached.

        The returned adapter has an additional .calibration attribute
        (CalibrationBridge) that can be used to:
          - Get calibrated stage probabilities before Bayesian inference
          - Run online updates after confirmed stage classifications

        Parameters
        ----------
        build        : Engine build name ("overwatch", "kairos", "defense", "unified")
        learned_path : Optional path to previously saved learned parameters JSON
        """
        try:
            from calibration_bridge import CalibrationBridge
        except ImportError:
            from .calibration_bridge import CalibrationBridge

        adapter = EngineFactory.create(build)
        adapter.calibration = CalibrationBridge(learned_path=learned_path)
        return adapter


# Backward-compatible aliases
create_engine            = EngineFactory.create
create_calibrated_engine = EngineFactory.create_calibrated


# ─────────────────────────────────────────────────────────────────────────────
# CalibratedAdapter — wraps any build adapter with the calibration bridge
# ─────────────────────────────────────────────────────────────────────────────

class CalibratedAdapter:
    """
    Wraps an existing engine adapter with the UpdateAndRestoredOverwatch v5
    adaptive calibration layer (SAPCalibrationEngine).

    WIRING (LASE Task 5):
        The calibration bridge is now active inside analyze() — not just
        attached as an attribute.

    Inference flow:
        1. CalibrationBridge.forward(nsdt) → calibrated prior
           (expected_stage, probs, entropy from learned centroids)
        2. Wrapped engine.analyze(nsdt) → raw SAPAnalysisResult
        3. If calibration and engine disagree by >1.5 stages, blend them:
           final_stage = round(0.55 * engine_stage + 0.45 * expected_stage)
        4. Return augmented SAPAnalysisResult with calibration metadata attached.

    Online learning:
        After external confirmation of a true stage, call:
            adapter.record_confirmed(nsdt_list, confirmed_stage)
        This updates the bridge's learned centroids.

    Persistence:
        adapter.save_calibration(path)   — serialize centroids to JSON
        adapter.load_calibration(path)   — load previously saved centroids
    """

    def __init__(
        self,
        base_adapter,
        learned_path: Optional[str] = None,
        blend_weight: float = 0.45,   # weight of calibration prior in blend
    ):
        self._base      = base_adapter
        self._blend     = float(max(0.0, min(1.0, blend_weight)))
        self.build      = base_adapter.build

        # Import CalibrationBridge
        try:
            from .calibration_bridge import CalibrationBridge
        except ImportError:
            from calibration_bridge import CalibrationBridge

        self.calibration = CalibrationBridge(learned_path=learned_path)
        self._enabled    = True

    def analyze(self, nsdt: NSDTVector, system_id: str = "default") -> SAPAnalysisResult:
        """
        Run calibrated analysis.

        Blends the canonical engine's stage output with the calibration
        bridge's learned expected_stage when the two disagree significantly.
        """
        # 1. Run base engine
        result = self._base.analyze(nsdt, system_id)

        if not self._enabled:
            return result

        try:
            # 2. Get calibration prior
            nsdt_list = [
                nsdt.complexity, nsdt.stability,
                nsdt.tension,    nsdt.adaptability,
                nsdt.coherence,
            ]
            calib = self.calibration.forward(nsdt_list)
            cal_expected = calib["expected_stage"]
            cal_probs    = calib["probs"]
            cal_entropy  = calib["entropy"]

            # 3. Blend only when calibration and engine disagree > 1.5 stages
            engine_stage = result.stage
            if abs(engine_stage - cal_expected) > 1.5:
                blended_stage = round(
                    (1.0 - self._blend) * engine_stage +
                    self._blend * cal_expected
                )
                blended_stage = max(0, min(9, int(blended_stage)))
            else:
                blended_stage = engine_stage

            # 4. Augment result with calibration metadata
            #    (attach as extra attributes — SAPAnalysisResult is a dataclass
            #     so we can set extra attrs without breaking existing consumers)
            result.stage                = blended_stage
            result.stage_name           = SAP_STAGE_NAMES.get(blended_stage, f"UNKNOWN_{blended_stage}")
            result.calibration_expected = round(cal_expected, 3)
            result.calibration_entropy  = round(cal_entropy, 4)
            result.calibration_probs    = [round(p, 4) for p in cal_probs]
            result.calibration_blended  = (blended_stage != engine_stage)

        except Exception as _e:
            # Calibration failure is non-fatal — return raw engine result
            pass

        return result

    def record_confirmed(self, nsdt_list: list, confirmed_stage: int) -> None:
        """
        Online update: record a confirmed SAP stage for calibration learning.

        Call after forensic audit, retrospective validation, or domain-expert
        review confirms the true SAP stage of a previously classified system.

        Parameters
        ----------
        nsdt_list       : [complexity, stability, tension, adaptability, coherence]
                          on luminark native scale [0, 10]
        confirmed_stage : int [0–9] — verified true SAP stage
        """
        self.calibration.update(nsdt_list, confirmed_stage)

    def save_calibration(self, path: str) -> None:
        """Save learned calibration parameters to JSON."""
        self.calibration.save(path)

    def load_calibration(self, path: str) -> None:
        """Load previously saved calibration parameters from JSON."""
        self.calibration.load(path)

    def disable_calibration(self) -> None:
        """Disable calibration blending — pass-through to base engine only."""
        self._enabled = False

    def enable_calibration(self) -> None:
        """Re-enable calibration blending after disable_calibration()."""
        self._enabled = True


# Patch EngineFactory.create_calibrated to use the new CalibratedAdapter
def _create_calibrated_v2(
    build: str = "overwatch",
    learned_path: Optional[str] = None,
    blend_weight: float = 0.45,
) -> CalibratedAdapter:
    """
    Create a SAP engine adapter with the calibration bridge ACTIVE during inference.

    LASE Task 5 upgrade: CalibratedAdapter now blends calibration prior into
    every analyze() call rather than just attaching the bridge as a passive attribute.

    Parameters
    ----------
    build        : Engine build name ("overwatch", "kairos", "defense", "unified")
    learned_path : Optional path to previously saved learned parameters JSON
    blend_weight : Weight of calibration prior in stage blending [0.0–1.0]
                   Default 0.45 = calibration provides 45% influence when disagreement >1.5 stages

    Returns
    -------
    CalibratedAdapter — duck-type compatible with all engine adapters.
    Additional methods: record_confirmed(), save_calibration(), load_calibration()
    Additional attributes: calibration (CalibrationBridge)
    """
    base = EngineFactory.create(build)
    return CalibratedAdapter(base, learned_path=learned_path, blend_weight=blend_weight)


# Hot-patch the factory method and the backward-compatible alias
EngineFactory.create_calibrated = staticmethod(_create_calibrated_v2)
create_calibrated_engine         = _create_calibrated_v2
