"""Stage 6 – NEXUS OF HARMONY: Conductor's Paradox and Flow Quality."""

from typing import Dict, Any, Optional, List
from .tumbling_inversion import compute_inversion


def classify_flow_quality(nsdt_vector: List[float], middle_path_accessed: bool = False) -> Dict[str, Any]:
    """
    Determine Sustainable Flow vs Brittle Flow for Stage 6.

    Uses:
    - Middle Path access flag from Stage 5
    - Current inversion state (physical vs consciousness stability)
    - Conductor score: ability to hear approaching dissonance (rate of change of Tension)
    """
    N, S, D, T, C = nsdt_vector

    inv = compute_inversion(nsdt_vector, 6)

    # Conductor score: high Coherence + high Adaptability + moderate Tension
    conductor_score = (C * 0.5) + (D * 0.3) + (100 - abs(T - 50) * 0.2)
    conductor_score = round(conductor_score, 1)

    # Brittle risk: physical stability high but consciousness stability low
    brittle_risk = (inv.physical_stability > 70 and inv.consciousness_stability < 50)

    if middle_path_accessed and conductor_score >= 50 and not brittle_risk:
        flow_type = "sustainable"
        directive = (
            "Sustainable Flow – The Witness Position remains active. "
            "You are in flow AND aware that the flow is temporary. "
            "Harvest the peak, but listen for the dissonance that hasn't arrived yet."
        )
        stage_7_quality = "invitation"
    else:
        flow_type = "brittle"
        directive = (
            "Brittle Flow – The Witness Position was not established at Stage 5. "
            "You HAVE BECOME the flow. Stage 7 will arrive as crisis, not invitation. "
            "Re‑establish meta‑awareness before the peak ends."
        )
        stage_7_quality = "ambush"

    return {
        "flow_type": flow_type,
        "conductor_score": conductor_score,
        "brittle_risk": brittle_risk,
        "middle_path_accessed": middle_path_accessed,
        "stage_7_arrival": stage_7_quality,
        "directive": directive,
        "inversion": inv.__dict__,
    }
