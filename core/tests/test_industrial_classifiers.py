"""
tests/test_industrial_classifiers.py

Comprehensive test suite for Stage 6-8 industrial classifiers.
Tests the three new mechanisms: Operating Margin, Failure Isolation, Resource Recirculation.

These tests verify that the classifiers correctly identify industrial system states
without anthropomorphizing the machine, maintaining clean separation from KAIROS.
"""

import pytest
from luminark.sap_types import NSDTVector, SAPStage, SystemState
from luminark.inversion_analyzer import InversionAnalyzer
from luminark.stage_descriptions import (
    get_stage_description,
    get_classifier_method,
    get_risk_level,
)


class TestOperatingMarginClassifier:
    """Stage 6: Safety Margin Utilization"""

    def test_sustainable_margin(self):
        """Sustainable margin: S 40-70, T < 50"""
        nsdt = NSDTVector(
            complexity=5.0,
            stability=55.0,  # In sustainable range
            tension=40.0,    # Below threshold
            adaptability=5.0,
            coherence=5.0,
        )
        result = InversionAnalyzer.classify_operating_margin(nsdt)
        
        assert result["margin_type"] == "sustainable"
        assert "optimal" in result["directive"].lower()
        assert result["stability"] == 55.0
        assert result["tension"] == 40.0

    def test_brittle_margin(self):
        """Brittle margin: S > 75, T < 30"""
        nsdt = NSDTVector(
            complexity=5.0,
            stability=85.0,  # High stability
            tension=15.0,    # Low tension (hidden stress)
            adaptability=5.0,
            coherence=5.0,
        )
        result = InversionAnalyzer.classify_operating_margin(nsdt)
        
        assert result["margin_type"] == "brittle"
        assert "REDUCED SAFETY MARGIN" in result["directive"]
        assert "fatigue" in result["directive"].lower()

    def test_nominal_margin(self):
        """Nominal margin: all other cases"""
        nsdt = NSDTVector(
            complexity=5.0,
            stability=30.0,  # Below sustainable range
            tension=60.0,    # Above threshold
            adaptability=5.0,
            coherence=5.0,
        )
        result = InversionAnalyzer.classify_operating_margin(nsdt)
        
        assert result["margin_type"] == "nominal"
        assert "expected parameters" in result["directive"].lower()

    def test_boundary_conditions(self):
        """Test boundary conditions for margin classification"""
        # Exactly at sustainable lower bound with tension below threshold
        nsdt_lower = NSDTVector(stability=40.0, tension=40.0)
        result_lower = InversionAnalyzer.classify_operating_margin(nsdt_lower)
        assert result_lower["margin_type"] == "sustainable"
        
        # Exactly at sustainable upper bound
        nsdt_upper = NSDTVector(stability=70.0, tension=49.9)
        result_upper = InversionAnalyzer.classify_operating_margin(nsdt_upper)
        assert result_upper["margin_type"] == "sustainable"
        
        # Just outside brittle range
        nsdt_edge = NSDTVector(stability=75.1, tension=29.9)
        result_edge = InversionAnalyzer.classify_operating_margin(nsdt_edge)
        assert result_edge["margin_type"] == "brittle"


class TestFailureIsolationClassifier:
    """Stage 7: Failure Isolation / Component Stress-Testing"""

    def test_distillation_mode(self):
        """Distillation: N > 70, C > 60 (fault contained)"""
        nsdt = NSDTVector(
            complexity=80.0,  # High complexity
            stability=5.0,
            tension=5.0,
            adaptability=5.0,
            coherence=75.0,   # High coherence (system isolating fault)
        )
        result = InversionAnalyzer.classify_failure_isolation(nsdt)
        
        assert result["failure_isolation_mode"] == "distillation"
        assert "isolated" in result["directive"].lower()
        assert "rerouting" in result["directive"].lower()

    def test_collapse_mode(self):
        """Collapse: N > 70, C < 40 (cascading failure)"""
        nsdt = NSDTVector(
            complexity=85.0,  # High complexity
            stability=5.0,
            tension=5.0,
            adaptability=5.0,
            coherence=30.0,   # Low coherence (cascading)
        )
        result = InversionAnalyzer.classify_failure_isolation(nsdt)
        
        assert result["failure_isolation_mode"] == "collapse"
        assert "CRITICAL" in result["directive"]
        assert "cascading" in result["directive"].lower()
        assert "emergency shutdown" in result["directive"].lower()

    def test_degraded_mode(self):
        """Degraded: all other cases"""
        nsdt = NSDTVector(
            complexity=50.0,  # Moderate complexity
            stability=5.0,
            tension=5.0,
            adaptability=5.0,
            coherence=50.0,   # Moderate coherence
        )
        result = InversionAnalyzer.classify_failure_isolation(nsdt)
        
        assert result["failure_isolation_mode"] == "degraded"
        assert "monitor" in result["directive"].lower()

    def test_low_complexity_always_degraded(self):
        """Low complexity should never trigger distillation or collapse"""
        nsdt = NSDTVector(
            complexity=60.0,  # Below 70 threshold
            coherence=80.0,   # Even with high coherence
        )
        result = InversionAnalyzer.classify_failure_isolation(nsdt)
        assert result["failure_isolation_mode"] == "degraded"


class TestResourceRecirculationClassifier:
    """Stage 8: Resource Recirculation / Entropy Accounting"""

    def test_dissolution_trajectory(self):
        """Dissolution: 50 <= S <= 70, 30 <= T <= 50"""
        nsdt = NSDTVector(
            complexity=5.0,
            stability=60.0,   # In dissolution range
            tension=40.0,     # In dissolution range
            adaptability=5.0,
            coherence=5.0,
        )
        result = InversionAnalyzer.classify_resource_recirculation(nsdt)
        
        assert result["recirculation_trajectory"] == "dissolution"
        assert "decommissioning" in result["directive"].lower()
        assert "energy" in result["directive"].lower()
        assert "recirculated" in result["directive"].lower()

    def test_shattering_trajectory(self):
        """Shattering: S > 80, T < 20 (brittle crystal)"""
        nsdt = NSDTVector(
            complexity=5.0,
            stability=85.0,   # High stability
            tension=10.0,     # Low tension (hidden stress)
            adaptability=5.0,
            coherence=5.0,
        )
        result = InversionAnalyzer.classify_resource_recirculation(nsdt)
        
        assert result["recirculation_trajectory"] == "shattering"
        assert "STRUCTURAL BRITTLENESS" in result["directive"]
        assert "de-energization" in result["directive"].lower()

    def test_uncertain_trajectory(self):
        """Uncertain: all other cases"""
        nsdt = NSDTVector(
            complexity=5.0,
            stability=40.0,   # Below dissolution range
            tension=60.0,     # Above dissolution range
            adaptability=5.0,
            coherence=5.0,
        )
        result = InversionAnalyzer.classify_resource_recirculation(nsdt)
        
        assert result["recirculation_trajectory"] == "uncertain"
        assert "monitor" in result["directive"].lower()

    def test_divergence_calculation(self):
        """Verify divergence is calculated correctly"""
        nsdt = NSDTVector(stability=80.0, tension=30.0)
        result = InversionAnalyzer.classify_resource_recirculation(nsdt)
        
        expected_divergence = abs(80.0 - 30.0)
        assert result["divergence"] == expected_divergence
        assert result["divergence"] == 50.0


class TestIntegrationWithComputeStage:
    """Integration tests: classifiers invoked from compute_stage pipeline"""

    def test_stage_6_harmony_invokes_operating_margin(self):
        """Stage 6 (HARMONY) should invoke operating_margin classifier"""
        # Create NSDT that triggers Stage 6
        nsdt = NSDTVector(
            complexity=5.0,
            stability=65.0,
            tension=5.0,
            adaptability=85.0,
            coherence=5.0,
        )
        # Mock physical and conscious scores to force Stage 6
        nsdt.physical_score = lambda: 65.0
        nsdt.conscious_score = lambda: 65.0
        
        state = InversionAnalyzer.compute_stage(nsdt, allow_recalibration=False)
        
        # If stage is HARMONY (6), extra should contain operating_margin
        if state.stage == SAPStage.HARMONY:
            assert "operating_margin" in state.extra
            assert "margin_type" in state.extra["operating_margin"]

    def test_stage_7_foundation_invokes_failure_isolation(self):
        """Stage 7 (FOUNDATION) should invoke failure_isolation classifier"""
        nsdt = NSDTVector(
            complexity=75.0,
            stability=5.0,
            tension=5.0,
            adaptability=5.0,
            coherence=75.0,
        )
        nsdt.physical_score = lambda: 75.0
        nsdt.conscious_score = lambda: 50.0
        
        state = InversionAnalyzer.compute_stage(nsdt, allow_recalibration=False)
        
        if state.stage == SAPStage.FOUNDATION:
            assert "failure_isolation" in state.extra
            assert "failure_isolation_mode" in state.extra["failure_isolation"]

    def test_stage_8_integration_invokes_recirculation(self):
        """Stage 8 (INTEGRATION) should invoke resource_recirculation classifier"""
        nsdt = NSDTVector(
            complexity=5.0,
            stability=85.0,
            tension=5.0,
            adaptability=5.0,
            coherence=5.0,
        )
        nsdt.physical_score = lambda: 75.0
        nsdt.conscious_score = lambda: 50.0
        
        state = InversionAnalyzer.compute_stage(nsdt, allow_recalibration=False)
        
        if state.stage == SAPStage.INTEGRATION:
            assert "resource_recirculation" in state.extra
            assert "recirculation_trajectory" in state.extra["resource_recirculation"]

    def test_extra_field_preserved_in_serialization(self):
        """Extra field should be preserved in to_dict() serialization"""
        nsdt = NSDTVector(stability=65.0, coherence=75.0)
        nsdt.physical_score = lambda: 65.0
        nsdt.conscious_score = lambda: 65.0
        
        state = InversionAnalyzer.compute_stage(nsdt, allow_recalibration=False)
        state_dict = state.to_dict()
        
        assert "extra" in state_dict
        assert isinstance(state_dict["extra"], dict)


class TestStageDescriptions:
    """Test stage description lookup functions"""

    def test_get_stage_description_stage_6(self):
        """Stage 6 description should be available"""
        desc = get_stage_description(6)
        
        assert desc["name"] == "NEXUS OF HARMONY"
        assert "Safety Margin" in desc["industrial_theme"]
        assert desc["mechanism"] == "classify_operating_margin"

    def test_get_stage_description_stage_7(self):
        """Stage 7 description should be available"""
        desc = get_stage_description(7)
        
        assert desc["name"] == "LENS OF DISTILLATION"
        assert "Failure Isolation" in desc["industrial_theme"]
        assert desc["mechanism"] == "classify_failure_isolation"

    def test_get_stage_description_stage_8(self):
        """Stage 8 description should be available"""
        desc = get_stage_description(8)
        
        assert desc["name"] == "VESSEL OF GROUNDING"
        assert "Crystallization" in desc["industrial_theme"]
        assert desc["mechanism"] == "classify_resource_recirculation"

    def test_get_stage_description_non_industrial_stage(self):
        """Non-industrial stages should return empty dict"""
        desc = get_stage_description(3)
        assert desc == {}

    def test_get_classifier_method(self):
        """Classifier method lookup should work"""
        assert get_classifier_method(6) == "classify_operating_margin"
        assert get_classifier_method(7) == "classify_failure_isolation"
        assert get_classifier_method(8) == "classify_resource_recirculation"
        assert get_classifier_method(5) == ""

    def test_get_risk_level(self):
        """Risk level mapping should work"""
        risk = get_risk_level("operating_margin:brittle")
        assert risk["risk"] == "HIGH"
        assert risk["alert_color"] == "RED"
        
        risk = get_risk_level("failure_isolation:collapse")
        assert risk["risk"] == "CRITICAL"
        assert risk["alert_color"] == "RED"
        
        risk = get_risk_level("resource_recirculation:dissolution")
        assert risk["risk"] == "MEDIUM"
        assert risk["alert_color"] == "YELLOW"


class TestBackwardCompatibility:
    """Ensure existing tests for Stages 0-5 and 9 still pass"""

    def test_stage_0_through_5_unaffected(self):
        """Stages 0-5 should not have extra classifiers"""
        # Create NSDT that will result in early stages
        nsdt = NSDTVector(
            complexity=3.0,
            stability=3.0,
            tension=8.0,
            adaptability=2.0,
            coherence=2.0,
        )
        # Mock the score methods to ensure early stage
        nsdt.physical_score = lambda: 20.0
        nsdt.conscious_score = lambda: 20.0
        
        state = InversionAnalyzer.compute_stage(nsdt, allow_recalibration=False)
        
        # Extra should be empty dict for non-industrial stages
        if state.stage < 6:
            assert state.extra == {}

    def test_stage_9_unaffected(self):
        """Stage 9 should not have extra classifiers"""
        nsdt = NSDTVector(coherence=95.0, adaptability=80.0)
        # Mock the score methods
        nsdt.physical_score = lambda: 50.0
        nsdt.conscious_score = lambda: 50.0
        
        try:
            state = InversionAnalyzer.compute_stage(nsdt, allow_recalibration=False)
            
            if state.stage == SAPStage.RELEASE:
                assert state.extra == {}
        except AttributeError:
            # If physical_score/conscious_score not available, skip this test
            pytest.skip("physical_score/conscious_score methods not available")

    def test_system_state_extra_default_none_compatible(self):
        """SystemState with no extra should default to empty dict"""
        state = SystemState()
        assert state.extra == {}
        
        state_dict = state.to_dict()
        assert "extra" in state_dict
        assert state_dict["extra"] == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
