"""
sap_constrained_bayesian.py – Constrained Bayesian SAP Inference
Shared by Build 1 (Overwatch Strict) and Build 3 (Active Defense).

Computes a posterior distribution over 10 SAP stages using weighted
centroid distances, energy modulation, and geometric transition masking.
"""

import numpy as np
from typing import Dict, List, Optional
from sap_geometry_engine import (
    SAPGeometry, STAGE_CENTROIDS, STAGE_METADATA,
    AXIS_WEIGHTS, AXIS_SCALES
)
from sap_energy_layer import SAPEnergy


class SAPConstrainedBayesian:
    """
    Bayesian SAP stage estimator with:
    - Weighted normalised distance logits
    - Energy field modulation (beta coefficient)
    - Geometric adjacency masking (hard constraint)
    - Softmax with temperature
    """

    def __init__(self, temperature: float = 0.5, beta: float = 0.8):
        self.temperature = temperature
        self.beta = beta
        self.centroids = {k: np.array(v, dtype=float) for k, v in STAGE_CENTROIDS.items()}
        self.weights = np.array(AXIS_WEIGHTS)
        self.scales = np.array(AXIS_SCALES)
        self._prev_stage: Optional[int] = None

    def _weighted_distance(self, x: np.ndarray, centroid: np.ndarray) -> float:
        diff = (x - centroid) / self.scales
        return float(np.sqrt(np.sum(self.weights * diff * diff)))

    def _raw_logits(self, x: np.ndarray) -> np.ndarray:
        return np.array([
            -self._weighted_distance(x, self.centroids[s])
            for s in range(10)
        ])

    def posterior(self, x: np.ndarray,
                  prev_stage: Optional[int] = None) -> np.ndarray:
        logits = self._raw_logits(x)

        # Energy modulation
        logits = SAPEnergy.modulate_logits(logits, x.tolist(), self.beta)

        # Geometric mask
        if prev_stage is not None:
            mask = SAPGeometry.get_adjacency()[prev_stage]
            logits = np.where(mask > 0, logits, -np.inf)

        # Softmax with temperature
        temp = max(self.temperature, 0.05)
        logits = logits / temp
        finite = logits[np.isfinite(logits)]
        if len(finite) == 0:
            # All masked: return uniform over valid stages
            valid = np.isfinite(logits / (logits / temp))
            out = np.zeros(10)
            out[:] = 1.0 / 10.0
            return out
        logits = logits - np.max(finite)
        exp = np.where(np.isfinite(logits), np.exp(logits), 0.0)
        total = np.sum(exp)
        if total == 0:
            exp = np.ones(10) / 10.0
            total = 1.0
        return exp / total

    def forward(self, x: List[float],
                prev_stage: Optional[int] = None) -> Dict:
        """
        Full forward pass. Returns dict with all computed quantities.

        Parameters
        ----------
        x          : NSDT vector [C, S, T, A, Coh], each in [0, 10]
        prev_stage : previous SAP stage for geometric masking (optional)

        Returns
        -------
        dict with keys:
            posterior, dominant_stage, expected_stage, entropy,
            trap_energy, arc, geometric_valid, stage_metadata
        """
        x_arr = np.array(x, dtype=float)
        post = self.posterior(x_arr, prev_stage)

        dominant = int(np.argmax(post))
        expected = float(np.sum(np.arange(10) * post))
        entropy = float(-np.sum(post * np.log(post + 1e-12)))
        trap_energy = SAPEnergy.trap_energy(dominant, x)

        meta = STAGE_METADATA.get(dominant, {})
        arc = meta.get("arc", "unknown")

        # geometric_valid: was the dominant stage reachable from prev_stage?
        if prev_stage is not None:
            _, geo_msg = SAPGeometry.is_transition_allowed(prev_stage, dominant)
            geometric_valid = not geo_msg.startswith("geometric violation")
        else:
            geometric_valid = True

        return {
            "posterior": post.tolist(),
            "dominant_stage": dominant,
            "expected_stage": round(expected, 4),
            "entropy": round(entropy, 4),
            "trap_energy": round(trap_energy, 4),
            "arc": arc,
            "geometric_valid": geometric_valid,
            "stage_metadata": {
                "name": meta.get("name", ""),
                "arc": arc,
                "geometry": meta.get("geometry", ""),
            },
        }
