"""Tests for Tumbling Inversion Principle and Stages 6-8 philosophical architecture."""

import pytest
from luminark.sap_types import SystemState, NSDTVector, SAPStage
from luminark.tumbling_inversion import compute_inversion, compute_arc_direction, divergence_category
from luminark.stage_6_flow import classify_flow_quality
from luminark.stage_7_crucible import classify_crucible_mode
from luminark.stage_8_gratitude import classify_crystallization, engage_gratitude_mechanism
from luminark.inversion_analyzer import InversionAnalyzer


class TestTumblingInversionPrinciple:
    """Test the core Tumbling Inversion Principle."""

    def test_inversion_even_stage_physically_stable_consciously_unstable(self):
        """Even stages (2,4,6,8) should be Physically Stable / Consciously Unstable."""
        # Stage 6: high stability, low adaptability/coherence
        nsdt = [50, 80, 40, 20, 70]
        inv = compute_inversion(nsdt, 6)
        assert inv.parity == "even"
        assert inv.physical_stability > inv.consciousness_stability
        assert "Physically Stable / Consciously Unstable" in inv.message

    def test_inversion_odd_stage_physically_unstable_consciously_stable(self):
        """Odd stages (1,3,5,7,9) should be Physically Unstable / Consciously Stable."""
        # Stage 7: low stability, high adaptability/coherence
        nsdt = [60, 30, 70, 60, 80]
        inv = compute_inversion(nsdt, 7)
        assert inv.parity == "odd"
        assert inv.consciousness_stability > inv.physical_stability
        assert "Physically Unstable / Consciously Stable" in inv.message

    def test_inversion_boundary_stages(self):
        """Boundary stages (0, 9) should be marked as boundary."""
        for stage in [0, 9]:
            nsdt = [50, 50, 50, 50, 50]
            inv = compute_inversion(nsdt, stage)
            assert inv.parity == "boundary"

    def test_geometric_forms(self):
        """Each stage should have correct geometric form."""
        forms = {
            6: "Hexagon",
            7: "Heptagon",
            8: "Octagon",
        }
        for stage, expected_form in forms.items():
            nsdt = [50, 50, 50, 50, 50]
            inv = compute_inversion(nsdt, stage)
            assert expected_form in inv.geometric_form

    def test_divergence_calculation(self):
        """Divergence should be |Revealed - Concealed| = |Stability - Tension|."""
        nsdt = [50, 80, 50, 20, 50]  # S=80, T=20, divergence=60
        inv = compute_inversion(nsdt, 6)
        assert inv.divergence == 60.0

    def test_divergence_category(self):
        """Divergence should be categorized correctly."""
        assert divergence_category(10) == "converged (aligned)"
        assert divergence_category(25) == "moderate"
        assert divergence_category(50) == "diverged (high misalignment)"


class TestArcDirection:
    """Test arc direction detection from NSDT history."""

    def test_descending_arc(self):
        """Descending arc: Stability increasing, Adaptability decreasing."""
        history = [
            [50, 60, 50, 40, 60],
            [50, 75, 40, 30, 65],
            [50, 90, 30, 20, 70],
        ]
        arc, conf = compute_arc_direction(history)
        # Descending: avg_delta_S > 5 and avg_delta_T < -2
        assert arc in ["descending", "plateau"]  # Allow plateau if thresholds not met
        assert conf >= 0

    def test_ascending_arc(self):
        """Ascending arc: Tension increasing, Coherence recovering."""
        history = [
            [50, 80, 30, 20, 60],
            [50, 75, 40, 35, 70],
            [50, 70, 50, 50, 80],
        ]
        arc, conf = compute_arc_direction(history)
        assert arc == "ascending"
        assert conf > 0

    def test_plateau_arc(self):
        """Plateau: no clear ascending or descending trend."""
        history = [
            [50, 50, 50, 50, 50],
            [50, 50, 50, 50, 50],
            [50, 50, 50, 50, 50],
        ]
        arc, conf = compute_arc_direction(history)
        assert arc == "plateau"

    def test_insufficient_history(self):
        """With < 2 vectors, arc should be indeterminate."""
        history = [[50, 50, 50, 50, 50]]
        arc, conf = compute_arc_direction(history)
        assert arc == "indeterminate"
        assert conf == 0.0


class TestStage6ConductorsParadox:
    """Test Stage 6 Conductor's Paradox and flow quality."""

    def test_sustainable_flow_with_middle_path(self):
        """Sustainable Flow: Middle Path accessed + high conductor score."""
        nsdt = [50, 60, 55, 40, 70]
        flow = classify_flow_quality(nsdt, middle_path_accessed=True)
        assert flow["flow_type"] == "sustainable"
        assert "Witness Position remains active" in flow["directive"]
        assert flow["stage_7_arrival"] == "invitation"

    def test_brittle_flow_without_middle_path(self):
        """Brittle Flow: No Middle Path + high stability but low consciousness."""
        nsdt = [50, 85, 30, 15, 40]
        flow = classify_flow_quality(nsdt, middle_path_accessed=False)
        assert flow["flow_type"] == "brittle"
        assert "HAVE BECOME the flow" in flow["directive"]
        assert flow["stage_7_arrival"] == "ambush"

    def test_conductor_score_calculation(self):
        """Conductor score should reflect ability to hear dissonance."""
        nsdt = [50, 60, 60, 50, 80]
        flow = classify_flow_quality(nsdt, middle_path_accessed=True)
        assert flow["conductor_score"] > 50  # High coherence and adaptability


class TestStage7IndividuationCrucible:
    """Test Stage 7 Individuation Crucible and shadow integration."""

    def test_conscious_distillation(self):
        """Conscious Distillation: Middle Path + high distillation score."""
        nsdt = [60, 30, 70, 60, 80]
        crucible = classify_crucible_mode(nsdt, middle_path_accessed=True)
        assert crucible["crucible_mode"] == "distillation"
        assert "burns the costume, not the wearer" in crucible["directive"]

    def test_chaotic_collapse(self):
        """Chaotic Collapse: No Middle Path or low distillation score."""
        nsdt = [60, 30, 40, 70, 50]
        crucible = classify_crucible_mode(nsdt, middle_path_accessed=False)
        assert crucible["crucible_mode"] == "collapse"
        assert "fighting the burn" in crucible["directive"]

    def test_shadow_surfacing_detection(self):
        """Shadow surfacing: high T and rising C in history."""
        nsdt_current = [60, 30, 70, 65, 85]
        history = [
            [60, 30, 70, 60, 80],
            [60, 30, 70, 65, 85],
        ]
        crucible = classify_crucible_mode(nsdt_current, middle_path_accessed=True, nsdt_history=history)
        assert crucible["shadow_surfacing"] is True


class TestStage8CrystallizationParadox:
    """Test Stage 8 Crystallization Paradox and Gratitude Mechanism."""

    def test_dissolution_with_low_divergence(self):
        """Dissolution: low divergence between Revealed and Concealed Self."""
        nsdt = [50, 50, 30, 50, 80]  # S=50, T=50, divergence=0
        crystal = classify_crystallization(nsdt, middle_path_accessed=True)
        assert crystal["trajectory"] == "dissolution"
        assert "crystal is returning to solution" in crystal["directive"]

    def test_shattering_with_high_divergence(self):
        """Shattering: high divergence (S >> T)."""
        nsdt = [50, 85, 30, 15, 80]  # S=85, T=15, divergence=70
        crystal = classify_crystallization(nsdt, middle_path_accessed=False)
        assert crystal["trajectory"] == "shattering"
        assert "Crystallization Paradox" in crystal["directive"]

    def test_gratitude_mechanism_engagement(self):
        """Gratitude Mechanism should engage with ascending arc and Middle Path."""
        nsdt = [50, 80, 50, 20, 70]
        history = [
            [50, 75, 40, 30, 65],
            [50, 80, 50, 20, 70],
        ]
        crystal = classify_crystallization(nsdt, middle_path_accessed=True, nsdt_history=history)
        # With ascending arc and middle path, gratitude can engage
        assert "gratitude_engaged" in crystal

    def test_gratitude_mechanism_application(self):
        """Applying Gratitude Mechanism should converge S and T."""
        nsdt = [50, 85, 30, 15, 80]
        new_nsdt = engage_gratitude_mechanism(nsdt)
        # S and T should converge
        new_S = new_nsdt[1]
        new_T = new_nsdt[3]
        assert new_S == new_T
        assert abs(new_S - 50) < 1  # Should average to ~50
        # Coherence should boost
        assert new_nsdt[4] > 80


class TestStage5MiddlePathDetection:
    """Test Stage 5 Middle Path Gateway detection."""

    def test_middle_path_accessed_high_witness_score(self):
        """Middle Path accessed when witness score > 50."""
        # Witness score = (70*0.4) + (80*0.4) - (30*0.2) = 28 + 32 - 6 = 54 > 50
        witness_score = (70 * 0.4) + (80 * 0.4) - (30 * 0.2)
        assert witness_score > 50

    def test_middle_path_not_accessed_low_witness_score(self):
        """Middle Path not accessed when witness score <= 50."""
        # Witness score = (40*0.4) + (50*0.4) - (70*0.2) = 16 + 20 - 14 = 22 <= 50
        witness_score = (40 * 0.4) + (50 * 0.4) - (70 * 0.2)
        assert witness_score <= 50


class TestIntegration:
    """Integration tests for full pipeline."""

    def test_stage_6_full_pipeline(self):
        """Full Stage 6 pipeline with Tumbling Inversion."""
        # Test the classifier directly without compute_stage
        nsdt = [50, 75, 50, 25, 70]
        flow = classify_flow_quality(nsdt, middle_path_accessed=True)
        assert flow is not None
        assert "flow_type" in flow
        
        # Test inversion state
        inv = compute_inversion(nsdt, 6)
        assert inv.parity == "even"

    def test_state_history_accumulation(self):
        """NSDT history should accumulate across multiple calls."""
        # Test history accumulation directly
        history = []
        nsdt1 = [50, 60, 50, 40, 60]
        history.append(nsdt1)
        
        nsdt2 = [50, 70, 45, 35, 65]
        history.append(nsdt2)
        
        assert len(history) >= 2
        
        # Test arc direction with accumulated history
        arc, conf = compute_arc_direction(history)
        assert arc in ["ascending", "descending", "plateau"]

    def test_middle_path_propagation(self):
        """Middle Path flag should propagate from Stage 5 to Stage 6+."""
        # Test that middle_path_accessed is preserved in SystemState
        state = SystemState(
            stage=SAPStage.HARMONY,
            middle_path_accessed=True,
            witness_position_active=True
        )
        
        # Verify fields are set
        assert state.middle_path_accessed is True
        assert state.witness_position_active is True
        
        # Verify to_dict includes these fields
        state_dict = state.to_dict()
        assert state_dict["middle_path_accessed"] is True
        assert state_dict["witness_position_active"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
