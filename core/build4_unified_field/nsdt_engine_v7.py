"""
nsdt_engine_v7.py – Hybrid NSDataTEngine with Lyapunov stability layer.
Extends v6.5 with a Lyapunov controller for provable defense guarantees.
Drop‑in replacement for v6.5 engine (adds new outputs, no breaking changes).
"""

import math
import datetime
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

# v6.5 core modules
from sap_geometry_engine import SAPGeometry, STAGE_CENTROIDS, AXIS_WEIGHTS, AXIS_SCALES
from sap_energy_layer import SAPEnergy
from sap_constrained_bayesian import SAPConstrainedBayesian
from sap_lyapunov import LyapunovController

# Legacy data structures (same as v6.5)
STAGE_LABELS = {
    0: ("PLENARA", "Dormant/Reserve", "Fully quiescent — optimal reserve margin"),
    1: ("SEED", "Initializing", "Component spin-up, first load uptake"),
    2: ("EMERGENCE", "Early Operational", "Activating subsystems, load rising normally"),
    3: ("BREAKTHROUGH", "Peak Performance", "Maximum efficiency — breakthrough output"),
    4: ("FOUNDATION", "Stable Baseline", "Normal ops, healthy redundancy active"),
    5: ("THRESHOLD", "Pre-Stress Warning", "Approaching operational limits — MONITOR"),
    6: ("EXPRESSION", "Adaptive Stress", "System compensating — WATCH CLOSELY"),
    7: ("CRISIS", "Failure Trajectory", "Cascading risk detected — INTERVENE NOW"),
    8: ("RIGIDITY", "Permanence Trap", "Adaptation blocked — EMERGENCY PROTOCOL"),
    9: ("VOID", "Terminal/Renewal", "Forced shutdown OR full restoration"),
}

@dataclass
class NSDataT:
    complexity: float = 5.0
    stability: float = 5.0
    tension: float = 5.0
    adaptability: float = 5.0
    coherence: float = 5.0
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    source: str = "manual"
    domain: str = "power_grid"

    def to_dict(self) -> Dict:
        return {
            "complexity": self.complexity,
            "stability": self.stability,
            "tension": self.tension,
            "adaptability": self.adaptability,
            "coherence": self.coherence,
            "timestamp": self.timestamp,
            "source": self.source,
            "domain": self.domain,
        }

@dataclass
class TrapScoreResult:
    raw_score: float = 0.0
    normalized_score: float = 0.0
    rigidity_index: float = 0.0
    adaptability_norm: float = 0.0
    stage: int = 0
    risk_level: str = "LOW"

    @property
    def alert_color(self) -> str:
        return {"LOW": "GREEN", "MODERATE": "YELLOW",
                "HIGH": "ORANGE", "CRITICAL": "RED"}.get(self.risk_level, "GRAY")

@dataclass
class TemporalSnapshot:
    timestamp: str
    nsdt: NSDataT
    stage: int
    trap_score: float
    domain: str
    event_tag: str = ""


class NSDataTEngine:
    """
    v7 engine: v6.5 core + Lyapunov stability layer.
    Adds Lyapunov function and action recommendation without breaking existing APIs.
    """

    def __init__(self, temperature: float = 0.5, beta: float = 0.8,
                 w_H: float = 1.0, w_E: float = 2.0, w_v: float = 0.5):
        self.bayesian = SAPConstrainedBayesian(temperature=temperature, beta=beta)
        self.geometry = SAPGeometry()
        self.energy = SAPEnergy()
        self.lyapunov = LyapunovController(w_H=w_H, w_E=w_E, w_v=w_v)
        self._history: Dict[str, List[TemporalSnapshot]] = {}

    # ------------------------------------------------------------------
    # Core public methods (same signatures as v6.5)
    # ------------------------------------------------------------------

    def calculate_stage(self, nsdt: NSDataT, system_id: str = "default") -> int:
        x = [nsdt.complexity, nsdt.stability, nsdt.tension,
             nsdt.adaptability, nsdt.coherence]
        result = self.bayesian.forward(x)
        raw_stage = result["dominant_stage"]
        prev = None
        if system_id in self._history and self._history[system_id]:
            prev = self._history[system_id][-1].stage
        stage, _ = self.geometry.enforce_geometry(prev, raw_stage)
        return stage

    def calculate_micro_position(self, nsdt: NSDataT, stage: int) -> float:
        x = [nsdt.complexity, nsdt.stability, nsdt.tension,
             nsdt.adaptability, nsdt.coherence]
        return self.geometry.compute_micro_position(
            x, stage, STAGE_CENTROIDS, AXIS_WEIGHTS, AXIS_SCALES
        )

    def calculate_trap_score(self, nsdt: NSDataT, stage: int) -> Tuple[TrapScoreResult, List[float]]:
        x = [nsdt.complexity, nsdt.stability, nsdt.tension,
             nsdt.adaptability, nsdt.coherence]
        result = self.bayesian.forward(x)
        posterior = np.array(result["posterior"])
        energy = self.energy.compute_total_energy(x, posterior)
        normalized = min(100.0, energy * 100.0)
        grad = self.energy.compute_gradient(x, posterior)
        rigidity = (nsdt.tension + (10.0 - nsdt.stability)) / 20.0
        adapt_norm = nsdt.adaptability / 10.0
        if normalized < 25: risk = "LOW"
        elif normalized < 50: risk = "MODERATE"
        elif normalized < 75: risk = "HIGH"
        else: risk = "CRITICAL"
        trap_result = TrapScoreResult(
            raw_score=energy,
            normalized_score=round(normalized, 1),
            rigidity_index=round(rigidity, 3),
            adaptability_norm=round(adapt_norm, 3),
            stage=stage,
            risk_level=risk,
        )
        return trap_result, grad

    def calculate_trap_score_legacy(self, nsdt: NSDataT, stage: int) -> TrapScoreResult:
        trap, _ = self.calculate_trap_score(nsdt, stage)
        return trap

    def check_inversion_principle(self, nsdt: NSDataT, stage: int) -> Dict:
        x = [nsdt.complexity, nsdt.stability, nsdt.tension,
             nsdt.adaptability, nsdt.coherence]
        result = self.bayesian.forward(x)
        meta = self.geometry.get_metadata(stage)
        inversion_active = (
            meta.get("physical_stability", True) and
            result["trap_energy"] > 0.6 and
            result["entropy"] < 1.0
        )
        if stage == 8:
            inv_type = "RIGIDITY_COLLAPSE"
        elif inversion_active:
            inv_type = "STRUCTURAL_OVERSTABILITY"
        else:
            inv_type = "NONE"
        physical_stability = nsdt.stability / 10.0
        conscious_proxy = nsdt.coherence / 10.0
        stage8_signature = (stage == 8 and nsdt.stability >= 7.0 and nsdt.adaptability <= 3.0)
        uri_pattern = (nsdt.stability >= 6.5 and nsdt.tension >= 7.5 and nsdt.adaptability <= 2.5)
        return {
            "inversion_active": inversion_active,
            "inversion_type": inv_type,
            "physical_stability": round(physical_stability, 2),
            "adaptive_coherence": round(conscious_proxy, 2),
            "stage8_signature": stage8_signature,
            "uri_pattern_detected": uri_pattern,
            "warning": ("INVERSION ACTIVE – structural stability masks internal brittleness."
                        if inversion_active else "No inversion detected."),
            "sap_context": meta.get("name", ""),
        }

    def predict_trajectory(self, history: List[TemporalSnapshot]) -> Dict:
        if len(history) < 2:
            return {"prediction": "INSUFFICIENT_DATA", "confidence": 0.0}
        recent = history[-5:]
        expected = []
        entropy_vals = []
        for snap in recent:
            x = [snap.nsdt.complexity, snap.nsdt.stability, snap.nsdt.tension,
                 snap.nsdt.adaptability, snap.nsdt.coherence]
            res = self.bayesian.forward(x)
            expected.append(res["expected_stage"])
            entropy_vals.append(res["entropy"])
        if len(expected) < 2:
            return {"prediction": "INSUFFICIENT_DATA", "confidence": 0.0}
        velocity = expected[-1] - expected[0]
        entropy_delta = entropy_vals[-1] - entropy_vals[0]
        if velocity > 1.5 and entropy_delta < -0.2:
            trajectory = "LOCKING_IN_FAILURE"
            warning_hours = 6
            confidence = 0.92
        elif velocity > 1.0:
            trajectory = "ACCELERATING_RISK"
            warning_hours = 12
            confidence = 0.85
        elif velocity < -1.0:
            trajectory = "RECOVERY"
            warning_hours = 72
            confidence = 0.80
        elif entropy_vals[-1] > 2.0:
            trajectory = "UNSTABLE_UNCERTAIN"
            warning_hours = 24
            confidence = 0.70
        else:
            trajectory = "STABLE"
            warning_hours = 72
            confidence = 0.65
        stages = [s.stage for s in recent]
        traps = [s.trap_score for s in recent]
        stage_trend = stages[-1] - stages[0]
        trap_trend = traps[-1] - traps[0] if len(traps) > 1 else 0
        return {
            "trajectory": trajectory,
            "current_stage": stages[-1],
            "stage_trend": stage_trend,
            "trap_trend": round(trap_trend, 3),
            "warning_window_hours": warning_hours,
            "confidence": confidence,
            "velocity": round(velocity, 3),
            "entropy_delta": round(entropy_delta, 3),
            "recommended_action": self._get_action(trajectory, stages[-1]),
        }

    def _get_action(self, trajectory: str, stage: int) -> str:
        if trajectory in ("LOCKING_IN_FAILURE", "ACCELERATING_RISK") or stage >= 8:
            return "EMERGENCY_PROTOCOL: Immediate intervention required"
        if trajectory == "UNSTABLE_UNCERTAIN" or stage == 7:
            return "ELEVATED_ALERT: Increase monitoring, prepare for escalation"
        if stage >= 5:
            return "WATCH_ALERT: Monitor every 15 minutes"
        if stage == 4:
            return "ROUTINE: Continue scheduled maintenance"
        if stage <= 2:
            return "OPTIMIZE: System underutilized"
        return "MONITOR: Standard observation"

    # ------------------------------------------------------------------
    # New v7 methods: Lyapunov stability
    # ------------------------------------------------------------------

    def get_velocity(self, system_id: str) -> float:
        """Compute current stage velocity from history."""
        hist = self.get_history(system_id)
        if len(hist) < 2:
            return 0.0
        latest = hist[-1]
        prev = hist[-2]
        try:
            t1 = datetime.datetime.fromisoformat(prev.timestamp).timestamp()
            t2 = datetime.datetime.fromisoformat(latest.timestamp).timestamp()
            dt = max(0.001, t2 - t1)
        except Exception:
            dt = 1.0
        return (latest.stage - prev.stage) / dt

    def recommend_defense_action(self, nsdt: NSDataT, system_id: str = "default") -> str:
        """
        Lyapunov-based defense action recommendation.
        Uses current entropy, energy, velocity, and cynical loop detection.
        """
        # Compute entropy and energy from Bayesian forward
        x = [nsdt.complexity, nsdt.stability, nsdt.tension,
             nsdt.adaptability, nsdt.coherence]
        result = self.bayesian.forward(x)
        entropy = result["entropy"]
        energy = result["trap_energy"]  # from Bayesian (same as raw trap score)
        velocity = self.get_velocity(system_id)
        cynical = self._detect_cynical_loop(system_id)
        return self.lyapunov.recommend_action(entropy, energy, velocity, cynical)

    def _detect_cynical_loop(self, system_id: str, window: int = 10) -> bool:
        """Detect 8↔7 oscillation pattern in history."""
        hist = self.get_history(system_id)
        if len(hist) < 3:
            return False
        stages = [s.stage for s in hist[-window:]]
        # Look for 8→7→8 or 7↔8 oscillations
        for i in range(len(stages)-2):
            if stages[i] == 8 and stages[i+1] == 7 and stages[i+2] == 8:
                return True
        alt = sum(1 for i in range(len(stages)-1) if stages[i] in (7,8) and stages[i+1] in (7,8) and stages[i] != stages[i+1])
        return alt >= 2

    # ------------------------------------------------------------------
    # Extended analysis (includes Lyapunov)
    # ------------------------------------------------------------------

    def analyze_full(self, nsdt: NSDataT, system_id: str = "default") -> Dict:
        """
        Complete analysis with Lyapunov stability.
        Returns all v6.5 outputs plus Lyapunov V and recommended action.
        """
        x = [nsdt.complexity, nsdt.stability, nsdt.tension,
             nsdt.adaptability, nsdt.coherence]
        result = self.bayesian.forward(x)
        stage = self.calculate_stage(nsdt, system_id)
        micro = self.calculate_micro_position(nsdt, stage)
        trap_result, grad = self.calculate_trap_score(nsdt, stage)
        inversion = self.check_inversion_principle(nsdt, stage)
        velocity = self.get_velocity(system_id)
        entropy = result["entropy"]
        energy = trap_result.raw_score
        cynical = self._detect_cynical_loop(system_id)
        lyapunov_V = self.lyapunov.V(entropy, energy, velocity)
        recommended_action = self.lyapunov.recommend_action(entropy, energy, velocity, cynical)

        return {
            "stage": stage,
            "expected_stage": result["expected_stage"],
            "micro_position": micro,
            "posterior": result["posterior"],
            "entropy": entropy,
            "trap_energy": energy,
            "trap_normalized": trap_result.normalized_score,
            "energy_gradient": grad,
            "arc": result["arc"],
            "geometric_valid": result["geometric_valid"],
            "inversion_active": inversion["inversion_active"],
            "inversion_type": inversion["inversion_type"],
            "stage_metadata": result["stage_metadata"],
            "lyapunov": {
                "V": lyapunov_V,
                "recommended_action": recommended_action,
                "weights": {"w_H": self.lyapunov.w_H, "w_E": self.lyapunov.w_E, "w_v": self.lyapunov.w_v},
                "cynical_loop_detected": cynical,
            },
        }

    # ------------------------------------------------------------------
    # History management
    # ------------------------------------------------------------------

    def record_snapshot(self, system_id: str, nsdt: NSDataT, event_tag: str = "") -> TemporalSnapshot:
        stage = self.calculate_stage(nsdt, system_id)
        trap_result, _ = self.calculate_trap_score(nsdt, stage)
        snap = TemporalSnapshot(
            timestamp=nsdt.timestamp,
            nsdt=nsdt,
            stage=stage,
            trap_score=trap_result.raw_score,
            domain=nsdt.domain,
            event_tag=event_tag,
        )
        self._history.setdefault(system_id, []).append(snap)
        if len(self._history[system_id]) > 500:
            self._history[system_id] = self._history[system_id][-500:]
        return snap

    def get_history(self, system_id: str) -> List[TemporalSnapshot]:
        return self._history.get(system_id, [])
