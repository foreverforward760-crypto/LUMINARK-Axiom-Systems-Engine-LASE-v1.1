"""
nsdt_engine_v8.py – LUMINARK v8 Unified Field Engine.

Extends NSDataTEngine v7 with the unified field equation (sap_unified_field.py).
All v7 public methods are preserved via inheritance. New in v8:
  - unified_field_value(): compute U for a given NSDT state and true stage
  - unified_field_gradient(): ∂U/∂x for intervention targeting
  - analyze_full() extended with unified_field sub-dict

FLAW CORRECTIONS (vs submitted document):
  [6] datetime was not imported → NameError in get_velocity(). Fixed.
  [7] unified_field() accepted NSDataT object but tests pass raw np.ndarray.
      Renamed / split into unified_field_value() (accepts NSDataT) and
      unified_field_raw() (accepts raw array) for unambiguous interface.
  [8] "Methods omitted for brevity" skeleton was non-functional. Fixed by
      inheriting from NSDataTEngine (v7) — all methods present automatically.
"""

import datetime
import numpy as np
from typing import Dict, List, Optional, Tuple

from build3_active_defense.nsdt_engine_v7 import (
    NSDataTEngine as _NSDataTEngineV7,
    NSDataT, TrapScoreResult, TemporalSnapshot, STAGE_LABELS
)
from sap_unified_field import UnifiedField

# Re-export dataclasses so callers only need to import from this module
__all__ = [
    "NSDataTEngineV8", "NSDataT", "TrapScoreResult", "TemporalSnapshot",
    "STAGE_LABELS", "UnifiedField",
]


class NSDataTEngineV8(_NSDataTEngineV7):
    """
    v8 engine: all v7 capabilities + unified field equation.

    Inherits from NSDataTEngine (v7) — every v7 method is available unchanged.
    Adds unified field computation on top without modifying existing behaviour.
    """

    def __init__(self,
                 temperature: float = 0.5,
                 beta: float = 0.8,
                 w_H: float = 1.0,
                 w_E: float = 2.0,
                 w_v: float = 0.5,
                 uf_beta: float = 1.0,
                 uf_gamma: float = 1.0,
                 uf_delta: float = 1.0):
        super().__init__(
            temperature=temperature, beta=beta,
            w_H=w_H, w_E=w_E, w_v=w_v,
        )
        self.unified = UnifiedField(
            beta=uf_beta, gamma=uf_gamma, delta=uf_delta,
        )

    # ------------------------------------------------------------------
    # Unified field interface
    # ------------------------------------------------------------------

    def unified_field_raw(self, x: np.ndarray, true_stage: int,
                           system_id: str = "default",
                           velocity: Optional[float] = None) -> float:
        """
        Compute unified field U for a raw NSDT array.

        Parameters
        ----------
        x          : np.ndarray of shape (5,) — raw NSDT values in [0, 10]
        true_stage : int — observed SAP stage (for cross-entropy term P)
        system_id  : str — used to retrieve prev_stage and velocity from history
        velocity   : float or None — if None, computed from history

        Returns
        -------
        float — U value
        """
        prev = self._prev_stage(system_id)
        if velocity is None:
            velocity = self.get_velocity(system_id)
        return self.unified.U(x, true_stage, prev_stage=prev, velocity=velocity)

    def unified_field_value(self, nsdt: NSDataT, true_stage: int,
                             system_id: str = "default") -> float:
        """
        Compute unified field U from an NSDataT object.
        Convenience wrapper around unified_field_raw().
        """
        x = np.array(nsdt.to_vector(), dtype=float)
        return self.unified_field_raw(x, true_stage, system_id)

    def unified_field_gradient(self, nsdt: NSDataT, true_stage: int,
                                system_id: str = "default") -> List[float]:
        """
        Finite-difference gradient ∂U/∂x for an NSDataT state.
        Returns List[float] of length 5 — one partial per NSDT dimension.
        Useful for intervention targeting: move x in the direction of -∇U.
        """
        x = np.array(nsdt.to_vector(), dtype=float)
        prev = self._prev_stage(system_id)
        velocity = self.get_velocity(system_id)
        return self.unified.gradient(x, true_stage, prev_stage=prev,
                                     velocity=velocity).tolist()

    def unified_field_components(self, nsdt: NSDataT, true_stage: int,
                                  system_id: str = "default") -> Dict:
        """
        Return all unified field components (P, E, L, U) for inspection.
        """
        x = np.array(nsdt.to_vector(), dtype=float)
        prev = self._prev_stage(system_id)
        velocity = self.get_velocity(system_id)
        return self.unified.components(x, true_stage, prev_stage=prev,
                                       velocity=velocity)

    # ------------------------------------------------------------------
    # Helper — prev stage (shared with v7 internals)
    # ------------------------------------------------------------------

    def _prev_stage(self, system_id: str) -> Optional[int]:
        hist = self._history.get(system_id, [])
        return hist[-1].stage if hist else None

    # ------------------------------------------------------------------
    # Extended analyze_full — superset of v7 output
    # ------------------------------------------------------------------

    def analyze_full(self, nsdt: NSDataT, system_id: str = "default",
                     true_stage: Optional[int] = None) -> Dict:
        """
        Complete v8 analysis.
        If true_stage is provided, includes unified field components.
        All v7 keys are preserved exactly.
        """
        result = super().analyze_full(nsdt, system_id)

        if true_stage is not None:
            uf_components = self.unified_field_components(nsdt, true_stage, system_id)
            uf_grad = self.unified_field_gradient(nsdt, true_stage, system_id)
            result["unified_field"] = {
                **uf_components,
                "gradient": [round(g, 6) for g in uf_grad],
                "true_stage_input": true_stage,
            }

        return result
