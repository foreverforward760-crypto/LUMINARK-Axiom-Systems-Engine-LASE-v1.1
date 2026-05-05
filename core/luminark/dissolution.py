"""
Dissolution Engine - Handles 0-9-0 cycle completion.
Governs the final release from Stage 9 (Completion) back into Stage 0 (Plenara).
"""

from .sap_types import NSDTVector, SAPStage, SystemState

class DissolutionEngine:
    """Handles the final 0-9-0 cycle closure from Stage 9 back to Void."""

    @staticmethod
    def should_dissolve(state: SystemState) -> tuple[bool, str]:
        """
        Determine if a Stage 9 system is ready to return to Plenara (Stage 0).
        Conditions:
        - Coherence >= 95% (full pattern recognition)
        - Adaptability >= 80% (acceptance of impermanence)
        - Tension <= 20% (no remaining seeking)
        """
        if state.stage != SAPStage.RELEASE:
            return False, ""

        nsdt = state.nsdt
        if nsdt.coherence >= 95 and nsdt.adaptability >= 80 and nsdt.tension <= 20:
            return True, "Stage 9 completion: Ready for dissolution into the Void."
        return False, ""

    @staticmethod
    def dissolve(state: SystemState) -> SystemState:
        """
        Return the system to Stage 0 (Plenara).
        NSDT vector is reset to neutral primordial potential.
        """
        void_nsdt = NSDTVector(
            complexity=0.0,
            stability=50.0,      # Neutral equilibrium
            tension=0.0,
            adaptability=100.0,   # Pure potential
            coherence=100.0       # Undifferentiated wholeness
        )
        return SystemState(
            stage=SAPStage.VOID,
            nsdt=void_nsdt,
            is_trap=False,
            recommended_action="DISSOLVED: Cycle complete. Returned to Plenara.",
            unified_field_value=1.0,  # Perfect unity in void
            recalibration_recommended=False
        )
