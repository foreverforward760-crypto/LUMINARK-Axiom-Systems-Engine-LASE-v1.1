"""
luminark/sap_energy_layer.py
────────────────────────────
LUMINARK Canonical Energy Layer v2.1
Stanfield's Axiom of Perpetuity (SAP) Framework

Single authoritative source for all trap energy computation across the
LUMINARK ecosystem.  All apps (AxiomYield, CodeWriter, HybridEngine, Anubis)
install this module via the `luminark` pip package and import from here.

CANONICAL STAGE IDENTIFIERS — never alter:
    SAPStage.PLENARA                  = 0
    SAPStage.SPARK_OF_NAVIGATION      = 1
    SAPStage.FORGE_OF_POLARITY        = 2
    SAPStage.ENGINE_OF_EXPRESSION     = 3
    SAPStage.CRUCIBLE_OF_EQUILIBRIUM  = 4
    SAPStage.DYNAMO_OF_WILL           = 5  ← three-way bifurcation
    SAPStage.NEXUS_OF_HARMONY         = 6
    SAPStage.LENS_OF_DISTILLATION     = 7
    SAPStage.VESSEL_OF_GROUNDING      = 8  ← dual-chamber trap (1.45×)
    SAPStage.TRANSPARENCY_OF_THE_GUIDE= 9

STAGE 8 CONSTITUTIONAL DIRECTIVE:
    Chamber A = "Illusion of Arrival"     (stability high / adaptability collapsed)
    Chamber B = "Illusion of Permanence"  (tension high  / coherence collapsed)
    Construct = "Stage 8 Dual-Chamber Trap"
    DEPRECATED — must never appear: FALSE_HELL, False Hell, FALSE_HEAVEN, False Heaven

NSDT VECTOR CONTRACT:
    All public functions accept nsdt: dict with [0, 100] scale values.
    Keys: complexity, stability, tension, adaptability, coherence
    Short-form keys N, S, T, D, C also accepted.

© 2026 Richard L. Stanfield / Meridian Axiom Alignment Technologies LLC
Contact: LuminarkMeridian@gmail.com
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Canonical Stage Enum
# ─────────────────────────────────────────────────────────────────────────────

class SAPStage(IntEnum):
    PLENARA                   = 0
    SPARK_OF_NAVIGATION       = 1
    FORGE_OF_POLARITY         = 2
    ENGINE_OF_EXPRESSION      = 3
    CRUCIBLE_OF_EQUILIBRIUM   = 4
    DYNAMO_OF_WILL            = 5
    NEXUS_OF_HARMONY          = 6
    LENS_OF_DISTILLATION      = 7
    VESSEL_OF_GROUNDING       = 8
    TRANSPARENCY_OF_THE_GUIDE = 9


# ─────────────────────────────────────────────────────────────────────────────
# Constitutional Constants
# ─────────────────────────────────────────────────────────────────────────────

VESSEL_OF_GROUNDING_TRAP_AMPLIFIER: float = 1.45
"""Stage 8 TrapScore amplifier. ALWAYS reference by name — never write raw 1.45."""

VESSEL_OF_GROUNDING_CHAMBER_A: str = "Illusion of Arrival"
VESSEL_OF_GROUNDING_CHAMBER_B: str = "Illusion of Permanence"
VESSEL_OF_GROUNDING_CONSTRUCT: str = "Stage 8 Dual-Chamber Trap"

TRAP_ENERGY_NONE:     float = 0.0
TRAP_ENERGY_LOW:      float = 0.15
TRAP_ENERGY_MODERATE: float = 0.45
TRAP_ENERGY_HIGH:     float = 0.80
TRAP_ENERGY_MAXIMUM:  float = 1.00


# ─────────────────────────────────────────────────────────────────────────────
# Result Dataclasses
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Stage8TrapResult:
    """
    Result of the VESSEL OF GROUNDING dual-chamber trap evaluation.

    chamber_active:
        'A'  → Illusion of Arrival   (high stability / low adaptability)
        'B'  → Illusion of Permanence (high tension  / low coherence)
        None → healthy Stage 8 traversal, no trap active
    """
    chamber_active:    Optional[str]
    amplifier_applied: bool
    trap_energy:       float
    description:       str = field(default="")


@dataclass
class Stage5BifurcationResult:
    """
    Result of the DYNAMO OF WILL three-way bifurcation evaluation.

    path:
        'A' → Advance toward Stage 6              (TRAP_ENERGY_NONE)
        'B' → Graceful Regression toward Stage 4  (TRAP_ENERGY_MODERATE)
        'C' → Bifurcation Lock / crisis threshold  (TRAP_ENERGY_MAXIMUM)
    """
    path:        str
    trap_energy: float
    description: str = field(default="")


@dataclass
class EvaluationResult:
    """
    Unified result returned by evaluate_trap() for any stage.

    This is the primary output type for all app consumers (AxiomYield,
    CodeWriter, HybridEngine).  Provides all fields needed without
    requiring app-level branching on result type.

    Fields:
        stage          — SAPStage enum member
        trap_energy    — float [0.0, 1.0]
        trap_active    — True when trap_energy > TRAP_ENERGY_LOW
        chamber_active — 'A', 'B', or None  (Stage 8 only)
        path           — 'A', 'B', or 'C'  (Stage 5 only)
        detail         — human-readable description
    """
    stage:          SAPStage
    trap_energy:    float
    trap_active:    bool
    chamber_active: Optional[str] = None
    path:           Optional[str] = None
    detail:         str = field(default="")


# ─────────────────────────────────────────────────────────────────────────────
# NSDT Vector Unpacker
# ─────────────────────────────────────────────────────────────────────────────

def _unpack(nsdt: dict) -> tuple[float, float, float, float, float]:
    """
    Unpack NSDT vector dict → (complexity, stability, tension, adaptability, coherence).
    Accepts long-form keys or mathematical shorthand N/S/T/D/C.
    All values on [0.0, 100.0].
    """
    def _get(long: str, short: str) -> float:
        return float(nsdt.get(long, nsdt.get(short, 0.0)))

    return (
        _get("complexity",   "N"),
        _get("stability",    "S"),
        _get("tension",      "T"),
        _get("adaptability", "D"),
        _get("coherence",    "C"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Stage 8 — VESSEL OF GROUNDING: Dual-Chamber Trap
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_vessel_of_grounding_trap(nsdt: dict) -> Stage8TrapResult:
    """
    Evaluate the VESSEL OF GROUNDING (Stage 8) Dual-Chamber Trap.

    The 1.45× VESSEL_OF_GROUNDING_TRAP_AMPLIFIER is applied to the tension
    component whenever either chamber is active, surfacing the tension the
    system's own rigidity is masking.

    Chamber A — Illusion of Arrival
        Criteria: stability ≥ 70, coherence ≥ 65, adaptability ≤ 30, tension ≤ 25
        Pattern: system believes it has reached a permanent destination;
                 rigid, refuses further transition; appears rock-solid.

    Chamber B — Illusion of Permanence
        Criteria: tension ≥ 70, 35 ≤ stability ≤ 65, adaptability ≤ 30, coherence ≤ 35
        Pattern: system perceives its difficulty as permanent and inescapable;
                 cannot identify the threshold condition for Stage 9 entry.

    Release Mechanism (Gratitude Mechanism):
        Simultaneous acknowledgment of both chambers releases polarity tension
        and opens the Coherence threshold for Stage 9 dissolution.
        Dissolution thresholds: Coherence ≥ 95, Adaptability ≥ 80, Tension ≤ 20.
    """
    _, stability, tension, adaptability, coherence = _unpack(nsdt)

    # ── Chamber A: Illusion of Arrival ───────────────────────────────────────
    if (stability >= 70 and coherence >= 65 and
            adaptability <= 30 and tension <= 25):
        base    = tension / 100.0
        amplified = base * VESSEL_OF_GROUNDING_TRAP_AMPLIFIER
        rigidity  = (100.0 - adaptability) / 100.0
        energy    = min(TRAP_ENERGY_MAXIMUM, 0.40 * amplified + 0.60 * rigidity)
        return Stage8TrapResult(
            chamber_active    = "A",
            amplifier_applied = True,
            trap_energy       = round(energy, 4),
            description       = (
                f"Stage 8 — {VESSEL_OF_GROUNDING_CHAMBER_A} active. "
                f"Stability={stability:.1f}, Coherence={coherence:.1f}, "
                f"Adaptability={adaptability:.1f}. "
                f"{VESSEL_OF_GROUNDING_TRAP_AMPLIFIER}× amplifier applied. "
                f"TrapScore={energy:.4f}."
            ),
        )

    # ── Chamber B: Illusion of Permanence ────────────────────────────────────
    if (tension >= 70 and 35 <= stability <= 65 and
            adaptability <= 30 and coherence <= 35):
        base        = tension / 100.0
        amplified   = base * VESSEL_OF_GROUNDING_TRAP_AMPLIFIER
        incoherence = (100.0 - coherence) / 100.0
        energy      = min(TRAP_ENERGY_MAXIMUM, 0.65 * amplified + 0.35 * incoherence)
        return Stage8TrapResult(
            chamber_active    = "B",
            amplifier_applied = True,
            trap_energy       = round(energy, 4),
            description       = (
                f"Stage 8 — {VESSEL_OF_GROUNDING_CHAMBER_B} active. "
                f"Tension={tension:.1f}, Stability={stability:.1f}, "
                f"Coherence={coherence:.1f}. "
                f"{VESSEL_OF_GROUNDING_TRAP_AMPLIFIER}× amplifier applied. "
                f"TrapScore={energy:.4f}."
            ),
        )

    # ── Healthy Stage 8 traversal ─────────────────────────────────────────────
    return Stage8TrapResult(
        chamber_active    = None,
        amplifier_applied = False,
        trap_energy       = TRAP_ENERGY_LOW,
        description       = (
            "Stage 8 — VESSEL OF GROUNDING: healthy traversal. "
            "Neither Illusion of Arrival nor Illusion of Permanence detected."
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Stage 5 — DYNAMO OF WILL: Three-Way Bifurcation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_dynamo_of_will_bifurcation(
    nsdt: dict, build: str = "overwatch"
) -> Stage5BifurcationResult:
    """
    Evaluate the DYNAMO OF WILL (Stage 5) three-way bifurcation.

    Stage 5 is the ONLY stage in SAP with a permitted backward pathway.

    Path A — Advance (toward Stage 6, NEXUS OF HARMONY)
        Criteria: coherence ≥ 60, adaptability ≥ 55, tension ≤ 45
        TrapScore: TRAP_ENERGY_NONE (0.0)

    Path B — Graceful Regression (return to Stage 4, CRUCIBLE OF EQUILIBRIUM)
        Criteria: adaptability ≥ 40, coherence < 60, tension < 65
        TrapScore: TRAP_ENERGY_MODERATE (0.45)

    Path C — Bifurcation Lock (crisis threshold)
        All other conditions — cannot advance or safely retreat.
        TrapScore: TRAP_ENERGY_MAXIMUM (1.0)
    """
    _, _, tension, adaptability, coherence = _unpack(nsdt)

    # Path A: Advance
    if coherence >= 60 and adaptability >= 55 and tension <= 45:
        return Stage5BifurcationResult(
            path        = "A",
            trap_energy = TRAP_ENERGY_NONE,
            description = (
                "Stage 5 — Path A: Advance. "
                "System crossing bilateral threshold toward Stage 6 (NEXUS OF HARMONY). "
                f"Coherence={coherence:.1f}, Adaptability={adaptability:.1f}, "
                f"Tension={tension:.1f}."
            ),
        )

    # Path B: Graceful Regression
    if adaptability >= 40 and coherence < 60 and tension < 65:
        build_note = (
            "High-priority alert triggered." if build == "overwatch" else
            "Logged as wisdom response (kairos build)."
        )
        return Stage5BifurcationResult(
            path        = "B",
            trap_energy = TRAP_ENERGY_MODERATE,
            description = (
                "Stage 5 — Path B: Graceful Regression. "
                "System returning to Stage 4 (CRUCIBLE OF EQUILIBRIUM). "
                f"Adaptability={adaptability:.1f}, Coherence={coherence:.1f}, "
                f"Tension={tension:.1f}. {build_note}"
            ),
        )

    # Path C: Bifurcation Lock
    return Stage5BifurcationResult(
        path        = "C",
        trap_energy = TRAP_ENERGY_MAXIMUM,
        description = (
            "Stage 5 — Path C: Bifurcation Lock. "
            "System cannot advance or safely retreat. "
            f"Tension={tension:.1f}, Adaptability={adaptability:.1f}. "
            "MAXIMUM TrapScore. Immediate intervention required."
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# General Trap Energy Dispatcher
# ─────────────────────────────────────────────────────────────────────────────

def trap_energy(stage: SAPStage, nsdt: dict, build: str = "overwatch") -> float:
    """
    Returns trap energy scalar [0.0, 1.0] for any SAP stage.
    Routes Stage 5 and Stage 8 to dedicated evaluators.
    Used by the Constrained Bayesian Inference module.
    """
    _, stability, tension, adaptability, coherence = _unpack(nsdt)
    complexity = _unpack(nsdt)[0]

    if stage == SAPStage.PLENARA:
        return TRAP_ENERGY_NONE

    if stage == SAPStage.SPARK_OF_NAVIGATION:
        return TRAP_ENERGY_MODERATE if (coherence < 25 and adaptability < 30) else TRAP_ENERGY_LOW

    if stage == SAPStage.FORGE_OF_POLARITY:
        return TRAP_ENERGY_MODERATE if (tension < 20 and adaptability < 35) else TRAP_ENERGY_LOW

    if stage == SAPStage.ENGINE_OF_EXPRESSION:
        return TRAP_ENERGY_MODERATE if (coherence < 30 and complexity > 70) else TRAP_ENERGY_LOW

    if stage == SAPStage.CRUCIBLE_OF_EQUILIBRIUM:
        if tension > 65 and adaptability < 30 and coherence < 40:
            return TRAP_ENERGY_HIGH
        if tension > 50 and adaptability < 40:
            return TRAP_ENERGY_MODERATE
        return TRAP_ENERGY_LOW

    if stage == SAPStage.DYNAMO_OF_WILL:
        return evaluate_dynamo_of_will_bifurcation(nsdt, build=build).trap_energy

    if stage == SAPStage.NEXUS_OF_HARMONY:
        return TRAP_ENERGY_MODERATE if (stability > 85 and adaptability < 35) else TRAP_ENERGY_NONE

    if stage == SAPStage.LENS_OF_DISTILLATION:
        return (
            TRAP_ENERGY_MODERATE
            if (coherence > 80 and adaptability < 30 and tension > 50)
            else TRAP_ENERGY_LOW
        )

    if stage == SAPStage.VESSEL_OF_GROUNDING:
        return evaluate_vessel_of_grounding_trap(nsdt).trap_energy

    if stage == SAPStage.TRANSPARENCY_OF_THE_GUIDE:
        dissolution_ready = (coherence >= 95 and adaptability >= 80 and tension <= 20)
        if dissolution_ready:
            return TRAP_ENERGY_NONE
        return TRAP_ENERGY_LOW if build == "kairos" else TRAP_ENERGY_MODERATE

    return TRAP_ENERGY_NONE


# ─────────────────────────────────────────────────────────────────────────────
# Primary Public Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_trap(
    stage: SAPStage,
    nsdt: dict,
    build: str = "overwatch",
) -> EvaluationResult:
    """
    Primary entry point for all app consumers.

    Returns EvaluationResult with all fields populated:
        .stage          — SAPStage enum
        .trap_energy    — float [0.0, 1.0]
        .trap_active    — bool
        .chamber_active — 'A', 'B', or None  (Stage 8)
        .path           — 'A', 'B', or 'C'  (Stage 5)
        .detail         — description string

    Parameters
    ----------
    stage : SAPStage enum member
    nsdt  : dict with NSDT values on [0, 100] scale
    build : 'overwatch' | 'kairos' | 'defense' | 'unified'
    """
    if stage == SAPStage.VESSEL_OF_GROUNDING:
        s8 = evaluate_vessel_of_grounding_trap(nsdt)
        return EvaluationResult(
            stage          = stage,
            trap_energy    = s8.trap_energy,
            trap_active    = s8.chamber_active is not None,
            chamber_active = s8.chamber_active,
            path           = None,
            detail         = s8.description,
        )

    if stage == SAPStage.DYNAMO_OF_WILL:
        s5 = evaluate_dynamo_of_will_bifurcation(nsdt, build=build)
        return EvaluationResult(
            stage          = stage,
            trap_energy    = s5.trap_energy,
            trap_active    = s5.path in ("B", "C"),
            chamber_active = None,
            path           = s5.path,
            detail         = s5.description,
        )

    energy = trap_energy(stage, nsdt, build=build)
    return EvaluationResult(
        stage          = stage,
        trap_energy    = energy,
        trap_active    = energy > TRAP_ENERGY_LOW,
        chamber_active = None,
        path           = None,
        detail         = f"Stage {stage.value} ({stage.name}): trap_energy={energy:.4f}",
    )
