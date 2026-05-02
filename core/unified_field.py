"""
luminark/unified_field.py – UnifiedField facade for the luminark package.

Re-exports the UnifiedField class from the root-level sap_unified_field.py
(Build 4 core). This shim allows `from luminark import UnifiedField` to work
without requiring callers to navigate the build directory structure.

If the Build 4 module is not available (e.g. running only Build 1 in CI),
falls back to a lightweight stub that computes U = β·P + γ·E + δ·L
using only numpy — no cross-build imports required.
"""

from __future__ import annotations
import sys
import os

# Try to import the canonical UnifiedField from the root build4 module
try:
    # Root-level sap_unified_field.py (same directory as nsdt_engine_v8.py)
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _root not in sys.path:
        sys.path.insert(0, _root)
    from sap_unified_field import UnifiedField  # type: ignore
except ImportError:
    # Fallback stub — sufficient for package imports and type hints
    import numpy as np
    from typing import Optional

    class UnifiedField:  # type: ignore[no-redef]
        """
        Lightweight stub UnifiedField for environments where Build 4
        dependencies (sap_geometry_engine, sap_energy_layer, etc.) are not
        installed.  Provides the same public interface with simplified math.
        """

        def __init__(self, beta: float = 1.0, gamma: float = 1.0, delta: float = 1.0):
            self.beta  = beta
            self.gamma = gamma
            self.delta = delta

        def U(self, x: "np.ndarray", true_stage: int,
              prev_stage: Optional[int] = None,
              velocity: float = 0.0) -> float:
            """Stub: returns a simple scalar based on NSDT distance from true_stage."""
            P = float(np.mean(np.abs(x - true_stage)))
            E = float(np.mean(x) / 10.0)
            L = float(velocity ** 2 * 0.5)
            return self.beta * P + self.gamma * E + self.delta * L

        def gradient(self, x: "np.ndarray", true_stage: int,
                     prev_stage: Optional[int] = None,
                     velocity: float = 0.0,
                     epsilon: float = 1e-5) -> "np.ndarray":
            """Central finite-difference gradient (stub implementation)."""
            grad = np.zeros(len(x))
            for i in range(len(x)):
                xp = x.copy(); xp[i] += epsilon
                xm = x.copy(); xm[i] -= epsilon
                grad[i] = (self.U(xp, true_stage, prev_stage, velocity) -
                           self.U(xm, true_stage, prev_stage, velocity)) / (2 * epsilon)
            return grad

        def components(self, x: "np.ndarray", true_stage: int,
                       prev_stage: Optional[int] = None,
                       velocity: float = 0.0) -> dict:
            P = float(np.mean(np.abs(x - true_stage)))
            E = float(np.mean(x) / 10.0)
            L = float(velocity ** 2 * 0.5)
            return {
                "P": round(P, 6), "E": round(E, 6), "L": round(L, 6),
                "U": round(self.beta * P + self.gamma * E + self.delta * L, 6),
                "G": 0.0,
                "beta": self.beta, "gamma": self.gamma, "delta": self.delta,
            }


__all__ = ["UnifiedField"]
