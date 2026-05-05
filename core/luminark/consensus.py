"""
LUMINARK OVERWATCH PRIME — Core Engine v1.0
consensus.py — Multi-evaluator confidence scoring

PROTECTED MODULE.

The Consensus Engine runs three independent evaluator pathways with different
dimension weightings. Disagreement between evaluators reduces confidence and
raises an uncertainty flag — telling operators that the current reading is
ambiguous and may require additional data.

Three evaluator profiles:
  1. Risk-Sensitive:        Weights Tension and Stability more heavily
  2. Stability-Sensitive:   Weights Stability and Coherence more heavily
  3. Adaptability-Sensitive: Weights Adaptability and Complexity more heavily

This is not a voting trick — it models the reality that different operators
and different use cases prioritize different failure signals. When all three
agree, the classification is robust. When they split, the system is near a
stage boundary and deserves heightened scrutiny.
"""
import math
from typing import List, Tuple
from .schemas import NSDTVector, ConsensusResult

# ─────────────────────────────────────────────────────────────────────────────
# Evaluator weight profiles [complexity, stability, tension, adaptability, coherence]
# ─────────────────────────────────────────────────────────────────────────────
EVALUATOR_PROFILES = {
    "risk_sensitive":         [0.15, 0.35, 0.30, 0.10, 0.10],
    "stability_sensitive":    [0.10, 0.40, 0.15, 0.15, 0.20],
    "adaptability_sensitive": [0.20, 0.15, 0.20, 0.35, 0.10],
}

# Stage centroids — same as nsdt.py (duplicated here for evaluator independence)
from .nsdt import STAGE_CENTROIDS


def _weighted_euclidean(vec: List[float], centroid: List[float], weights: List[float]) -> float:
    """Weighted Euclidean distance."""
    return math.sqrt(sum(w * (v - c) ** 2 for w, v, c in zip(weights, vec, centroid)))


def _classify_with_weights(vec: List[float], weights: List[float]) -> int:
    """Classify stage using a weighted distance metric."""
    distances = [
        (stage, _weighted_euclidean(vec, centroid, weights))
        for stage, centroid in STAGE_CENTROIDS.items()
    ]
    best_stage, _ = min(distances, key=lambda x: x[1])
    return best_stage


def consensus_analysis(vec: NSDTVector) -> ConsensusResult:
    """
    Run three independent evaluators and compute agreement.

    Returns ConsensusResult with confidence, label, votes, and uncertainty.
    """
    v = vec.as_list()

    votes: List[int] = []
    for profile_name, weights in EVALUATOR_PROFILES.items():
        stage = _classify_with_weights(v, weights)
        votes.append(stage)

    # Agreement calculation
    unique_votes = set(votes)
    if len(unique_votes) == 1:
        # Perfect consensus
        confidence = 0.95
        label = "HIGH CONSENSUS"
    elif max(votes.count(s) for s in unique_votes) >= 2:
        # Majority agreement (2/3)
        confidence = 0.72
        label = "MODERATE CONSENSUS"
    else:
        # Three-way split
        confidence = 0.45
        label = "SPLIT VERDICT"

    # Proximity bonus: if all votes are within 1 stage of each other
    if max(votes) - min(votes) <= 1 and len(unique_votes) > 1:
        confidence = min(0.95, confidence + 0.10)
        if label == "SPLIT VERDICT":
            label = "MODERATE CONSENSUS"

    return ConsensusResult(
        confidence=round(confidence, 3),
        label=label,
        votes=votes,
        uncertainty=round(1.0 - confidence, 3),
    )
