"""Stage 8 – VESSEL OF GROUNDING: Crystallization Paradox and Gratitude Mechanism."""

from typing import Dict, Any, Optional, List
from .tumbling_inversion import compute_inversion, compute_arc_direction, divergence_category


def classify_crystallization(nsdt_vector: List[float], middle_path_accessed: bool = False, nsdt_history: Optional[List[List[float]]] = None) -> Dict[str, Any]:
    """
    Determine whether Stage 8 will lead to dissolution or shattering.

    Uses:
    - Revealed Self (Stability) vs Concealed Self (Tension) divergence
    - Arc direction (ascending/descending)
    - Middle Path flag (influences availability of Gratitude Mechanism)
    """
    N, S, D, T, C = nsdt_vector

    inv = compute_inversion(nsdt_vector, 8)

    revealed_self = S
    concealed_self = T
    divergence = inv.divergence

    arc, confidence = ("indeterminate", 0)
    if nsdt_history and len(nsdt_history) >= 2:
        arc, confidence = compute_arc_direction(nsdt_history)

    # Gratitude Mechanism: structural operation to align Revealed and Concealed
    # If divergence is low, the mechanism is already engaged.
    gratitude_engaged = divergence < 25
    if middle_path_accessed and not gratitude_engaged and arc == "ascending":
        # User can deliberately engage gratitude
        gratitude_engaged = True

    if gratitude_engaged and divergence < 30:
        trajectory = "dissolution"
        directive = (
            "Gratitude Mechanism engaged. The crystal is returning to solution. "
            "Hold the full weight of the cycle – every stage, every cost, every gift – "
            "simultaneously. Do not require any stage to have been different. "
            "This dual acknowledgment dissolves the structure. The wisdom is preserved."
        )
    else:
        trajectory = "shattering"
        directive = (
            "Crystallization Paradox active. The system is maximally dense and maximally brittle. "
            "Divergence between Revealed Self (projected certainty) and Concealed Self (hidden anxiety) "
            "is too high. Engage the Gratitude Mechanism before the crystal shatters."
        )

    return {
        "trajectory": trajectory,
        "revealed_self": round(revealed_self, 1),
        "concealed_self": round(concealed_self, 1),
        "divergence": divergence,
        "divergence_category": divergence_category(divergence),
        "gratitude_engaged": gratitude_engaged,
        "arc_direction": arc,
        "arc_confidence": confidence,
        "directive": directive,
        "inversion": inv.__dict__,
    }


def engage_gratitude_mechanism(nsdt_vector: List[float]) -> List[float]:
    """Apply the Gratitude Mechanism: reduce divergence between S and T."""
    nsdt = list(nsdt_vector)
    # Mutual acknowledgment: average S and T
    new_S = (nsdt[1] + nsdt[3]) / 2
    new_T = new_S   # make them converge
    nsdt[1] = round(new_S, 1)
    nsdt[3] = round(new_T, 1)
    # Also boost Coherence slightly
    nsdt[4] = min(100, nsdt[4] + 5)
    return nsdt
