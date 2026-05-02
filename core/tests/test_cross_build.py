"""
tests/test_cross_build.py  –  Cross-build invariant test suite.

Runs the same 28 canonical NSDT vectors through Build 1 (Overwatch),
Build 3 (Defense), and Build 4 (Unified Field) and asserts that every build
respects the same SAP invariants regardless of implementation.

Build 2 (Kairos) is excluded from automated testing because it requires a
running HTTP server; its adapter is tested separately in tests/test_kairos_adapter.py.

Run with:
    pytest tests/test_cross_build.py -v
"""

import sys
import os
import pytest
import numpy as np

# Make the root luminark package importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from luminark import create_engine, NSDTVector, SAP_STAGE_NAMES

# ---------------------------------------------------------------------------
# Canonical NSDT test vectors  (28 vectors spanning all 10 stages + edge cases)
# Each entry: (label, [C, S, T, A, Coh])
# ---------------------------------------------------------------------------

CANONICAL_VECTORS = [
    # Stage 0 territory – Plenara (quiet, low everything)
    ("stage0_center",     [0.0, 0.0, 0.0, 0.0, 0.0]),
    ("stage0_near",       [0.5, 0.5, 0.5, 0.5, 0.5]),

    # Stage 1 – Spark of Navigation
    ("stage1_typical",    [1.0, 8.0, 1.0, 1.0, 1.0]),
    ("stage1_variant",    [1.5, 7.5, 1.5, 1.5, 1.5]),

    # Stage 2 – Forge of Polarity
    ("stage2_typical",    [2.0, 7.0, 2.0, 2.0, 2.0]),
    ("stage2_high_stab",  [2.5, 8.0, 1.5, 2.5, 2.5]),

    # Stage 3 – Engine of Expression
    ("stage3_typical",    [4.0, 7.0, 2.5, 3.0, 4.0]),
    ("stage3_variant",    [3.5, 6.5, 3.0, 3.0, 3.5]),

    # Stage 4 – Crucible of Equilibrium
    ("stage4_typical",    [3.5, 6.5, 3.0, 3.5, 5.0]),
    ("stage4_variant",    [4.0, 6.0, 3.5, 4.0, 5.5]),

    # Stage 5 – Dynamo of Will (bifurcation point)
    ("stage5_center",     [5.0, 4.0, 5.0, 5.0, 4.5]),
    ("stage5_high_tension",[5.5, 3.5, 6.0, 4.5, 4.0]),

    # Stage 6 – Nexus of Harmony
    ("stage6_typical",    [6.0, 5.5, 4.0, 6.0, 6.5]),
    ("stage6_variant",    [6.5, 5.0, 4.5, 6.5, 7.0]),

    # Stage 7 – Lens of Distillation
    ("stage7_typical",    [6.5, 3.0, 7.0, 7.0, 3.5]),
    ("stage7_isolation",  [7.0, 2.5, 7.5, 7.5, 3.0]),

    # Stage 8 – Vessel of Grounding (trap territory)
    ("stage8_typical",    [7.5, 7.0, 8.0, 2.0, 2.0]),
    ("stage8_high_coh",   [8.0, 8.0, 8.5, 1.5, 3.0]),
    ("stage8_vessel_of_grounding", [8.0, 7.5, 9.0, 1.0, 0.5]),

    # Stage 9 – Transparency of the Guide
    ("stage9_typical",    [8.0, 2.0, 8.5, 1.5, 1.5]),
    ("stage9_variant",    [8.5, 1.5, 9.0, 1.0, 1.0]),

    # Edge cases
    ("all_max",           [10.0, 10.0, 10.0, 10.0, 10.0]),
    ("all_mid",           [5.0, 5.0, 5.0, 5.0, 5.0]),
    ("high_tension_only", [5.0, 5.0, 10.0, 5.0, 5.0]),
    ("high_adaptability", [5.0, 5.0, 5.0, 10.0, 5.0]),
    ("low_coherence",     [5.0, 5.0, 5.0, 5.0, 0.0]),
    ("high_coherence",    [5.0, 5.0, 5.0, 5.0, 10.0]),
    ("asymmetric",        [1.0, 9.0, 2.0, 8.0, 3.0]),
]

# Builds to test (excludes kairos – requires HTTP server)
BUILDS_UNDER_TEST = ["overwatch", "defense", "unified"]


def _make_nsdt(values):
    return NSDTVector.from_list(values)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", params=BUILDS_UNDER_TEST)
def engine(request):
    """One engine per build, shared across all tests for that build (module scope)."""
    return create_engine(request.param)


# ---------------------------------------------------------------------------
# Parametrised invariant tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("label,values", CANONICAL_VECTORS)
def test_stage_in_valid_range(engine, label, values):
    """Stage must always be an integer in [0, 9]."""
    nsdt = _make_nsdt(values)
    result = engine.analyze(nsdt)
    assert 0 <= result.stage <= 9, (
        f"[{engine.build}] {label}: stage={result.stage} out of range"
    )


@pytest.mark.parametrize("label,values", CANONICAL_VECTORS)
def test_posterior_sums_to_one(engine, label, values):
    """Posterior must sum to 1.0 (probability distribution)."""
    nsdt = _make_nsdt(values)
    result = engine.analyze(nsdt)
    post_sum = sum(result.posterior)
    assert abs(post_sum - 1.0) < 1e-5, (
        f"[{engine.build}] {label}: posterior sums to {post_sum}"
    )


@pytest.mark.parametrize("label,values", CANONICAL_VECTORS)
def test_posterior_length(engine, label, values):
    """Posterior must have exactly 10 elements (one per SAP stage)."""
    nsdt = _make_nsdt(values)
    result = engine.analyze(nsdt)
    assert len(result.posterior) == 10, (
        f"[{engine.build}] {label}: posterior length={len(result.posterior)}"
    )


@pytest.mark.parametrize("label,values", CANONICAL_VECTORS)
def test_trap_energy_bounded(engine, label, values):
    """Trap energy must be in [0, 1]."""
    nsdt = _make_nsdt(values)
    result = engine.analyze(nsdt)
    assert 0.0 <= result.trap_energy <= 1.0, (
        f"[{engine.build}] {label}: trap_energy={result.trap_energy}"
    )


@pytest.mark.parametrize("label,values", CANONICAL_VECTORS)
def test_entropy_non_negative(engine, label, values):
    """Shannon entropy of posterior must be >= 0."""
    nsdt = _make_nsdt(values)
    result = engine.analyze(nsdt)
    assert result.entropy >= -1e-6, (
        f"[{engine.build}] {label}: entropy={result.entropy}"
    )


@pytest.mark.parametrize("label,values", CANONICAL_VECTORS)
def test_stage_name_canonical(engine, label, values):
    """Stage name must match the canonical SAP registry exactly."""
    nsdt = _make_nsdt(values)
    result = engine.analyze(nsdt)
    expected = SAP_STAGE_NAMES[result.stage]
    assert result.stage_name == expected, (
        f"[{engine.build}] {label}: name='{result.stage_name}' expected='{expected}'"
    )


@pytest.mark.parametrize("label,values", CANONICAL_VECTORS)
def test_arc_is_valid(engine, label, values):
    """Stage arc must be one of the three valid values."""
    nsdt = _make_nsdt(values)
    result = engine.analyze(nsdt)
    assert result.stage_arc in ("neutral", "descending", "bifurcation", "ascending"), (
        f"[{engine.build}] {label}: arc='{result.stage_arc}'"
    )


@pytest.mark.parametrize("label,values", CANONICAL_VECTORS)
def test_risk_level_valid(engine, label, values):
    """Risk level must be one of the four valid categories."""
    nsdt = _make_nsdt(values)
    result = engine.analyze(nsdt)
    assert result.risk_level in ("LOW", "MODERATE", "HIGH", "CRITICAL"), (
        f"[{engine.build}] {label}: risk_level='{result.risk_level}'"
    )


@pytest.mark.parametrize("label,values", CANONICAL_VECTORS)
def test_expected_stage_in_range(engine, label, values):
    """Expected stage (posterior mean) must lie in [0, 9]."""
    nsdt = _make_nsdt(values)
    result = engine.analyze(nsdt)
    assert 0.0 <= result.expected_stage <= 9.0, (
        f"[{engine.build}] {label}: expected_stage={result.expected_stage}"
    )


@pytest.mark.parametrize("label,values", CANONICAL_VECTORS)
def test_result_serialisation_roundtrip(engine, label, values):
    """to_dict() → from_dict() must preserve stage, energy, build."""
    nsdt = _make_nsdt(values)
    result = engine.analyze(nsdt)
    d = result.to_dict()
    restored = result.from_dict(d)
    assert restored.stage == result.stage
    assert restored.build  == result.build
    assert abs(restored.trap_energy - result.trap_energy) < 1e-9


# ---------------------------------------------------------------------------
# Build-specific additional tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("label,values", CANONICAL_VECTORS)
def test_lyapunov_present_for_defense_and_unified(engine, label, values):
    """Builds 3 & 4 must always populate the Lyapunov sub-result."""
    if engine.build not in ("defense", "unified"):
        pytest.skip("Lyapunov only in defense and unified builds")
    nsdt = _make_nsdt(values)
    result = engine.analyze(nsdt)
    assert result.lyapunov is not None, f"[{engine.build}] {label}: lyapunov is None"
    assert result.lyapunov.V >= 0.0, f"[{engine.build}] {label}: V={result.lyapunov.V}"
    assert result.defense_action in ("HOLD", "DAMPEN", "INTERVENE", "BREAK_PATTERN"), (
        f"[{engine.build}] {label}: action='{result.defense_action}'"
    )


@pytest.mark.parametrize("label,values", CANONICAL_VECTORS)
def test_unified_field_present_and_bounded(engine, label, values):
    """Build 4 must always populate UnifiedFieldState with U >= 0."""
    if engine.build != "unified":
        pytest.skip("UnifiedFieldState only in unified build")
    nsdt = _make_nsdt(values)
    result = engine.analyze(nsdt)
    uf = result.unified_field
    assert uf is not None, f"[unified] {label}: unified_field is None"
    assert uf.U >= 0.0,    f"[unified] {label}: U={uf.U} is negative"
    for comp in ("G", "P", "E", "L"):
        v = getattr(uf, comp)
        assert v >= 0.0, f"[unified] {label}: component {comp}={v} is negative"
    assert uf.gradient is not None and len(uf.gradient) == 5, (
        f"[unified] {label}: gradient={uf.gradient}"
    )


# ---------------------------------------------------------------------------
# Cross-build agreement tests  (same NSDT → builds should mostly agree on stage)
# ---------------------------------------------------------------------------

def test_all_builds_agree_on_stage_range():
    """
    For every canonical vector, all builds must report a stage in [0, 9].
    Cross-build stage values are allowed to differ (each build has its own
    transition law and tuning), but none may go out of range.
    """
    engines = {b: create_engine(b) for b in BUILDS_UNDER_TEST}
    for label, values in CANONICAL_VECTORS:
        nsdt = _make_nsdt(values)
        stages = {b: engines[b].analyze(nsdt).stage for b in BUILDS_UNDER_TEST}
        for b, s in stages.items():
            assert 0 <= s <= 9, f"{label}: build={b} stage={s} out of range"


def test_all_builds_agree_on_energy_is_bounded():
    """
    All builds must return trap_energy in [0, 1] for all canonical vectors.
    """
    engines = {b: create_engine(b) for b in BUILDS_UNDER_TEST}
    for label, values in CANONICAL_VECTORS:
        nsdt = _make_nsdt(values)
        for b in BUILDS_UNDER_TEST:
            e = engines[b].analyze(nsdt).trap_energy
            assert 0.0 <= e <= 1.0, f"{label}: build={b} energy={e} out of [0,1]"
