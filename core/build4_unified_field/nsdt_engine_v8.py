"""
nsdt_engine_v8.py  –  LUMINARK Unified Field v8 Engine.

Extends NSDataTEngine (v7) with the unified field equation.
All v7 public methods are preserved unchanged (no breaking changes).

FLAW-6 FIX: datetime was not imported → NameError in get_velocity().
FLAW-7 FIX: Dual interface provided:
  - unified_field_value(nsdt, ...)  accepts NSDataT object (matches v7 convention)
  - unified_field_raw(x, ...)       accepts raw np.ndarray (matches test harness)
FLAW-8 FIX: Previously a non-functional skeleton with "methods omitted for brevity".
  Now properly inherits from NSDataTEngine (v7) so all v7 methods work.
"""

import datetime                                     # FLAW-6 FIX
import numpy as np
from typing import Dict, List, Optional, Tuple

from sap_geometry_engine import SAPGeometry, STAGE_CENTROIDS, AXIS_WEIGHTS, AXIS_SCALES
from sap_energy_layer import SAPEnergy
from sap_constrained_bayesian import SAPConstrainedBayesian
from sap_lyapunov import LyapunovController
from nsdt_engine_v7 import NSDataTEngine, NSDataT, TemporalSnapshot  # FLAW-8 FIX
from sap_unified_field import UnifiedField


class NSDataTEngineV8(NSDataTEngine):
    """
    v8 engine: unified field combining geometry, probability, energy, Lyapunov.

    All v7 methods (calculate_stage, calculate_trap_score, get_history, …)
    are inherited unchanged.  New additions:

      unified_field_value(nsdt, system_id, velocity)  →  float
      unified_field_raw(x, prev_stage, velocity)      →  float
      unified_field_gradient(x, prev_stage, velocity) →  np.ndarray
      unified_field_components(x, prev_stage, velocity) → dict
    """

    def __init__(
        self,
        temperature: float = 0.5,
        beta: float = 0.8,
        w_H: float = 1.0,
        w_E: float = 2.0,
        w_v: float = 0.5,
        uf_alpha: float = 1.0,
        uf_beta: float = 1.0,
        uf_gamma: float = 1.0,
        uf_delta: float = 1.0,
    ):
        super().__init__(
            temperature=temperature, beta=beta,
            w_H=w_H, w_E=w_E, w_v=w_v,
        )
        self.unified = UnifiedField(
            alpha=uf_alpha,
            beta=uf_beta,
            gamma=uf_gamma,
            delta=uf_delta,
            temperature=temperature,
            bay_beta=beta,
            w_H=w_H,
            w_E=w_E,
            w_v=w_v,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _nsdt_to_array(self, nsdt: NSDataT) -> np.ndarray:
        return np.array([
            nsdt.complexity, nsdt.stability, nsdt.tension,
            nsdt.adaptability, nsdt.coherence,
        ], dtype=np.float64)

    def _get_velocity(self, system_id: str) -> float:
        """Stage velocity from history.  Returns 0 if fewer than 2 snapshots."""
        hist = self.get_history(system_id)
        if len(hist) < 2:
            return 0.0
        latest = hist[-1]
        prev = hist[-2]
        try:
            t1 = datetime.datetime.fromisoformat(prev.timestamp).timestamp()   # FLAW-6 FIX
            t2 = datetime.datetime.fromisoformat(latest.timestamp).timestamp()
            dt = max(0.001, t2 - t1)
        except Exception:
            dt = 1.0
        return (latest.stage - prev.stage) / dt

    def _prev_stage_for(self, system_id: str) -> Optional[int]:
        """Return last recorded stage for system_id, or None."""
        hist = self.get_history(system_id)
        if hist:
            return hist[-1].stage
        return None

    # ------------------------------------------------------------------
    # Public unified-field API  (FLAW-7 FIX: dual interface)
    # ------------------------------------------------------------------

    def unified_field_value(
        self,
        nsdt: NSDataT,
        system_id: str = "default",
        velocity: Optional[float] = None,
    ) -> float:
        """
        Compute U for an NSDataT observation.
        Uses system history for prev_stage and velocity if not supplied.
        """
        x = self._nsdt_to_array(nsdt)
        prev_stage = self._prev_stage_for(system_id)
        if velocity is None:
            velocity = self._get_velocity(system_id)
        return self.unified.U(x, prev_stage=prev_stage, velocity=velocity)

    def unified_field_raw(
        self,
        x: np.ndarray,
        prev_stage: Optional[int] = None,
        velocity: float = 0.0,
    ) -> float:
        """
        Compute U directly from a raw NSDT ndarray.
        Useful for optimisation loops and the test harness.
        """
        return self.unified.U(x, prev_stage=prev_stage, velocity=velocity)

    def unified_field_gradient(
        self,
        x: np.ndarray,
        prev_stage: Optional[int] = None,
        velocity: float = 0.0,
    ) -> np.ndarray:
        """Finite-difference gradient of U w.r.t. x."""
        return self.unified.gradient(x, prev_stage=prev_stage, velocity=velocity)

    def unified_field_components(
        self,
        x: np.ndarray,
        prev_stage: Optional[int] = None,
        velocity: float = 0.0,
    ) -> dict:
        """Return breakdown of G, P, E, L components."""
        return self.unified.components(x, prev_stage=prev_stage, velocity=velocity)

    # ------------------------------------------------------------------
    # Full analysis (extended v7 analyse())
    # ------------------------------------------------------------------

    def analyse_v8(self, nsdt: NSDataT, system_id: str = "default") -> dict:
        """
        Full v8 analysis: all v7 outputs plus unified field value and components.
        """
        # Run v7 analysis
        v7 = self.analyze_full(nsdt, system_id)

        # Augment with v8 unified field
        x = self._nsdt_to_array(nsdt)
        prev = self._prev_stage_for(system_id)
        vel = self._get_velocity(system_id)
        uf_val = self.unified.U(x, prev_stage=prev, velocity=vel)
        uf_parts = self.unified.components(x, prev_stage=prev, velocity=vel)

        v7["unified_field"] = round(uf_val, 6)
        v7["unified_field_components"] = {k: round(v, 6) for k, v in uf_parts.items()}
        return v7
