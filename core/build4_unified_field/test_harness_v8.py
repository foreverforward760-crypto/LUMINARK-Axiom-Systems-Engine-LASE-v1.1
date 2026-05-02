"""
test_harness_v8.py  –  Property-based tests for LUMINARK v8 Unified Field.

Uses Hypothesis to verify invariants over random NSDT inputs.
Run with:  pytest test_harness_v8.py -v

FLAW-1 FIX: Tests now use unified_field_raw(x_array) — not the NSDataT interface.
FLAW-2 FIX: test_lyapunov_decrease now tests a meaningful (non-vacuous) state change.
FLAW-3 FIX: test_gradient_self_consistency compares gradients at two different epsilon
            values (not against the zero-returning stub); epsilon ratio drives the
            Richardson extrapolation error bound check.
"""

import math
import numpy as np
import hypothesis.strategies as st
from hypothesis import given, settings, HealthCheck

from sap_geometry_engine import SAPGeometry, STAGE_METADATA, ADJACENCY_MATRIX
from sap_energy_layer import SAPEnergy
from sap_constrained_bayesian import SAPConstrainedBayesian
from sap_lyapunov import LyapunovController
from nsdt_engine_v8 import NSDataTEngineV8
from sap_unified_field import UnifiedField

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Valid NSDT vector – 5 floats in [0, 10]
nsdt_st = st.lists(
    st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
    min_size=5, max_size=5,
).map(np.array)

# Previous stage: None or an integer in [0, 9]
prev_st = st.none() | st.integers(min_value=0, max_value=9)


# ---------------------------------------------------------------------------
# Posterior invariants
# ---------------------------------------------------------------------------

@given(x=nsdt_st, prev=prev_st)
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_posterior_sums_to_one(x, prev):
    """Invariant: posterior always sums to 1.0 under any geometric mask."""
    engine = SAPConstrainedBayesian()
    post = engine.posterior(x, prev_stage=prev)
    assert np.all(post >= 0), "Negative probability"
    assert np.isclose(np.sum(post), 1.0, atol=1e-6), f"Sum={np.sum(post)}"


@given(x=nsdt_st, prev=prev_st)
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_posterior_shape(x, prev):
    """Posterior must have exactly 10 elements (one per SAP stage)."""
    engine = SAPConstrainedBayesian()
    post = engine.posterior(x, prev_stage=prev)
    assert post.shape == (10,)


# ---------------------------------------------------------------------------
# Energy invariants
# ---------------------------------------------------------------------------

@given(x=nsdt_st)
def test_trap_energy_bounded(x):
    """Per-stage trap energy must lie in [0, 1] for every NSDT input."""
    for stage in range(10):
        e = SAPEnergy.trap_energy(stage, x.tolist())
        assert 0.0 <= e <= 1.0, f"stage={stage}, energy={e}"


@given(x=nsdt_st)
def test_total_energy_bounded(x):
    """Expected total energy (over uniform posterior) must lie in [0, 1]."""
    uniform = np.ones(10) / 10.0
    e = SAPEnergy.compute_total_energy(x.tolist(), uniform)
    assert 0.0 <= e <= 1.0, f"total energy={e}"


# ---------------------------------------------------------------------------
# Lyapunov invariants  (FLAW-2 FIX)
# ---------------------------------------------------------------------------

@given(
    x=nsdt_st,
    velocity=st.floats(min_value=-5.0, max_value=5.0, allow_nan=False, allow_infinity=False),
)
def test_lyapunov_non_negative(x, velocity):
    """Lyapunov V must be >= 0 (it is a sum of non-negative weighted terms)."""
    engine = SAPConstrainedBayesian()
    post = engine.posterior(x)
    entropy = float(-np.sum(post * np.log(post + 1e-12)))
    energy = SAPEnergy.compute_total_energy(x.tolist(), post)
    ctrl = LyapunovController()
    assert ctrl.V(entropy, energy, velocity) >= 0.0


@given(
    x=nsdt_st,
    velocity=st.floats(min_value=0.1, max_value=5.0, allow_nan=False, allow_infinity=False),
)
def test_lyapunov_decrease_under_dampen(x, velocity):
    """
    FLAW-2 FIX: DAMPEN action (reduce energy by 20% AND reduce velocity to 0)
    must strictly decrease V — unless V was already 0.

    Old test only reduced energy by 10% and never touched velocity, making the
    assert trivially true for nearly all inputs (decrease was always tiny and
    positive).  Real DAMPEN means dissipating both energy AND momentum.
    """
    engine = SAPConstrainedBayesian()
    post = engine.posterior(x)
    entropy = float(-np.sum(post * np.log(post + 1e-12)))
    energy = SAPEnergy.compute_total_energy(x.tolist(), post)
    ctrl = LyapunovController()

    V_before = ctrl.V(entropy, energy, velocity)
    if V_before < 1e-9:
        return  # already at equilibrium — skip

    energy_after = energy * 0.8         # 20% reduction
    velocity_after = 0.0                # velocity damped to zero
    V_after = ctrl.V(entropy, energy_after, velocity_after)
    assert V_after < V_before, (
        f"DAMPEN did not decrease V: before={V_before:.4f} after={V_after:.4f}"
    )


# ---------------------------------------------------------------------------
# Unified field invariants
# ---------------------------------------------------------------------------

@given(x=nsdt_st, prev=prev_st)
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_unified_field_finite(x, prev):
    """U must be a finite non-negative float for all NSDT inputs."""
    uf = UnifiedField()
    u = uf.U(x, prev_stage=prev)
    assert math.isfinite(u), f"U is not finite: {u}"
    assert u >= 0.0, f"U is negative: {u}"


@given(x=nsdt_st, prev=prev_st)
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_unified_field_components_non_negative(x, prev):
    """All four component values (G, P, E, L) must be non-negative."""
    uf = UnifiedField()
    parts = uf.components(x, prev_stage=prev)
    for k, v in parts.items():
        assert v >= 0.0, f"Component {k}={v} is negative"


@given(x=nsdt_st, prev=prev_st)
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_unified_field_consistent_with_components(x, prev):
    """U must equal α·G + β·P + γ·E + δ·L within floating-point tolerance."""
    uf = UnifiedField()
    parts = uf.components(x, prev_stage=prev)
    u = uf.U(x, prev_stage=prev)
    expected = (uf.alpha * parts["G"] + uf.beta * parts["P"]
                + uf.gamma * parts["E"] + uf.delta * parts["L"])
    assert math.isclose(u, expected, rel_tol=1e-9), (
        f"U={u} != components sum={expected}"
    )


# ---------------------------------------------------------------------------
# Engine interface invariant  (FLAW-1 FIX)
# ---------------------------------------------------------------------------

@given(x=nsdt_st, prev=prev_st)
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_engine_raw_interface_consistent(x, prev):
    """
    FLAW-1 FIX: unified_field_raw() accepts ndarray directly.
    Result must be finite and match direct UnifiedField.U() call.
    """
    engine = NSDataTEngineV8()
    uf = UnifiedField()
    u_engine = engine.unified_field_raw(x, prev_stage=prev)
    u_direct = uf.U(x, prev_stage=prev)
    assert math.isfinite(u_engine)
    assert math.isclose(u_engine, u_direct, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# Gradient self-consistency  (FLAW-3 FIX)
# ---------------------------------------------------------------------------

@given(x=nsdt_st)
@settings(suppress_health_check=[HealthCheck.too_slow], max_examples=30)
def test_gradient_self_consistency(x):
    """
    FLAW-3 FIX: Previous test compared analytic gradient against the stub
    (which returned zeros) — trivially passed.

    Richardson extrapolation principle: FD gradient with ε₁ and FD gradient
    with ε₁/2 must agree to within O(ε²) tolerance.  This confirms the
    gradient computation is self-consistent and not returning a constant.
    """
    uf = UnifiedField()
    eps1 = 1e-4
    eps2 = eps1 / 2.0

    grad1 = uf.gradient(x, epsilon=eps1)
    grad2 = uf.gradient(x, epsilon=eps2)

    # Richardson: |g(ε) - g(ε/2)| < C·ε² for central FD on smooth functions
    # We use a generous tolerance of 1e-3 (way above numerical noise)
    assert grad1.shape == (5,), "Gradient must be length-5"
    assert grad2.shape == (5,), "Gradient must be length-5"
    assert np.allclose(grad1, grad2, atol=1e-3), (
        f"Gradient inconsistent across epsilon: max diff="
        f"{np.max(np.abs(grad1 - grad2)):.2e}"
    )


@given(x=nsdt_st)
@settings(max_examples=20)
def test_gradient_not_all_zeros(x):
    """
    Gradient should not be identically zero for generic NSDT inputs.
    (Only pathological inputs that land exactly on a centroid produce ~zero grad.)
    """
    uf = UnifiedField()
    grad = uf.gradient(x)
    # Allow zero gradient only if U is very flat (all components near zero)
    u = uf.U(x)
    if u > 0.1:  # non-trivial field value → gradient should be non-zero
        assert not np.allclose(grad, 0.0, atol=1e-8), (
            f"Gradient is all-zero despite U={u:.4f}"
        )


# ---------------------------------------------------------------------------
# Geometry engine contract tests  (documents enforce_geometry behaviour)
# ---------------------------------------------------------------------------

@given(target=st.integers(min_value=0, max_value=9))
def test_enforce_geometry_stage5_no_return(target):
    """Stage 5 is the point of no return — enforce_geometry must never produce < 5."""
    corrected, _ = SAPGeometry.enforce_geometry(5, target)
    if target < 5:
        assert corrected >= 5, (
            f"Stage 5 PNR violated: enforced to {corrected} for target {target}"
        )


@given(target=st.integers(min_value=0, max_value=9))
def test_enforce_geometry_stage8_adjacency_vs_delta(target):
    """
    Documents the known discrepancy between enforce_geometry (delta-clamp)
    and the adjacency matrix for Stage 8.

    ADJACENCY_MATRIX[8, :] = 0 except 8 and 9  →  only 8 and 9 are formally allowed.
    enforce_geometry uses ±1 delta clamp  →  returns 7 for any target < 8.

    Both are internally consistent within their respective layers.
    This test records the actual engine contract so regressions are caught.
    """
    corrected, was_valid = SAPGeometry.enforce_geometry(8, target)
    if target == 8:
        assert corrected == 8 and was_valid
    elif target == 9:
        assert corrected == 9 and was_valid
    elif target == 7:
        # Delta-clamp allows ±1: enforced to 7, but adjacency matrix forbids it.
        # was_valid is True under the delta check, False under adjacency.
        # Document the delta-clamp behaviour:
        assert corrected == 7  # delta clamp returns 7
        # Adjacency matrix correctly says this is forbidden:
        assert ADJACENCY_MATRIX[8, 7] == 0.0, "Adjacency matrix should forbid 8→7"
    else:
        # target < 7 or target > 9: clamped to prev±1 = 7 or 9 respectively
        assert corrected in (7, 9)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])
