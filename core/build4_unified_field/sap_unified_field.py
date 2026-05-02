"""
sap_unified_field.py  –  Unified Field equation for LUMINARK v8.

Combines geometric constraint violation, cross-entropy (negative log-posterior),
trap energy, and Lyapunov into a single differentiable scalar field:

    U = α·G + β·P + γ·E + δ·L

All four components are functions of the NSDT vector x ∈ R^5.
Gradients are computed via central finite differences (verified correct to 1e-5
tolerance in test_harness_v8.py).

FLAW-4 CORRECTION: gradient() previously returned np.zeros(5) unconditionally.
  Now computes real finite-difference gradient of U w.r.t. x.

FLAW-5 CORRECTION: _geometric_violation() previously took a 'true_stage' label
  and compared it against prev_stage.  That conflates supervised labels with
  geometric inference.  The correct formulation asks: "does the *geometric mask*
  from prev_stage rule out the posterior-dominant stage?" — a pure inference
  question that requires no ground-truth label.  The G term is now computed as
  the fraction of posterior mass placed on geometrically forbidden stages.
"""

import numpy as np
from typing import Optional

from sap_geometry_engine import SAPGeometry, ADJACENCY_MATRIX
from sap_energy_layer import SAPEnergy
from sap_constrained_bayesian import SAPConstrainedBayesian
from sap_lyapunov import LyapunovController


class UnifiedField:
    """
    Unified Field  U = α·G + β·P + γ·E + δ·L
    where:
      G = geometric violation mass: fraction of posterior on forbidden stages
          (0 if no prev_stage; rises toward 1 if mass concentrates on forbidden)
      P = negative log-posterior of dominant stage (cross-entropy / surprise)
      E = total trap energy (expectation of per-stage energy over posterior)
      L = Lyapunov function  V = w_H·H + w_E·E + w_v·v²

    All four terms are non-negative scalars, so U >= 0 always.
    """

    def __init__(
        self,
        alpha: float = 1.0,
        beta: float = 1.0,
        gamma: float = 1.0,
        delta: float = 1.0,
        temperature: float = 0.5,
        bay_beta: float = 0.8,
        w_H: float = 1.0,
        w_E: float = 2.0,
        w_v: float = 0.5,
    ):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.bayesian = SAPConstrainedBayesian(temperature=temperature, beta=bay_beta)
        self.lyapunov = LyapunovController(w_H=w_H, w_E=w_E, w_v=w_v)

    # ------------------------------------------------------------------
    # Component helpers
    # ------------------------------------------------------------------

    def _posterior(self, x: np.ndarray, prev_stage: Optional[int]) -> np.ndarray:
        """Geometric-masked posterior over 10 stages."""
        return self.bayesian.posterior(x, prev_stage=prev_stage)

    def _geometric_violation(self, post: np.ndarray, prev_stage: Optional[int]) -> float:
        """
        G = total posterior mass on stages forbidden by the adjacency matrix.

        If there is no prev_stage, no stage is forbidden → G = 0.
        Uses ADJACENCY_MATRIX directly so it stays consistent with the geometry
        engine's formal transition law (not just the ±1 delta clamp).
        """
        if prev_stage is None:
            return 0.0
        mask = ADJACENCY_MATRIX[prev_stage]          # shape (10,)
        forbidden_mass = float(np.sum(post[mask == 0]))
        return min(1.0, max(0.0, forbidden_mass))    # clamp to [0,1]

    def _cross_entropy(self, post: np.ndarray) -> float:
        """P = −log p(dominant stage).  Measures surprise / uncertainty."""
        dominant = int(np.argmax(post))
        p_dom = max(post[dominant], 1e-12)
        return -np.log(p_dom)

    def _expected_energy(self, x: np.ndarray, post: np.ndarray) -> float:
        """E = Σ p(s) · trap_energy(s, x)."""
        return SAPEnergy.compute_total_energy(x.tolist(), post)

    def _lyapunov_value(
        self, x: np.ndarray, post: np.ndarray, energy: float, velocity: float
    ) -> float:
        """L = V(entropy, energy, velocity)."""
        entropy = float(-np.sum(post * np.log(post + 1e-12)))
        return self.lyapunov.V(entropy, energy, velocity)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def components(
        self,
        x: np.ndarray,
        prev_stage: Optional[int] = None,
        velocity: float = 0.0,
    ) -> dict:
        """
        Compute all four field components and return them as a dict.
        Useful for debugging / logging.
        """
        post = self._posterior(x, prev_stage)
        G = self._geometric_violation(post, prev_stage)
        P = self._cross_entropy(post)
        E = self._expected_energy(x, post)
        L = self._lyapunov_value(x, post, E, velocity)
        return {"G": G, "P": P, "E": E, "L": L}

    def U(
        self,
        x: np.ndarray,
        prev_stage: Optional[int] = None,
        velocity: float = 0.0,
    ) -> float:
        """
        Compute unified field value U.
        x must be a 1-D array of shape (5,), values in [0, 10].
        """
        post = self._posterior(x, prev_stage)
        G = self._geometric_violation(post, prev_stage)
        P = self._cross_entropy(post)
        E = self._expected_energy(x, post)
        L = self._lyapunov_value(x, post, E, velocity)
        return self.alpha * G + self.beta * P + self.gamma * E + self.delta * L

    def gradient(
        self,
        x: np.ndarray,
        prev_stage: Optional[int] = None,
        velocity: float = 0.0,
        epsilon: float = 1e-5,
    ) -> np.ndarray:
        """
        Central finite-difference gradient of U w.r.t. x.
        Returns shape (5,) float64 array.

        FLAW-4 FIX: Previous implementation returned np.zeros(5).
        This correctly perturbs each dimension individually.
        """
        grad = np.empty(5, dtype=np.float64)
        for i in range(5):
            x_plus = x.copy()
            x_plus[i] += epsilon
            x_minus = x.copy()
            x_minus[i] -= epsilon
            grad[i] = (self.U(x_plus, prev_stage, velocity)
                       - self.U(x_minus, prev_stage, velocity)) / (2.0 * epsilon)
        return grad
