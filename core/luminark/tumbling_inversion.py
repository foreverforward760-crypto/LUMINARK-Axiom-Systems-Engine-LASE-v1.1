"""Tumbling Inversion Principle – core phenomenological engine for SAP stages 6‑8.

This module implements the fundamental insight:
- Even stages (2,4,6,8): Physically Stable / Consciously Unstable
- Odd stages (1,3,5,7,9): Physically Unstable / Consciously Stable

It also provides divergence (Revealed vs. Concealed Self) and arc direction.
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple
import math


@dataclass
class InversionState:
    """State of the tumbling inversion for a given NSDT vector."""
    stage: int
    parity: str          # 'even', 'odd', 'boundary'
    physical_stability: float   # 0-100, high = stable
    consciousness_stability: float  # 0-100, high = stable
    divergence: float    # 0-100, difference between Revealed and Concealed Self
    geometric_form: str
    message: str


def compute_inversion(nsdt_vector: List[float], stage: int) -> InversionState:
    """
    Compute the inversion state from an NSDT vector and its SAP stage.

    NSDT indices: [Complexity, Stability, Adaptability, Tension, Coherence]
    """
    N, S, D, T, C = nsdt_vector

    # Physical stability: high S and low T -> stable
    physical = (S * 0.7) + (100 - T) * 0.3
    # Consciousness stability: high D and high C -> stable (aware, adaptable)
    conscious = (D * 0.5) + (C * 0.5)

    # Divergence: Revealed = projected stability (S), Concealed = internal tension (T)
    revealed = S
    concealed = T
    divergence = abs(revealed - concealed)

    # Parity and geometric form based on stage
    if stage == 0 or stage == 9:
        parity = "boundary"
        geometric = "Circle" if stage == 0 else "Nonagon → Circle"
    elif stage % 2 == 0:
        parity = "even"
        geometric = {2: "Line/Spindle", 4: "Square/Foundation", 6: "Hexagon", 8: "Octagon"}.get(stage, "Polygon")
    else:
        parity = "odd"
        geometric = {1: "Point/Spark", 3: "Triangle", 5: "Perpendicular Axis", 7: "Heptagon", 9: "Nonagon"}.get(stage, "Polygon")

    # Message summarizing the inversion principle for this stage
    if parity == "even":
        msg = f"Even stage {stage} – Physically Stable / Consciously Unstable. Physical stability = {physical:.1f}, consciousness stability = {conscious:.1f}."
    elif parity == "odd":
        msg = f"Odd stage {stage} – Physically Unstable / Consciously Stable. Physical stability = {physical:.1f}, consciousness stability = {conscious:.1f}."
    else:
        msg = f"Boundary stage {stage} – dissolution or primordial potential."

    return InversionState(
        stage=stage,
        parity=parity,
        physical_stability=round(physical, 1),
        consciousness_stability=round(conscious, 1),
        divergence=round(divergence, 1),
        geometric_form=geometric,
        message=msg
    )


def compute_arc_direction(history: List[List[float]]) -> Tuple[str, float]:
    """
    Determine ascending vs descending arc from NSDT history (last 3-5 vectors).

    Returns (arc, confidence) where arc is 'ascending', 'descending', or 'plateau'.
    Descending: Stability increasing, Adaptability decreasing.
    Ascending: Tension increasing, Coherence recovering.
    """
    if len(history) < 2:
        return ("indeterminate", 0.0)

    # Take differences between consecutive vectors
    deltas = []
    for i in range(1, len(history)):
        prev = history[i-1]
        curr = history[i]
        deltas.append([curr[j] - prev[j] for j in range(5)])

    # Average delta for key axes
    avg_delta_S = sum(d[1] for d in deltas) / len(deltas)   # Stability
    avg_delta_D = sum(d[2] for d in deltas) / len(deltas)   # Adaptability
    avg_delta_T = sum(d[3] for d in deltas) / len(deltas)   # Tension
    avg_delta_C = sum(d[4] for d in deltas) / len(deltas)   # Coherence

    descending_score = avg_delta_S - avg_delta_D
    ascending_score = avg_delta_T + avg_delta_C

    if descending_score > 5 and ascending_score < -2:
        arc = "descending"
        confidence = min(100, descending_score * 5)
    elif ascending_score > 5 and descending_score < -2:
        arc = "ascending"
        confidence = min(100, ascending_score * 5)
    else:
        arc = "plateau"
        confidence = 50.0

    return (arc, round(confidence, 1))


def divergence_category(divergence: float) -> str:
    """Categorize divergence between Revealed and Concealed Self."""
    if divergence < 15:
        return "converged (aligned)"
    elif divergence < 35:
        return "moderate"
    else:
        return "diverged (high misalignment)"
