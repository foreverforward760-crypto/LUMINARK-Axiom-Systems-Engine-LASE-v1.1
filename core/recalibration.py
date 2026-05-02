"""
luminark/recalibration.py – RecalibrationEngine

Applies corrective stage adjustment when inversion analyzer detects
a system drifting into an unsustainable or contradictory state.

Recalibration is a soft intervention — it does not force a stage jump
but nudges the recommended action and flags the state for upstream review.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .sap_types import SystemState


class RecalibrationEngine:
    """
    Evaluates whether a SystemState warrants recalibration and applies
    the corrective recommended action if so.
    """

    @staticmethod
    def should_recalibrate(state: "SystemState") -> tuple[bool, str]:
        """
        Returns (should_recalibrate: bool, reason: str).

        Recalibration is triggered when:
        - System is flagged as a trap (is_trap=True)
        - NSDT coherence and adaptability are both very low (< 20)
          indicating a system stuck in incoherence
        """
        if state.is_trap:
            return True, "Trap detected: recalibration recommended"
        if state.nsdt is not None:
            # Low coherence AND low adaptability = stuck state
            if state.nsdt.coherence < 20 and state.nsdt.adaptability < 20:
                return True, "Low coherence + low adaptability: system may be stuck"
        return False, ""

    @staticmethod
    def apply_recalibration(state: "SystemState") -> "SystemState":
        """
        Apply a recalibration nudge to a state.
        Returns a modified copy of the state with updated recommended_action
        and recalibration_recommended flag set.
        """
        from .sap_types import SystemState
        return SystemState(
            stage=state.stage,
            nsdt=state.nsdt,
            is_trap=state.is_trap,
            trap_reason=state.trap_reason,
            recommended_action=f"RECALIBRATE: {state.recommended_action}",
            unified_field_value=state.unified_field_value,
            recalibration_recommended=True,
        )
