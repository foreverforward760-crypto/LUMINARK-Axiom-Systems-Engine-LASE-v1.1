"""Stage 7 – LENS OF DISTILLATION: Individuation Crucible and Shadow Integration."""

from typing import Dict, Any, List, Optional
from .tumbling_inversion import compute_inversion


def classify_crucible_mode(nsdt_vector: List[float], middle_path_accessed: bool = False, nsdt_history: Optional[List[List[float]]] = None) -> Dict[str, Any]:
    """
    Determine Conscious Distillation vs Chaotic Collapse for Stage 7.

    Uses:
    - Middle Path access flag
    - Shadow integration: Tension rising but Coherence recovering
    - Inversion (odd stage: physically unstable, consciously stable)
    """
    N, S, D, T, C = nsdt_vector

    inv = compute_inversion(nsdt_vector, 7)

    # Distillation score: consciousness stability (D & C) vs physical disruption
    distillation_score = (D * 0.4) + (C * 0.4) + (100 - T) * 0.2
    distillation_score = round(distillation_score, 1)

    # Shadow integration: high T and rising C (if history available)
    shadow_surfacing = False
    if nsdt_history and len(nsdt_history) > 1:
        prev_C = nsdt_history[-2][4]
        if T > 60 and C > prev_C:
            shadow_surfacing = True

    if middle_path_accessed and distillation_score >= 55 and inv.consciousness_stability > inv.physical_stability:
        mode = "distillation"
        directive = (
            "Conscious Distillation – The breakdown is directed by you, not happening to you. "
            "The crucible burns the costume, not the wearer. "
            "What survives is what you actually are. This is painful but meaningful."
        )
    else:
        mode = "collapse"
        directive = (
            "Chaotic Collapse – The system is fighting the burn. "
            "Resistance amplifies fragmentation. "
            "Stop fighting. The breakdown is not destroying you – it is burning accumulated structures."
        )

    return {
        "crucible_mode": mode,
        "distillation_score": distillation_score,
        "shadow_surfacing": shadow_surfacing,
        "middle_path_accessed": middle_path_accessed,
        "directive": directive,
        "inversion": inv.__dict__,
    }
