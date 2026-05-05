"""
sap_unified_field.py – Unified Field equation for LUMINARK v8.

Combines cross‑entropy, trap energy, and Lyapunov into a single differentiable
scalar field U. Provides a finite-difference gradient (production-correct).

Field equation:
    U = β·P + γ·E + δ·L

Where:
  P = negative log‑posterior of true stage (cross‑entropy)
  E = total trap energy (expectation over posterior)
  L = Lyapunov function V(entropy, energy, velocity)
  β, γ, δ = weighting coefficients

FLAW CORRECTIONS (vs submitted document):
  [4] gradient() was a np.zeros(5) placeholder described as "analytic". Replaced
      with a correct finite-difference implementation over U(). Documented honestly.
      Analytic form is a roadmap item (v9).
  [5] _geometric_violation(prev_stage, true_stage) incorrectly mixed the ground-
      truth label into the transition check, conflating inference with supervision.
      Geometry is already enforced at the Bayesian layer (hard mask). G term
      removed from U; field simplified to U = β·P + γ·E + δ·L.
"""

import numpy as np
from typing import Optional
from sap_geometry_engine import SAPGeometry, STAGE_METADATA
from sap_energy_layer import SAPEnergy
from sap_constrained_bayesian import SAPConstrainedBayesian
from sap_lyapunov import LyapunovController


class UnifiedField:
    """
    Unified Field U = β·P + γ·E + δ·L

    P = cross-entropy (negative log-posterior of true stage)
    E = total trap energy (expectation over posterior)
    L = Lyapunov V(entropy, energy, velocity)

    Note on geometry: geometric constraints are enforced as a hard mask inside
    SAPConstrainedBayesian.posterior(). They are not a soft penalty in U — adding
    them as a differentiable penalty would conflate supervised labels with geometric
    inference. The Bayesian layer handles geometry correctly.
    """

    def __init__(self, beta: float = 1.0, gamma: float = 1.0, delta: float = 1.0):
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.bayesian = SAPConstrainedBayesian()
        self.lyapunov = LyapunovController()

    def _cross_entropy(self, x: np.ndarray, true_stage: int,
                       prev_stage: Optional[int] = None) -> float:
        """Negative log-posterior of the true stage (cross-entropy loss)."""
        post = self.bayesian.posterior(x, prev_stage=prev_stage)
        p_true = float(max(post[true_stage], 1e-12))
        return -np.log(p_true)

    def _expected_energy(self, x: np.ndarray,
                          prev_stage: Optional[int] = None) -> float:
        """Total trap energy — E[trap_energy(s, x)] over posterior."""
        post = self.bayesian.posterior(x, prev_stage=prev_stage)
        return SAPEnergy.compute_total_energy(x.tolist(), post)

    def _lyapunov_V(self, x: np.ndarray, velocity: float = 0.0,
                    prev_stage: Optional[int] = None) -> float:
        """Lyapunov function V(entropy, energy, velocity)."""
        post = self.bayesian.posterior(x, prev_stage=prev_stage)
        entropy = float(-np.sum(post * np.log(post + 1e-12)))
        energy = SAPEnergy.compute_total_energy(x.tolist(), post)
        return self.lyapunov.V(entropy, energy, velocity)

    def U(self, x: np.ndarray, true_stage: int,
          prev_stage: Optional[int] = None,
          velocity: float = 0.0) -> float:
        """
        Compute unified field value U for NSDT vector x.

        Parameters
        ----------
        x          : np.ndarray of shape (5,) — NSDT vector, values in [0, 10]
        true_stage : int — observed/ground-truth SAP stage (for cross-entropy P)
        prev_stage : Optional[int] — previous stage for geometric masking
        velocity   : float — stage velocity for Lyapunov term

        Returns
        -------
        float — scalar field value U ≥ 0
        """
        P = self._cross_entropy(x, true_stage, prev_stage)
        E = self._expected_energy(x, prev_stage)
        L = self._lyapunov_V(x, velocity, prev_stage)
        return self.beta * P + self.gamma * E + self.delta * L

    def gradient(self, x: np.ndarray, true_stage: int,
                 prev_stage: Optional[int] = None,
                 velocity: float = 0.0,
                 epsilon: float = 1e-5) -> np.ndarray:
        """
        Finite-difference gradient of U with respect to x (the NSDT vector).
        Returns np.ndarray of shape (5,).

        This is a correct, production-quality implementation using central differences.

        Note: True analytic gradients (via chain rule through softmax) are a v9
        roadmap item. Finite-difference is numerically equivalent and sufficient
        for intervention targeting and property-based testing.
        """
        grad = np.zeros(5)
        for i in range(5):
            x_plus = x.copy()
            x_plus[i] += epsilon
            U_plus = self.U(x_plus, true_stage, prev_stage, velocity)

            x_minus = x.copy()
            x_minus[i] -= epsilon
            U_minus = self.U(x_minus, true_stage, prev_stage, velocity)

            grad[i] = (U_plus - U_minus) / (2.0 * epsilon)
        return grad

    def components(self, x: np.ndarray, true_stage: int,
                   prev_stage: Optional[int] = None,
                   velocity: float = 0.0) -> dict:
        """
        Return all field components for inspection/debugging.
        """
        P = self._cross_entropy(x, true_stage, prev_stage)
        E = self._expected_energy(x, prev_stage)
        L = self._lyapunov_V(x, velocity, prev_stage)
        return {
            "P": round(P, 6),
            "E": round(E, 6),
            "L": round(L, 6),
            "U": round(self.beta * P + self.gamma * E + self.delta * L, 6),
            "beta": self.beta,
            "gamma": self.gamma,
            "delta": self.delta,
        }
