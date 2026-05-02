"""
SAP Geometry Engine v6.5 – Canonical state space, transition topology,
centroids, and geometric micro‑position projection.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional

# Stage metadata (complete)
STAGE_METADATA = {
    0: {"name": "Plenara", "geometry": "Sphere", "arc": "neutral",
        "physical_stability": True, "conscious_stability": True,
        "tumbling_energy_coeff": 0.1},
    1: {"name": "The Spark", "geometry": "Point", "arc": "descending",
        "physical_stability": False, "conscious_stability": True,
        "tumbling_energy_coeff": 0.2},
    2: {"name": "The Vessel", "geometry": "Line", "arc": "descending",
        "physical_stability": True, "conscious_stability": False,
        "tumbling_energy_coeff": 0.3},
    3: {"name": "The Engine", "geometry": "Triangle", "arc": "descending",
        "physical_stability": False, "conscious_stability": True,
        "tumbling_energy_coeff": 0.4},
    4: {"name": "The Crucible", "geometry": "Square", "arc": "descending",
        "physical_stability": True, "conscious_stability": False,
        "tumbling_energy_coeff": 0.5},
    5: {"name": "The Dynamo", "geometry": "Pentagon", "arc": "bifurcation",
        "physical_stability": False, "conscious_stability": True,
        "tumbling_energy_coeff": 0.6},
    6: {"name": "The Nexus", "geometry": "Hexagon", "arc": "ascending",
        "physical_stability": True, "conscious_stability": False,
        "tumbling_energy_coeff": 0.7},
    7: {"name": "The Lens", "geometry": "Heptagon", "arc": "ascending",
        "physical_stability": False, "conscious_stability": True,
        "tumbling_energy_coeff": 0.8},
    8: {"name": "The Vessel of Grounding", "geometry": "Octagon", "arc": "ascending",
        "physical_stability": True, "conscious_stability": False,
        "tumbling_energy_coeff": 0.9},
    9: {"name": "The Transparency", "geometry": "Nonagon", "arc": "ascending",
        "physical_stability": False, "conscious_stability": True,
        "tumbling_energy_coeff": 1.0},
}

# Canonical centroids (initial)
STAGE_CENTROIDS = {
    0: [0.0, 0.0, 0.0, 0.0, 0.0],
    1: [1.0, 8.0, 1.0, 1.0, 1.0],
    2: [2.0, 7.0, 2.0, 2.0, 2.0],
    3: [4.0, 7.0, 2.5, 3.0, 4.0],
    4: [3.5, 6.5, 3.0, 3.5, 5.0],
    5: [5.0, 4.0, 5.0, 5.0, 4.5],
    6: [6.0, 5.5, 4.0, 6.0, 6.5],
    7: [6.5, 3.0, 7.0, 7.0, 3.5],
    8: [7.5, 7.0, 8.0, 2.0, 2.0],
    9: [8.0, 2.0, 8.5, 1.5, 1.5],
}

# Axis weights and scales for distance
AXIS_WEIGHTS = [1.0, 1.5, 1.5, 1.0, 0.8]
AXIS_SCALES = [10.0, 10.0, 10.0, 10.0, 10.0]

# 10x10 adjacency matrix – formal transition law
ADJACENCY_MATRIX = np.zeros((10, 10))
for i in range(10):
    ADJACENCY_MATRIX[i, i] = 1.0          # self
    if i > 0:
        ADJACENCY_MATRIX[i, i-1] = 1.0    # backward
    if i < 9:
        ADJACENCY_MATRIX[i, i+1] = 1.0    # forward

# SAP‑specific hard rules
ADJACENCY_MATRIX[5, :5] = 0.0             # Stage 5 irreversible
ADJACENCY_MATRIX[8, :] = 0.0
ADJACENCY_MATRIX[8, 8] = 1.0
ADJACENCY_MATRIX[8, 9] = 1.0


class SAPGeometry:
    """Geometry layer – defines transition laws and spatial projection."""

    @staticmethod
    def get_adjacency() -> np.ndarray:
        return ADJACENCY_MATRIX.copy()

    @staticmethod
    def is_transition_allowed(prev: Optional[int], new: int) -> Tuple[bool, str]:
        if prev is None:
            return True, "initial"
        if ADJACENCY_MATRIX[prev, new] > 0:
            return True, f"allowed {prev}→{new}"
        return False, f"geometric violation {prev}→{new}"

    @staticmethod
    def get_metadata(stage: int) -> dict:
        return STAGE_METADATA.get(stage, {})

    @staticmethod
    def arc_from_stage(stage: int) -> str:
        return STAGE_METADATA[stage]["arc"]

    @staticmethod
    def weighted_normalised_distance(v1: List[float], v2: List[float],
                                      weights: List[float] = AXIS_WEIGHTS,
                                      scales: List[float] = AXIS_SCALES) -> float:
        return np.sqrt(np.sum([w * ((a - b) / s) ** 2
                             for w, a, b, s in zip(weights, v1, v2, scales)]))

    @staticmethod
    def compute_micro_position(x: List[float], stage: int,
                               centroids: Dict[int, List[float]],
                               weights: List[float] = AXIS_WEIGHTS,
                               scales: List[float] = AXIS_SCALES) -> float:
        """
        Geometric projection of NSDT vector onto the line between
        current stage's centroid and the next stage's centroid.
        Returns continuous position within [stage, stage+1] (or wrap 9→0).
        """
        if stage == 9:
            # wrap to Stage 0
            cent_cur = centroids[9]
            cent_next = centroids[0]
            total_dist = SAPGeometry.weighted_normalised_distance(cent_cur, cent_next, weights, scales)
            dist_to_next = SAPGeometry.weighted_normalised_distance(x, cent_next, weights, scales)
            return 9.0 + (1.0 - dist_to_next / total_dist) * 0.99
        cent_cur = centroids[stage]
        cent_next = centroids[stage + 1]
        direction = [cent_next[i] - cent_cur[i] for i in range(5)]
        observed = [x[i] - cent_cur[i] for i in range(5)]
        dot_num = sum(weights[i] * observed[i] * direction[i] / (scales[i]**2) for i in range(5))
        dot_den = sum(weights[i] * direction[i] * direction[i] / (scales[i]**2) for i in range(5))
        if dot_den == 0:
            t = 0.0
        else:
            t = max(0.0, min(1.0, dot_num / dot_den))
        return stage + t

    @staticmethod
    def enforce_geometry(prev_stage: Optional[int], new_stage: int) -> Tuple[int, bool]:
        """
        Hard enforcement of geometric transition law.
        Returns (corrected_stage, was_valid).
        """
        if prev_stage is None:
            return new_stage, True

        delta = new_stage - prev_stage

        # Stage 5 point of no return
        if prev_stage == 5 and new_stage < 5:
            return 5, False

        # No skipping – clamp to nearest valid neighbor
        if delta > 1:
            return prev_stage + 1, False
        if delta < -1:
            return prev_stage - 1, False

        return new_stage, True
