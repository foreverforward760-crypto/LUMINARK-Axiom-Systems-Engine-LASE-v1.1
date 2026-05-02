"""
NSDataTEngine v6.5 – Drop-in replacement class for LatestLUMINARK_OVERWATCH_PRIME_ULTRA.py
Geometry as hard boundary, energy as field, posterior-driven trajectory, emergent inversion.

INTEGRATION INSTRUCTIONS:
1. Add to imports at top of LatestLUMINARK_OVERWATCH_PRIME_ULTRA.py:
       from sap_geometry_engine import SAPGeometry, STAGE_CENTROIDS, AXIS_WEIGHTS, AXIS_SCALES
       from sap_energy_layer import SAPEnergy
       from sap_constrained_bayesian import SAPConstrainedBayesian
2. Replace the existing `class NSDataTEngine` block entirely with the class below.
3. All other classes (domain analyzers, defense systems, etc.) remain unchanged.
"""

from typing import Dict, List, Tuple, Optional
import numpy as np

from sap_geometry_engine import SAPGeometry, STAGE_CENTROIDS, AXIS_WEIGHTS, AXIS_SCALES
from sap_energy_layer import SAPEnergy
from sap_constrained_bayesian import SAPConstrainedBayesian
from sap_datastructures import NSDataT, TrapScoreResult, TemporalSnapshot


class NSDataTEngine:
    """
    v6.5 engine: geometry as hard boundary, energy as field,
    posterior‑driven trajectory, emergent inversion.
    Drop‑in replacement for legacy engine.
    """

    def __init__(self, temperature: float = 0.5, beta: float = 0.8):
        self.bayesian = SAPConstrainedBayesian(temperature=temperature, beta=beta)
        self.geometry = SAPGeometry()
        self.energy = SAPEnergy()
        self._history: Dict[str, List] = {}

    # ------------------------------------------------------------------
    # Core public methods (same signatures as legacy)
    # ------------------------------------------------------------------

    def calculate_stage(self, nsdt, system_id: str = "default") -> int:
        """
        Return integer stage, geometrically enforced.
        """
        x = [nsdt.complexity, nsdt.stability, nsdt.tension,
             nsdt.adaptability, nsdt.coherence]
        result = self.bayesian.forward(x)
        raw_stage = result["dominant_stage"]

        # Get previous stage from history
        prev = None
        if system_id in self._history and self._history[system_id]:
            prev = self._history[system_id][-1].stage

        # Hard geometric enforcement
        stage, _ = self.geometry.enforce_geometry(prev, raw_stage)
        return stage

    def calculate_micro_position(self, nsdt, stage: int) -> float:
        """
        Geometric projection onto centroid‑to‑next‑centroid line.
        """
        x = [nsdt.complexity, nsdt.stability, nsdt.tension,
             nsdt.adaptability, nsdt.coherence]
        return self.geometry.compute_micro_position(
            x, stage, STAGE_CENTROIDS, AXIS_WEIGHTS, AXIS_SCALES
        )

    def calculate_trap_score(self, nsdt, stage: int):
        """
        Returns (TrapScoreResult, energy_gradient).
        Energy is a true field (0‑1), not a scaled score.
        """
        x = [nsdt.complexity, nsdt.stability, nsdt.tension,
             nsdt.adaptability, nsdt.coherence]
        result = self.bayesian.forward(x)
        posterior = np.array(result["posterior"])

        # Total energy (field)
        energy = self.energy.compute_total_energy(x, posterior)
        normalized = min(100.0, energy * 100.0)

        # Gradient of energy field
        grad = self.energy.compute_gradient(x, posterior)

        # Legacy metrics for compatibility
        rigidity = (nsdt.tension + (10.0 - nsdt.stability)) / 20.0
        adapt_norm = nsdt.adaptability / 10.0

        if normalized < 25:
            risk = "LOW"
        elif normalized < 50:
            risk = "MODERATE"
        elif normalized < 75:
            risk = "HIGH"
        else:
            risk = "CRITICAL"

        trap_result = TrapScoreResult(
            raw_score=energy,
            normalized_score=round(normalized, 1),
            rigidity_index=round(rigidity, 3),
            adaptability_norm=round(adapt_norm, 3),
            stage=stage,
            risk_level=risk,
        )
        return trap_result, grad

    # Legacy compatibility: single return version (ignores gradient)
    def calculate_trap_score_legacy(self, nsdt, stage: int):
        trap, _ = self.calculate_trap_score(nsdt, stage)
        return trap

    def check_inversion_principle(self, nsdt, stage: int) -> Dict:
        """
        Emergent inversion: active when stage's physical stability flag
        coincides with high trap energy and low entropy.
        """
        x = [nsdt.complexity, nsdt.stability, nsdt.tension,
             nsdt.adaptability, nsdt.coherence]
        result = self.bayesian.forward(x)
        meta = self.geometry.get_metadata(stage)

        # Inversion emerges from energy + entropy, not heuristic thresholds
        inversion_active = (
            meta.get("physical_stability", True) and
            result["trap_energy"] > 0.6 and
            result["entropy"] < 1.0
        )

        # Determine inversion type
        if stage == 8:
            inv_type = "RIGIDITY_COLLAPSE"
        elif inversion_active:
            inv_type = "STRUCTURAL_OVERSTABILITY"
        else:
            inv_type = "NONE"

        # Legacy fields for compatibility
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
            "warning": (
                "INVERSION ACTIVE – structural stability masks internal brittleness."
                if inversion_active else
                "No inversion detected."
            ),
            "sap_context": meta.get("name", ""),
        }

    def predict_trajectory(self, history: List) -> Dict:
        """
        Posterior‑driven trajectory: uses expected stage velocity and entropy delta.
        """
        if len(history) < 2:
            return {"prediction": "INSUFFICIENT_DATA", "confidence": 0.0}

        recent = history[-5:]  # use up to 5 snapshots
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

        # Determine trajectory
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

        # Legacy fields
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
    # Extended method – single truth source
    # ------------------------------------------------------------------

    def analyze_full(self, nsdt, system_id: str = "default") -> Dict:
        """
        Complete analysis: returns all v6.5 outputs.
        This is the single source of truth for the engine.
        """
        x = [nsdt.complexity, nsdt.stability, nsdt.tension,
             nsdt.adaptability, nsdt.coherence]
        result = self.bayesian.forward(x)
        stage = self.calculate_stage(nsdt, system_id)
        micro = self.calculate_micro_position(nsdt, stage)
        trap_result, grad = self.calculate_trap_score(nsdt, stage)
        inversion = self.check_inversion_principle(nsdt, stage)

        return {
            "stage": stage,
            "expected_stage": result["expected_stage"],
            "micro_position": micro,
            "posterior": result["posterior"],
            "entropy": result["entropy"],
            "trap_energy": trap_result.raw_score,
            "trap_normalized": trap_result.normalized_score,
            "energy_gradient": grad,
            "arc": result["arc"],
            "geometric_valid": result["geometric_valid"],
            "inversion_active": inversion["inversion_active"],
            "inversion_type": inversion["inversion_type"],
            "stage_metadata": result["stage_metadata"],
        }

    # ------------------------------------------------------------------
    # History management (for trajectory)
    # ------------------------------------------------------------------

    def record_snapshot(self, system_id: str, nsdt, event_tag: str = ""):
        """Record a snapshot for trajectory prediction."""
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
        # Keep history bounded
        if len(self._history[system_id]) > 500:
            self._history[system_id] = self._history[system_id][-500:]
        return snap

    def get_history(self, system_id: str) -> List:
        return self._history.get(system_id, [])
