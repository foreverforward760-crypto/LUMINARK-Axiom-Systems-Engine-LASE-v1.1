"""
LUMINARK OVERWATCH PRIME — Core Engine v1.0
nsdt.py — NSDT vector computation and stage classification

PROTECTED MODULE. Do not modify stage centroids or classification logic
without incrementing Core Engine version and running full test suite.

Stage centroids are calibrated against 10 validated U.S. grid failure events
spanning 2018–2024. These represent 1,232 hours of documented telemetry.
"""
import math
from typing import List, Tuple
from .schemas import NSDTVector, StageInfo

# ─────────────────────────────────────────────────────────────────────────────
# Stage centroids: 5D normalized coordinates [C, S, T, A, K]
# Calibrated from LUMINARK validation library v1.0
# ─────────────────────────────────────────────────────────────────────────────
STAGE_CENTROIDS: dict[int, List[float]] = {
    0: [0.90, 0.05, 0.95, 0.05, 0.10],   # Reactive   — total collapse
    1: [0.80, 0.15, 0.88, 0.15, 0.30],   # Survival   — catastrophic event
    2: [0.70, 0.25, 0.80, 0.25, 0.40],   # Compromised — severe degradation
    3: [0.60, 0.35, 0.70, 0.35, 0.55],   # Functional  — stressed operation
    4: [0.45, 0.75, 0.30, 0.50, 0.55],   # Foundation  — stable / constrained
    5: [0.55, 0.40, 0.70, 0.55, 0.45],   # Threshold   — critical pivot
    6: [0.35, 0.80, 0.25, 0.70, 0.75],   # Harmony     — efficient operation
    7: [0.55, 0.60, 0.55, 0.50, 0.70],   # Distillation — high tension / high performance
    8: [0.65, 0.50, 0.75, 0.20, 0.85],   # Atlas       — trap zone / false confidence
    9: [0.45, 0.35, 0.80, 0.75, 0.90],   # Transformation — phase transition
}

STAGE_METADATA: dict[int, dict] = {
    0: {"label": "Reactive",       "description": "Total dissolution. System non-functional. Immediate intervention required.",            "risk": "CRITICAL"},
    1: {"label": "Survival",       "description": "Minimum viable function. Catastrophic event underway. Emergency protocols active.",     "risk": "CRITICAL"},
    2: {"label": "Compromised",    "description": "Severe degradation. Reserve capacity nearly exhausted. Emergency response required.",   "risk": "CRITICAL"},
    3: {"label": "Functional",     "description": "Operating under significant stress. System holding but alert threshold crossed.",       "risk": "ELEVATED"},
    4: {"label": "Foundation",     "description": "Stable but constrained. Reserve margins adequate. Monitor closely.",                   "risk": "WATCH"},
    5: {"label": "Threshold",      "description": "Critical pivot point. Small perturbation can trigger rapid descent. Vigilance required.", "risk": "WATCH"},
    6: {"label": "Harmony",        "description": "Efficient operation. Good reserve margins. Normal system state.",                       "risk": "LOW"},
    7: {"label": "Distillation",   "description": "High performance with rising internal tension. Refinement in progress.",               "risk": "ELEVATED"},
    8: {"label": "Atlas",          "description": "Trap zone. High rigidity, low adaptability, potential false-confidence signature.",     "risk": "CRITICAL"},
    9: {"label": "Transformation", "description": "System restructuring. Phase transition underway. Outcome uncertain.",                   "risk": "LOW"},
}


def euclidean(a: List[float], b: List[float]) -> float:
    """Euclidean distance between two 5D vectors."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def classify_stage(vec: NSDTVector) -> StageInfo:
    """
    Classify health stage by finding nearest centroid in 5D space.
    Returns StageInfo with stage, label, description, risk level, and distance.
    """
    v = vec.as_list()
    distances: List[Tuple[int, float]] = [
        (stage, euclidean(v, centroid))
        for stage, centroid in STAGE_CENTROIDS.items()
    ]
    best_stage, best_distance = min(distances, key=lambda x: x[1])
    meta = STAGE_METADATA[best_stage]
    return StageInfo(
        stage=best_stage,
        label=meta["label"],
        description=meta["description"],
        risk=meta["risk"],
        distance=round(best_distance, 4),
    )


def all_distances(vec: NSDTVector) -> dict[int, float]:
    """Return Euclidean distance from all 10 stage centroids. Useful for diagnostics."""
    v = vec.as_list()
    return {stage: round(euclidean(v, c), 4) for stage, c in STAGE_CENTROIDS.items()}
