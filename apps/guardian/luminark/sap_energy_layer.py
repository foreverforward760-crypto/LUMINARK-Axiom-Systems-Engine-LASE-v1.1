"""
backend/luminark/sap_energy_layer.py
──────────────────────────────────────
Axiom Yield Broker — SAP Energy Layer (Logistics Domain Adapter) v1.0
Stanfield's Axiom of Perpetuity (SAP) Framework

Provides trap energy computation and stage-specific evaluation functions
for the Axiom Yield Broker's carrier risk intelligence engine.

This module is the logistics-domain adapter of the LUMINARK HybridEngine
energy layer (build1_overwatch_strict).  It exposes the three public
functions consumed by the signal translation pipeline and the demo
scenario runner:

    trap_energy(stage, nsdt_dict)                  → float [0.0, 1.0]
    evaluate_trap(stage, nsdt_dict, build)          → EvaluationResult
    evaluate_vessel_of_grounding_trap(nsdt_dict)    → VesselResult
    evaluate_dynamo_of_will_bifurcation(nsdt_dict)  → DynamoResult

INPUT SCALE CONTRACT:
    All public functions accept nsdt_dict with values on [0, 100].
    Internal computation normalises to [0, 10] to match the LUMINARK
    engine's native scale.  Never alter this contract — the scenario
    runner and the Pydantic API layer both assume [0, 100] external inputs.

DESIGN PRINCIPLE (IP Protection):
    Amplifier coefficients, chamber thresholds, and bifurcation boundary
    conditions are NOT documented in comments.  They are computed inline.
    The signal translator (sap_signal_translator.py) is the only external
    surface — raw energy values and chamber identifiers never leave this
    module through the API layer.

Author : Richard L. Stanfield / MAAT (Meridian Axiom Alignment Technologies)
Contact: LuminarkMeridian@gmail.com
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Canonical SAP stage enum  (matches sap_signal_translator.STAGE_NAMES)
# ─────────────────────────────────────────────────────────────────────────────

class SAPStage(IntEnum):
    PLENARA                    = 0
    SPARK_OF_NAVIGATION        = 1
    FORGE_OF_POLARITY          = 2
    ENGINE_OF_EXPRESSION       = 3
    CRUCIBLE_OF_EQUILIBRIUM    = 4
    DYNAMO_OF_WILL             = 5
    NEXUS_OF_HARMONY           = 6
    LENS_OF_DISTILLATION       = 7
    VESSEL_OF_GROUNDING        = 8
    TRANSPARENCY_OF_THE_GUIDE  = 9


# ─────────────────────────────────────────────────────────────────────────────
# Result dataclasses
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class EvaluationResult:
    """
    Output of evaluate_trap().
    trap_energy  : float [0.0, 1.0] — 0 = no trap, 1 = maximum trap
    chamber_active: 'A', 'B', or None (Stage 8 only)
    path          : 'A', 'B', or 'C' (Stage 5 only)
    """
    stage:          SAPStage
    trap_energy:    float
    chamber_active: Optional[str]   # Stage 8: 'A'=crystallization, 'B'=tension lock
    path:           Optional[str]   # Stage 5: 'A'=advance, 'B'=regression, 'C'=lock
    build:          str


@dataclass
class VesselResult:
    """
    Detailed output of evaluate_vessel_of_grounding_trap().
    Stage 8 — VESSEL OF GROUNDING — Illusion of Permanence.
    """
    trap_energy:     float
    chamber_active:  Optional[str]   # 'A' or 'B' or None
    illusion_score:  float           # [0.0, 1.0] — how crystallized the system is
    tension_locked:  bool            # True if Chamber B (suppressed tension lock)


@dataclass
class DynamoResult:
    """
    Detailed output of evaluate_dynamo_of_will_bifurcation().
    Stage 5 — DYNAMO OF WILL — the only stage with a backward pathway.
    """
    trap_energy:  float
    path:         str    # 'A'=advance, 'B'=regression, 'C'=lock
    advance_prob: float  # [0.0, 1.0]
    regress_prob: float  # [0.0, 1.0]
    lock_prob:    float  # [0.0, 1.0]


# ─────────────────────────────────────────────────────────────────────────────
# Internal: scale normalisation
# ─────────────────────────────────────────────────────────────────────────────

def _to_10(v: float) -> float:
    """Convert a [0, 100] input value to [0, 10] engine scale."""
    return max(0.0, min(10.0, v / 10.0))


def _nsdt_to_engine(nsdt: dict) -> tuple:
    """
    Unpack and normalise nsdt_dict [0, 100] → engine scale [0, 10].
    Returns (c, s, t, a, coh).
    """
    c   = _to_10(nsdt.get("complexity",   50.0))
    s   = _to_10(nsdt.get("stability",    50.0))
    t   = _to_10(nsdt.get("tension",      50.0))
    a   = _to_10(nsdt.get("adaptability", 50.0))
    coh = _to_10(nsdt.get("coherence",    50.0))
    return c, s, t, a, coh


# ─────────────────────────────────────────────────────────────────────────────
# Core trap energy function (LUMINARK engine formula — logistics adapter)
# ─────────────────────────────────────────────────────────────────────────────

def trap_energy(stage: SAPStage, nsdt: dict, build: str = "overwatch") -> float:
    """
    Compute trap energy for a given SAP stage and NSDT vector.

    Parameters
    ----------
    stage : SAPStage enum member
    nsdt  : dict with keys complexity, stability, tension, adaptability,
            coherence — all on [0, 100] scale
    build : engine build context ('overwatch', 'kairos', etc.)

    Returns
    -------
    float in [0.0, 1.0] — 0 = no trap, 1 = maximum trap energy
    """
    c, s, t, a, coh = _nsdt_to_engine(nsdt)

    if stage == SAPStage.VESSEL_OF_GROUNDING:
        # Illusion of Permanence Amplifier — 1.45× coefficient on Stage 8
        raw = (2.0 * coh - 1.5 * a + 1.2 * s) / 58.5
        amplified = raw * 1.45
        return max(0.0, min(1.0, amplified))

    if stage == SAPStage.LENS_OF_DISTILLATION:
        return max(0.0, min(1.0, (1.5 * t - 1.0 * a) / 13.0))

    if stage == SAPStage.DYNAMO_OF_WILL:
        return max(0.0, min(1.0, (4.0 - a) * (1.0 - (c + coh) / 2.0) / 4.0))

    if stage == SAPStage.ENGINE_OF_EXPRESSION:
        return max(0.0, min(1.0, (a - 7.0) * (4.0 - coh) / 30.0))

    if stage == SAPStage.TRANSPARENCY_OF_THE_GUIDE:
        # Dissolution threshold — maximum trap
        return max(0.0, min(1.0, (t + (10.0 - a) + (10.0 - coh)) / 30.0))

    return 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Stage 8 — VESSEL OF GROUNDING  (Illusion of Permanence)
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_vessel_of_grounding_trap(nsdt: dict) -> VesselResult:
    """
    Detailed Stage 8 evaluation — Illusion of Permanence.

    Two distinct carrier failure chambers:
        Chamber A — Crystallization: appears fully stable, zero adaptive margin.
                    Failure is silent and sudden.  24-hour window.
        Chamber B — Tension Lock: high suppressed tension, carrier cannot
                    self-recover. Failure is imminent. 12-hour window.

    Parameters
    ----------
    nsdt : dict — NSDT values on [0, 100] scale

    Returns
    -------
    VesselResult
    """
    c, s, t, a, coh = _nsdt_to_engine(nsdt)

    # Crystallization score: high stability + high coherence + low adaptability
    illusion_score = max(0.0, min(1.0, (s * 0.45 + coh * 0.35 - a * 0.45) / 5.0 + 0.2))

    # Tension lock: high stability + high tension + very low adaptability
    tension_locked = (s >= 6.0 and t >= 6.0 and a <= 3.0)

    # Chamber routing
    if tension_locked:
        chamber = "B"
    elif illusion_score >= 0.45 or (s >= 7.0 and a <= 2.5):
        chamber = "A"
    else:
        chamber = None

    # Final trap energy with Illusion of Permanence Amplifier (1.45×)
    raw = (2.0 * coh - 1.5 * a + 1.2 * s) / 58.5
    energy = max(0.0, min(1.0, raw * 1.45))

    return VesselResult(
        trap_energy=round(energy, 4),
        chamber_active=chamber,
        illusion_score=round(illusion_score, 4),
        tension_locked=tension_locked,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Stage 5 — DYNAMO OF WILL  (Bifurcation Gateway)
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_dynamo_of_will_bifurcation(
    nsdt: dict, build: str = "overwatch"
) -> DynamoResult:
    """
    Stage 5 bifurcation evaluation — the only stage with a backward pathway.

    Three possible paths:
        Path A — Advance: carrier crosses the bilateral threshold, recovery arc.
        Path B — Regression: voluntary pullback, system retains recovery capacity.
        Path C — Lock: bifurcation lock, cannot advance or safely retreat.
                       Highest-risk state.  6-hour failure window.

    Bifurcation probabilities are computed from the Stage 5 tension-adaptability
    surface.  The Observer Effect Multiplier (+35% reorganisation bonus) is
    applied when coherence is high (coh >= 7.0), reflecting clean communication
    as a stabilising factor at the gateway.

    Parameters
    ----------
    nsdt  : dict — NSDT values on [0, 100] scale
    build : engine build context

    Returns
    -------
    DynamoResult
    """
    import math
    c, s, t, a, coh = _nsdt_to_engine(nsdt)

    # Raw bifurcation scores — higher = more likely for that path
    advance_raw  = (a * 0.55 + coh * 0.35 + s * 0.10) / 10.0
    regress_raw  = (s * 0.40 + (10.0 - t) * 0.40 + coh * 0.20) / 10.0
    lock_raw     = (t * 0.55 + (10.0 - a) * 0.40 + (10.0 - coh) * 0.05) / 10.0

    # Observer Effect Multiplier: high coherence boosts advance probability
    if coh >= 7.0:
        advance_raw *= 1.35

    # Softmax normalisation → probabilities
    def softmax3(x1, x2, x3):
        e1, e2, e3 = math.exp(x1 * 3), math.exp(x2 * 3), math.exp(x3 * 3)
        total = e1 + e2 + e3
        return e1 / total, e2 / total, e3 / total

    adv_p, reg_p, lock_p = softmax3(advance_raw, regress_raw, lock_raw)

    # Hard lock condition: extreme tension + collapsed adaptability
    if t >= 8.0 and a <= 2.0:
        path = "C"
    elif adv_p >= reg_p and adv_p >= lock_p:
        path = "A"
    elif reg_p >= adv_p and reg_p >= lock_p:
        path = "B"
    else:
        path = "C"

    # Trap energy at Stage 5
    energy = max(0.0, min(1.0, (4.0 - a) * (1.0 - (c + coh) / 2.0) / 4.0))

    return DynamoResult(
        trap_energy=round(energy, 4),
        path=path,
        advance_prob=round(adv_p, 4),
        regress_prob=round(reg_p, 4),
        lock_prob=round(lock_p, 4),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Unified evaluate_trap dispatcher
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_trap(
    stage: SAPStage, nsdt: dict, build: str = "overwatch"
) -> EvaluationResult:
    """
    Unified trap evaluation dispatcher.  Routes to the stage-specific
    evaluator where one exists; falls back to the general trap_energy
    formula for all other stages.

    Parameters
    ----------
    stage : SAPStage enum member
    nsdt  : dict — NSDT values on [0, 100] scale
    build : engine build context

    Returns
    -------
    EvaluationResult — includes trap_energy, chamber, and bifurcation path
    """
    chamber = None
    path    = None

    if stage == SAPStage.VESSEL_OF_GROUNDING:
        vessel = evaluate_vessel_of_grounding_trap(nsdt)
        return EvaluationResult(
            stage=stage,
            trap_energy=vessel.trap_energy,
            chamber_active=vessel.chamber_active,
            path=None,
            build=build,
        )

    if stage == SAPStage.DYNAMO_OF_WILL:
        dynamo = evaluate_dynamo_of_will_bifurcation(nsdt, build=build)
        return EvaluationResult(
            stage=stage,
            trap_energy=dynamo.trap_energy,
            chamber_active=None,
            path=dynamo.path,
            build=build,
        )

    # General case
    energy = trap_energy(stage, nsdt, build=build)
    return EvaluationResult(
        stage=stage,
        trap_energy=energy,
        chamber_active=None,
        path=None,
        build=build,
    )
