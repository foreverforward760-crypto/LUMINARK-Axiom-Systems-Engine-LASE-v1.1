import pytest
from luminark.sap_types import NSDTVector, SAPStage, SystemState
from luminark.dissolution import DissolutionEngine

def test_should_dissolve_stage9_ready():
    nsdt = NSDTVector(
        complexity=10.0, stability=50.0, tension=10.0,
        adaptability=90.0, coherence=96.0
    )
    state = SystemState(
        stage=SAPStage.RELEASE, nsdt=nsdt, is_trap=False,
        recommended_action="", unified_field_value=0.9
    )
    should, reason = DissolutionEngine.should_dissolve(state)
    assert should is True
    assert "Stage 9 completion" in reason

def test_should_not_dissolve_stage9_not_ready():
    nsdt = NSDTVector(
        complexity=50.0, stability=50.0, tension=50.0,
        adaptability=70.0, coherence=90.0
    )
    state = SystemState(
        stage=SAPStage.RELEASE, nsdt=nsdt, is_trap=False,
        recommended_action="", unified_field_value=0.8
    )
    should, reason = DissolutionEngine.should_dissolve(state)
    assert should is False

def test_dissolve_resets_to_void():
    nsdt = NSDTVector(
        complexity=50.0, stability=50.0, tension=10.0,
        adaptability=90.0, coherence=96.0
    )
    state = SystemState(
        stage=SAPStage.RELEASE, nsdt=nsdt, is_trap=False,
        recommended_action="", unified_field_value=0.9
    )
    new_state = DissolutionEngine.dissolve(state)
    assert new_state.stage == SAPStage.VOID
    assert new_state.nsdt.complexity == 0.0
    assert new_state.nsdt.adaptability == 100.0
    assert "DISSOLVED" in new_state.recommended_action
