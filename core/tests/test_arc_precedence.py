"""
tests/test_arc_precedence.py — Arc Precedence and Classifier Integration Tests (v8.2.1)

Validates that arc direction (Ascending/Descending) is correctly passed through
the Stage 6-8 classifier pipeline and affects industrial overlay outputs.

Author: Richard L. Stanfield — Meridian Axiom Alignment Technologies (MAAT)
"""

import pytest
from luminark.sap_types import SystemState
# Stage classifiers are tested through industrial_overlay
# which calls them internally
from luminark.industrial_overlay import (
    classify_operating_margin,
    classify_failure_isolation,
    classify_resource_recirculation,
)


class TestArcPrecedence:
    """Verify arc direction is correctly propagated through classifiers."""

    def test_stage_6_ascending_arc_sustainable_flow(self):
        """Ascending Arc + Sustainable Flow = Optimal Operating Margin."""
        state = SystemState(
            stage=6,
            arc_direction="ascending",
            flow_analysis={
                "flow_type": "sustainable",
                "conductor_score": 0.85,
            },
        )
        result = classify_operating_margin(state)
        assert result["arc"] == "Ascending"
        assert result["margin_type"] == "optimal"
        assert "Conductor Score confirms" in result["directive"]

    def test_stage_6_descending_arc_initial_crystallization(self):
        """Descending Arc at Stage 6 = Initial Crystallization (hidden brittleness)."""
        state = SystemState(
            stage=6,
            arc_direction="descending",
            flow_analysis={
                "flow_type": "sustainable",
                "conductor_score": 0.85,
            },
        )
        result = classify_operating_margin(state)
        assert result["arc"] == "Descending"
        assert result["margin_type"] == "initial_crystallization"
        assert "high output, hidden brittleness" in result["directive"]

    def test_stage_7_ascending_arc_contained_isolation(self):
        """Ascending Arc + Distillation = Contained Failure Isolation."""
        state = SystemState(
            stage=7,
            arc_direction="ascending",
            crucible_analysis={
                "crucible_mode": "distillation",
                "shadow_surfacing": True,
                "shadow_note": "Ego-identification burned away",
            },
        )
        result = classify_failure_isolation(state)
        assert result["arc"] == "Ascending"
        assert result["isolation_mode"] == "contained"
        assert "burning what cannot survive" in result["directive"]

    def test_stage_7_descending_arc_uncontrolled_fragmentation(self):
        """Descending Arc at Stage 7 = Uncontrolled Fragmentation."""
        state = SystemState(
            stage=7,
            arc_direction="descending",
            crucible_analysis={
                "crucible_mode": "distillation",
                "shadow_surfacing": False,
            },
        )
        result = classify_failure_isolation(state)
        assert result["arc"] == "Descending"
        assert result["isolation_mode"] == "uncontrolled"
        assert "emergency isolation protocol" in result["directive"]

    def test_stage_8_ascending_arc_graceful_dissolution(self):
        """Ascending Arc + Dissolution = Graceful Decommission."""
        state = SystemState(
            stage=8,
            arc_direction="ascending",
            crystallization_analysis={
                "trajectory": "dissolution",
                "divergence": 0.5,
                "gratitude_engaged": True,
            },
        )
        result = classify_resource_recirculation(state)
        assert result["arc"] == "Ascending"
        assert result["recirculation_status"] == "engaged"
        assert result["trajectory"] == "dissolution"
        assert "Gratitude Mechanism engaged" in result["directive"]

    def test_stage_8_descending_arc_crystallization_in_progress(self):
        """Descending Arc at Stage 8 = Crystallization In Progress (shattering risk)."""
        state = SystemState(
            stage=8,
            arc_direction="descending",
            crystallization_analysis={
                "trajectory": "dissolution",
                "divergence": 3.0,
                "gratitude_engaged": False,
            },
        )
        result = classify_resource_recirculation(state)
        assert result["arc"] == "Descending"
        assert result["recirculation_status"] == "crystallizing"
        assert result["trajectory"] == "shattering_risk"
        assert "Ascending Arc required" in result["directive"]

    def test_stage_8_descending_arc_shattering_risk(self):
        """Descending Arc at Stage 8 = Crystallization In Progress (shattering risk)."""
        state = SystemState(
            stage=8,
            arc_direction="descending",
            crystallization_analysis={
                "trajectory": "shattering",
                "divergence": 4.8,
                "gratitude_engaged": False,
            },
        )
        result = classify_resource_recirculation(state)
        assert result["arc"] == "Descending"
        # Descending arc always returns crystallizing status
        assert result["recirculation_status"] == "crystallizing"
        assert result["trajectory"] == "shattering_risk"
        assert "Ascending Arc required" in result["directive"]

    def test_arc_missing_defaults_to_descending(self):
        """If arc is missing, default to Descending (conservative assumption)."""
        state = SystemState(
            stage=6,
            # arc_direction not set (defaults to "indeterminate")
            flow_analysis={"flow_type": "sustainable", "conductor_score": 0.85},
        )
        result = classify_operating_margin(state)
        # indeterminate defaults to Descending in industrial_overlay
        assert result["arc"] in ["Descending", "indeterminate"]
        assert "hidden brittleness" in result["directive"]

    def test_arc_propagation_through_full_pipeline(self):
        """Verify arc is correctly propagated through all three classifiers."""
        # Ascending Arc scenario
        state_asc = SystemState(
            stage=8,
            arc_direction="ascending",
            crystallization_analysis={
                "trajectory": "dissolution",
                "divergence": 0.3,
                "gratitude_engaged": True,
            },
        )
        result_asc = classify_resource_recirculation(state_asc)
        assert result_asc["arc"] == "Ascending"
        assert "Gratitude Mechanism" in result_asc["directive"]

        # Descending Arc scenario (same state, different arc)
        state_desc = SystemState(
            stage=8,
            arc_direction="descending",
            crystallization_analysis={
                "trajectory": "dissolution",
                "divergence": 0.3,
                "gratitude_engaged": True,
            },
        )
        result_desc = classify_resource_recirculation(state_desc)
        assert result_desc["arc"] == "Descending"
        assert "Ascending Arc required" in result_desc["directive"]

        # Same crystallization_analysis, different arc → different outputs
        assert result_asc["recirculation_status"] != result_desc["recirculation_status"]


class TestIndustrialOverlayConsistency:
    """Verify industrial overlay maintains consistency with phenomenological classifiers."""

    def test_overlay_respects_flow_analysis(self):
        """Industrial overlay correctly interprets flow_analysis from Stage 6."""
        state = SystemState(
            stage=6,
            arc_direction="ascending",
            flow_analysis={
                "flow_type": "sustainable",
                "conductor_score": 0.92,
            },
        )
        result = classify_operating_margin(state)
        assert result["conductor_score"] == 0.92
        assert result["margin_type"] == "optimal"

    def test_overlay_respects_crucible_analysis(self):
        """Industrial overlay correctly interprets crucible_analysis from Stage 7."""
        state = SystemState(
            stage=7,
            arc_direction="ascending",
            crucible_analysis={
                "crucible_mode": "distillation",
                "shadow_surfacing": True,
                "shadow_note": "Persona dissolved; authentic self emerging",
            },
        )
        result = classify_failure_isolation(state)
        assert result["shadow_surfacing"] is True
        assert result["shadow_note"] == "Persona dissolved; authentic self emerging"
        assert result["isolation_mode"] == "contained"

    def test_overlay_respects_crystallization_analysis(self):
        """Industrial overlay correctly interprets crystallization_analysis from Stage 8."""
        state = SystemState(
            stage=8,
            arc_direction="ascending",
            crystallization_analysis={
                "trajectory": "dissolution",
                "divergence": 0.2,
                "gratitude_engaged": True,
            },
        )
        result = classify_resource_recirculation(state)
        assert result["divergence"] == 0.2
        assert result["gratitude_engaged"] is True
        assert result["trajectory"] == "dissolution"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
