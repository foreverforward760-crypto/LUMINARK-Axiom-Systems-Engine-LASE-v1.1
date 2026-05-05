"""
sap_energy_layer.py
───────────────────
Luminark Hybrid Engine — Energy Layer v2.0
Stanfield's Axiom of Perpetuity (SAP) Framework

Computes trap energy for each canonical SAP stage by deforming the Bayesian
posterior probability landscape with stage-specific energy potentials.  Stages
with active trap conditions are down-weighted so the classifier correctly
identifies system vulnerability before it becomes observable in raw data.

CANONICAL STAGE IDENTIFIERS (constitutional constants — never alter):
    SAPStage.PLENARA                  = 0
    SAPStage.SPARK_OF_NAVIGATION      = 1
    SAPStage.FORGE_OF_POLARITY        = 2
    SAPStage.ENGINE_OF_EXPRESSION     = 3
    SAPStage.CRUCIBLE_OF_EQUILIBRIUM  = 4
    SAPStage.DYNAMO_OF_WILL           = 5   ← three-way bifurcation
    SAPStage.NEXUS_OF_HARMONY         = 6
    SAPStage.LENS_OF_DISTILLATION     = 7
    SAPStage.VESSEL_OF_GROUNDING      = 8   ← dual-chamber trap (1.45× amplifier)
    SAPStage.TRANSPARENCY_OF_THE_GUIDE= 9

DEPRECATED TERMS — must never appear in code, comments, or output:
    FALSE_HELL, False Hell, False Heaven, FALSE_HEAVEN, F-HELL
    These were pre-canonical designations.  Stage 8 chambers are now:
        Chamber A → Illusion of Arrival
        Chamber B → Illusion of Permanence

Author : Richard L. Stanfield / MAAT (Meridian Axiom Alignment Technologies)
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
# Constants
# ─────────────────────────────────────────────────────────────────────────────

# Stage 8 trap amplifier — surfaces suppressed tension masked by system rigidity
VESSEL_OF_GROUNDING_TRAP_AMPLIFIER: float = 1.45

# Trap energy levels returned by each stage evaluator (0.0 – 1.0 scale)
TRAP_ENERGY_NONE:     float = 0.0   # healthy traversal, no trap active
TRAP_ENERGY_LOW:      float = 0.15  # mild tension, monitor only
TRAP_ENERGY_MODERATE: float = 0.45  # active trap — alert required
TRAP_ENERGY_HIGH:     float = 0.80  # critical — immediate intervention
TRAP_ENERGY_MAXIMUM:  float = 1.00  # bifurcation lock / dissolution failure


# ─────────────────────────────────────────────────────────────────────────────
# Result dataclasses
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Stage8TrapResult:
    """
    Result of the VESSEL OF GROUNDING dual-chamber trap evaluation.

    chamber_active:
        'A'  → Illusion of Arrival   (high stability / low adaptability)
        'B'  → Illusion of Permanence (high tension  / low coherence)
        None → healthy Stage 8 traversal, no trap active

    amplifier_applied:
        True if the 1.45× TrapScore amplifier was applied to the
        tension component of the returned trap energy.

    trap_energy:
        Final deformed energy value fed to the Bayesian posterior.
    """
    chamber_active:   Optional[str]  # 'A', 'B', or None
    amplifier_applied: bool
    trap_energy:       float
    description:       str = field(default="")


@dataclass
class Stage5BifurcationResult:
    """
    Result of the DYNAMO OF WILL three-way bifurcation evaluation.

    path:
        'A' → Advance toward Stage 6             (low trap energy)
        'B' → Graceful Regression toward Stage 4 (moderate trap energy)
        'C' → Bifurcation Lock / crisis threshold (maximum trap energy)

    trap_energy:
        Final deformed energy value fed to the Bayesian posterior.
    """
    path:        str   # 'A', 'B', or 'C'
    trap_energy: float
    description: str = field(default="")


@dataclass
class TrapEnergyResult:
    """
    General trap energy result for any stage.
    """
    stage:       SAPStage
    trap_energy: float
    trap_active: bool
    detail:      str = field(default="")


# ─────────────────────────────────────────────────────────────────────────────
# NSDT vector helper
# ─────────────────────────────────────────────────────────────────────────────

def _unpack(nsdt: dict) -> tuple[float, float, float, float, float]:
    """
    Unpack an NSDT vector dict into (complexity, stability, tension,
    adaptability, coherence).  All values are on the [0.0, 100.0] scale.
    Accepts both long-form keys and the mathematical shorthand N/S/T/D/C.
    """
    def _get(long: str, short: str) -> float:
        val = nsdt.get(long, nsdt.get(short, 0.0))
        return float(val)

    complexity   = _get("complexity",   "N")
    stability    = _get("stability",    "S")
    tension      = _get("tension",      "T")
    adaptability = _get("adaptability", "D")
    coherence    = _get("coherence",    "C")
    return complexity, stability, tension, adaptability, coherence


# ─────────────────────────────────────────────────────────────────────────────
# Stage 8 — VESSEL OF GROUNDING: Dual-Chamber Trap
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_vessel_of_grounding_trap(nsdt: dict) -> Stage8TrapResult:
    """
    Evaluate the VESSEL OF GROUNDING (Stage 8) dual-chamber trap.

    The 1.45× amplifier is applied to the tension component whenever either
    chamber is detected, surfacing tension the system's own rigidity is
    masking and preventing misclassification of a deep trap as stable Stage 8.

    Chamber A — Illusion of Arrival
    ────────────────────────────────
    The system believes it has reached a permanent destination.  Coherence and
    stability are high, but adaptability has calcified.  The system resists all
    further transition because the current state feels final.

    Detection criteria:
        stability    ≥ 70
        coherence    ≥ 65
        adaptability ≤ 30
        tension      ≤ 25

    Chamber B — Illusion of Permanence
    ────────────────────────────────────
    The system perceives its difficulty or suffering as permanent and
    inescapable.  Tension is driving the vector but the system cannot identify
    the threshold condition that would allow progression to Stage 9.

    Detection criteria:
        tension      ≥ 70
        stability    ≥ 35  AND  stability ≤ 65   (moderate — not collapsed)
        adaptability ≤ 30
        coherence    ≤ 35

    When neither chamber is detected:
        Stage 8 is in healthy traversal.  Baseline trap energy, no amplifier.

    Release mechanism (Gratitude Mechanism):
        Recognition and integration of both polarity states simultaneously
        allows the Coherence threshold for Stage 9 entry to be met.
        Thresholds for dissolution: Coherence ≥ 95, Adaptability ≥ 80,
        Tension ≤ 20.
    """
    _, stability, tension, adaptability, coherence = _unpack(nsdt)

    # ── Chamber A: Illusion of Arrival ───────────────────────────────────────
    chamber_a_active = (
        stability    >= 70 and
        coherence    >= 65 and
        adaptability <= 30 and
        tension      <= 25
    )

    # ── Chamber B: Illusion of Permanence ────────────────────────────────────
    chamber_b_active = (
        tension      >= 70 and
        stability    >= 35 and stability <= 65 and
        adaptability <= 30 and
        coherence    <= 35
    )

    if chamber_a_active:
        # Apply 1.45× amplifier to tension component of trap energy.
        # Tension is low in Chamber A, but the amplifier surfaces the
        # suppressed rigidity that the system's false-arrival perception masks.
        base_tension_contribution = tension / 100.0
        amplified = base_tension_contribution * VESSEL_OF_GROUNDING_TRAP_AMPLIFIER
        # Trap energy: weighted combination of amplified tension and
        # inverted adaptability (rigidity signal).
        rigidity_signal = (100.0 - adaptability) / 100.0
        trap_energy = min(
            TRAP_ENERGY_MAXIMUM,
            0.40 * amplified + 0.60 * rigidity_signal
        )
        return Stage8TrapResult(
            chamber_active    = "A",
            amplifier_applied = True,
            trap_energy       = round(trap_energy, 4),
            description       = (
                "Stage 8 — Chamber A: Illusion of Arrival active. "
                "System perceives permanent destination. "
                f"Stability={stability:.1f}, Coherence={coherence:.1f}, "
                f"Adaptability={adaptability:.1f}. "
                f"1.45× amplifier applied. Trap energy={trap_energy:.4f}."
            )
        )

    if chamber_b_active:
        # Apply 1.45× amplifier to tension component.
        # Tension is high in Chamber B; the amplifier surfaces the full
        # depth of perceived permanence the system is trapped inside.
        base_tension_contribution = tension / 100.0
        amplified = base_tension_contribution * VESSEL_OF_GROUNDING_TRAP_AMPLIFIER
        # Trap energy: amplified tension + inverted coherence (loss-of-signal).
        incoherence_signal = (100.0 - coherence) / 100.0
        trap_energy = min(
            TRAP_ENERGY_MAXIMUM,
            0.65 * amplified + 0.35 * incoherence_signal
        )
        return Stage8TrapResult(
            chamber_active    = "B",
            amplifier_applied = True,
            trap_energy       = round(trap_energy, 4),
            description       = (
                "Stage 8 — Chamber B: Illusion of Permanence active. "
                "System perceives suffering as permanent and inescapable. "
                f"Tension={tension:.1f}, Stability={stability:.1f}, "
                f"Coherence={coherence:.1f}. "
                f"1.45× amplifier applied. Trap energy={trap_energy:.4f}."
            )
        )

    # ── Healthy Stage 8 traversal ─────────────────────────────────────────────
    # Neither chamber active.  Low baseline energy — system is moving through
    # the duality mastery phase without crystallizing in either illusion.
    trap_energy = TRAP_ENERGY_LOW
    return Stage8TrapResult(
        chamber_active    = None,
        amplifier_applied = False,
        trap_energy       = trap_energy,
        description       = (
            "Stage 8 — VESSEL OF GROUNDING: healthy traversal. "
            "Neither Illusion of Arrival nor Illusion of Permanence detected. "
            f"Trap energy={trap_energy:.4f}."
        )
    )


# ─────────────────────────────────────────────────────────────────────────────
# Stage 5 — DYNAMO OF WILL: Three-Way Bifurcation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_dynamo_of_will_bifurcation(
    nsdt: dict,
    build: str = "overwatch"
) -> Stage5BifurcationResult:
    """
    Evaluate the DYNAMO OF WILL (Stage 5) three-way bifurcation.

    Stage 5 is the only stage in the SAP framework with a permitted backward
    pathway.  All other stages permit only forward advancement or hold (trap).
    The three paths must be evaluated in order — Path A first, then B, then C.

    Path A — Advance (toward Stage 6, NEXUS OF HARMONY)
    ─────────────────────────────────────────────────────
    The system is healthy and crossing the bilateral threshold of the torus.

    Conditions (all must be met):
        coherence    ≥ 60
        adaptability ≥ 55
        tension      ≤ 45

    Trap energy: TRAP_ENERGY_NONE (0.0)
    The Observer Effect (+35% reorganization bonus applied in kairos build
    from Stage 6 onward) activates when this path is taken in Witness Position.

    Path B — Graceful Regression (return to Stage 4, CRUCIBLE OF EQUILIBRIUM)
    ──────────────────────────────────────────────────────────────────────────
    The system voluntarily returns to Stage 4.  This is a wisdom response —
    the system correctly identified it was not ready for Stage 6 integration.

    Conditions (all must be met):
        adaptability ≥ 40  (system retains capacity for movement)
        coherence    <  60
        tension      <  65

    Trap energy: TRAP_ENERGY_MODERATE (0.45)
    Build behavior:
        overwatch build → high-priority alert triggered
        kairos build    → logged as valid wisdom response, not a failure

    Path C — Bifurcation Lock (crisis threshold)
    ─────────────────────────────────────────────
    The system can neither advance nor retreat.  Highest-risk state in the
    SAP framework.  Requires immediate intervention signal.

    Conditions:
        tension      ≥ 65
        adaptability ≤ 25

    Trap energy: TRAP_ENERGY_MAXIMUM (1.0)
    Both builds trigger maximum-priority alert.

    Parameters
    ----------
    nsdt  : NSDT vector dict with keys stability/S, tension/T,
            adaptability/D, coherence/C, complexity/N.
    build : Engine build context — 'overwatch', 'kairos', 'defense',
            or 'unified'.  Affects Path B interpretation only.
    """
    _, _, tension, adaptability, coherence = _unpack(nsdt)

    # ── Path A: Advance ───────────────────────────────────────────────────────
    if coherence >= 60 and adaptability >= 55 and tension <= 45:
        return Stage5BifurcationResult(
            path        = "A",
            trap_energy = TRAP_ENERGY_NONE,
            description = (
                "Stage 5 — Path A: Advance. "
                "System is crossing the bilateral threshold toward "
                "NEXUS OF HARMONY (Stage 6). "
                f"Coherence={coherence:.1f}, Adaptability={adaptability:.1f}, "
                f"Tension={tension:.1f}. "
                + (
                    "Observer Effect active in kairos build — "
                    "+35% reorganization bonus applied Stages 6-9."
                    if build == "kairos" else ""
                )
            )
        )

    # ── Path B: Graceful Regression ───────────────────────────────────────────
    if adaptability >= 40 and coherence < 60 and tension < 65:
        build_note = (
            "High-priority alert triggered (overwatch build)."
            if build == "overwatch" else
            "Logged as wisdom response — voluntary retreat, not failure "
            "(kairos build)."
            if build == "kairos" else
            "Regression event logged."
        )
        return Stage5BifurcationResult(
            path        = "B",
            trap_energy = TRAP_ENERGY_MODERATE,
            description = (
                "Stage 5 — Path B: Graceful Regression. "
                "System returning to CRUCIBLE OF EQUILIBRIUM (Stage 4). "
                f"Adaptability={adaptability:.1f}, Coherence={coherence:.1f}, "
                f"Tension={tension:.1f}. "
                + build_note
            )
        )

    # ── Path C: Bifurcation Lock ──────────────────────────────────────────────
    # Default: if Path A and Path B conditions are not met, the system is in
    # or approaching crisis.  Explicit check confirms the lock condition.
    return Stage5BifurcationResult(
        path        = "C",
        trap_energy = TRAP_ENERGY_MAXIMUM,
        description = (
            "Stage 5 — Path C: Bifurcation Lock. "
            "System cannot advance or retreat. "
            f"Tension={tension:.1f}, Adaptability={adaptability:.1f}. "
            "MAXIMUM trap energy. Immediate intervention required."
        )
    )


# ─────────────────────────────────────────────────────────────────────────────
# General trap_energy dispatcher
# ─────────────────────────────────────────────────────────────────────────────

def trap_energy(stage: SAPStage, nsdt: dict, build: str = "overwatch") -> float:
    """
    Primary entry point for the Energy Layer.

    Returns the trap energy scalar [0.0, 1.0] for the given stage and NSDT
    vector.  This value is used by the Constrained Bayesian Inference module
    to deform the posterior probability landscape.

    Higher values = higher trap energy = stage is down-weighted in posterior.

    Parameters
    ----------
    stage : SAPStage enum member (canonical identifier)
    nsdt  : NSDT vector dict
    build : Engine build — 'overwatch', 'kairos', 'defense', or 'unified'
    """
    _, stability, tension, adaptability, coherence = _unpack(nsdt)

    # ── Stage 0: PLENARA ──────────────────────────────────────────────────────
    # Primordial state — dissolution has completed.  No trap energy.
    if stage == SAPStage.PLENARA:
        return TRAP_ENERGY_NONE

    # ── Stage 1: SPARK OF NAVIGATION ─────────────────────────────────────────
    # Fragile ignition.  Trap: insufficient coherence to orient.
    if stage == SAPStage.SPARK_OF_NAVIGATION:
        if coherence < 25 and adaptability < 30:
            return TRAP_ENERGY_MODERATE
        return TRAP_ENERGY_LOW

    # ── Stage 2: FORGE OF POLARITY ────────────────────────────────────────────
    # Polarization phase.  Trap: tension collapses without forming polarity.
    if stage == SAPStage.FORGE_OF_POLARITY:
        if tension < 20 and adaptability < 35:
            return TRAP_ENERGY_MODERATE
        return TRAP_ENERGY_LOW

    # ── Stage 3: ENGINE OF EXPRESSION ────────────────────────────────────────
    # First self-reflection and 3D complexity emerge.
    # Trap: complexity overwhelms coherence — system fragments.
    if stage == SAPStage.ENGINE_OF_EXPRESSION:
        _, complexity, tension, adaptability, coherence = _unpack(nsdt)
        if coherence < 30 and complexity > 70:
            return TRAP_ENERGY_MODERATE
        return TRAP_ENERGY_LOW

    # ── Stage 4: CRUCIBLE OF EQUILIBRIUM ─────────────────────────────────────
    # Maximum complexity threshold — forge or collapse.
    # Trap: system stalls at threshold, neither forging nor collapsing.
    if stage == SAPStage.CRUCIBLE_OF_EQUILIBRIUM:
        if tension > 65 and adaptability < 30 and coherence < 40:
            return TRAP_ENERGY_HIGH
        if tension > 50 and adaptability < 40:
            return TRAP_ENERGY_MODERATE
        return TRAP_ENERGY_LOW

    # ── Stage 5: DYNAMO OF WILL — three-way bifurcation ──────────────────────
    if stage == SAPStage.DYNAMO_OF_WILL:
        result = evaluate_dynamo_of_will_bifurcation(nsdt, build=build)
        return result.trap_energy

    # ── Stage 6: NEXUS OF HARMONY ────────────────────────────────────────────
    # Peak integration — all systems synchronized.
    # Trap (Conductor's Paradox): system over-controls and loses organic flow.
    if stage == SAPStage.NEXUS_OF_HARMONY:
        if stability > 85 and adaptability < 35:
            return TRAP_ENERGY_MODERATE
        return TRAP_ENERGY_NONE

    # ── Stage 7: LENS OF DISTILLATION ────────────────────────────────────────
    # Deep refinement.  Trap (Individuation Crucible): system over-refines
    # and cannot release distilled wisdom into action.
    if stage == SAPStage.LENS_OF_DISTILLATION:
        if coherence > 80 and adaptability < 30 and tension > 50:
            return TRAP_ENERGY_MODERATE
        return TRAP_ENERGY_LOW

    # ── Stage 8: VESSEL OF GROUNDING — dual-chamber trap ─────────────────────
    if stage == SAPStage.VESSEL_OF_GROUNDING:
        result = evaluate_vessel_of_grounding_trap(nsdt)
        return result.trap_energy

    # ── Stage 9: TRANSPARENCY OF THE GUIDE ───────────────────────────────────
    # Completion and dissolution.
    # Trap: refusal of dissolution (Stage 9 → Stage 8 regression in kairos;
    # terminal alert in overwatch if dissolution thresholds are not met after
    # extended dwell).
    if stage == SAPStage.TRANSPARENCY_OF_THE_GUIDE:
        dissolution_ready = (
            coherence    >= 95 and
            adaptability >= 80 and
            tension      <= 20
        )
        if dissolution_ready:
            return TRAP_ENERGY_NONE
        # Thresholds not met — system is dwelling without completing.
        if build == "kairos":
            # Therapeutic build: regression to Stage 8 is a valid response.
            return TRAP_ENERGY_LOW
        return TRAP_ENERGY_MODERATE

    # Fallback — unknown stage
    return TRAP_ENERGY_NONE


# ─────────────────────────────────────────────────────────────────────────────
# Full diagnostic result (for callers that need structured output)
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_trap(
    stage: SAPStage,
    nsdt: dict,
    build: str = "overwatch"
) -> TrapEnergyResult:
    """
    Returns a structured TrapEnergyResult for logging, telemetry, and UI.

    For Stage 5 and Stage 8, the detail field contains the full chamber /
    path description.  For all other stages, a concise summary is returned.
    """
    if stage == SAPStage.VESSEL_OF_GROUNDING:
        s8 = evaluate_vessel_of_grounding_trap(nsdt)
        return TrapEnergyResult(
            stage       = stage,
            trap_energy = s8.trap_energy,
            trap_active = s8.chamber_active is not None,
            detail      = s8.description
        )

    if stage == SAPStage.DYNAMO_OF_WILL:
        s5 = evaluate_dynamo_of_will_bifurcation(nsdt, build=build)
        return TrapEnergyResult(
            stage       = stage,
            trap_energy = s5.trap_energy,
            trap_active = s5.path in ("B", "C"),
            detail      = s5.description
        )

    energy = trap_energy(stage, nsdt, build=build)
    return TrapEnergyResult(
        stage       = stage,
        trap_energy = energy,
        trap_active = energy > TRAP_ENERGY_LOW,
        detail      = f"Stage {stage.value} ({stage.name}): trap_energy={energy:.4f}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Smoke test
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== SAP Energy Layer — Smoke Test ===\n")

    # Stage 8 Chamber A — Illusion of Arrival
    nsdt_s8_chamber_a = {
        "stability": 82.0, "coherence": 78.0,
        "adaptability": 18.0, "tension": 12.0, "complexity": 55.0
    }
    r = evaluate_vessel_of_grounding_trap(nsdt_s8_chamber_a)
    print(f"Stage 8 Chamber A test:\n  {r.description}\n")

    # Stage 8 Chamber B — Illusion of Permanence
    nsdt_s8_chamber_b = {
        "stability": 50.0, "coherence": 22.0,
        "adaptability": 15.0, "tension": 85.0, "complexity": 60.0
    }
    r = evaluate_vessel_of_grounding_trap(nsdt_s8_chamber_b)
    print(f"Stage 8 Chamber B test:\n  {r.description}\n")

    # Stage 8 healthy traversal
    nsdt_s8_healthy = {
        "stability": 65.0, "coherence": 60.0,
        "adaptability": 55.0, "tension": 40.0, "complexity": 50.0
    }
    r = evaluate_vessel_of_grounding_trap(nsdt_s8_healthy)
    print(f"Stage 8 Healthy traversal test:\n  {r.description}\n")

    # Stage 5 Path A — Advance
    nsdt_s5_advance = {
        "stability": 60.0, "coherence": 72.0,
        "adaptability": 65.0, "tension": 30.0, "complexity": 45.0
    }
    r = evaluate_dynamo_of_will_bifurcation(nsdt_s5_advance, build="overwatch")
    print(f"Stage 5 Path A test:\n  {r.description}\n")

    # Stage 5 Path B — Graceful Regression
    nsdt_s5_regression = {
        "stability": 55.0, "coherence": 45.0,
        "adaptability": 50.0, "tension": 55.0, "complexity": 40.0
    }
    r = evaluate_dynamo_of_will_bifurcation(nsdt_s5_regression, build="kairos")
    print(f"Stage 5 Path B test:\n  {r.description}\n")

    # Stage 5 Path C — Bifurcation Lock
    nsdt_s5_lock = {
        "stability": 40.0, "coherence": 30.0,
        "adaptability": 15.0, "tension": 88.0, "complexity": 70.0
    }
    r = evaluate_dynamo_of_will_bifurcation(nsdt_s5_lock, build="overwatch")
    print(f"Stage 5 Path C test:\n  {r.description}\n")

    # Full dispatcher sweep
    print("Full trap_energy dispatcher sweep:")
    test_nsdt = {
        "stability": 55.0, "coherence": 50.0,
        "adaptability": 45.0, "tension": 50.0, "complexity": 50.0
    }
    for s in SAPStage:
        e = trap_energy(s, test_nsdt, build="overwatch")
        print(f"  {s.value} {s.name:<32} trap_energy={e:.4f}")


"""
Energy Layer v6.5 – Trap potentials as a true energy field,
with total energy and gradient computation.
"""

import numpy as np
from typing import List, Optional

class SAPEnergy:
    @staticmethod
    def trap_energy(stage: int, x: List[float]) -> float:
        """Geometry‑derived energy potential for a given stage (0‑1 range)."""
        c, s, t, a, coh = x
        if stage == 8:  # Illusion of Permanence (Crystallization Paradox)
            return max(0.0, min(1.0, (2.0 * coh - 1.5 * a + 1.2 * s) / 5.0))
        if stage == 7:  # Permanent isolation
            return max(0.0, min(1.0, (1.5 * t - 1.0 * a) / 5.0))
        if stage == 5:  # Stagnation at bifurcation
            return max(0.0, min(1.0, (4.0 - a) * (1.0 - (c + coh) / 2.0) / 4.0))
        if stage == 3:  # Avoidance disguised as discipline
            return max(0.0, min(1.0, (a - 7.0) * (4.0 - coh) / 30.0))
        return 0.0

    @staticmethod
    def compute_total_energy(x: List[float], posterior: np.ndarray) -> float:
        """
        Total energy = expectation of per‑stage trap energy over posterior.
        Returns value in 0.0–1.0 range (no arbitrary scaling).
        """
        total = 0.0
        for stage, p in enumerate(posterior):
            total += p * SAPEnergy.trap_energy(stage, x)
        return total

    @staticmethod
    def compute_gradient(x: List[float], posterior: np.ndarray,
                         epsilon: float = 1e-5) -> List[float]:
        """
        Finite‑difference gradient of total energy w.r.t. each NSDT dimension.
        Returns vector of 5 floats.
        """
        grad = []
        for i in range(5):
            x_plus = x.copy()
            x_plus[i] += epsilon
            e_plus = SAPEnergy.compute_total_energy(x_plus, posterior)

            x_minus = x.copy()
            x_minus[i] -= epsilon
            e_minus = SAPEnergy.compute_total_energy(x_minus, posterior)

            grad.append((e_plus - e_minus) / (2 * epsilon))
        return grad

    @staticmethod
    def modulate_logits(logits: np.ndarray, x: List[float], beta: float = 0.8) -> np.ndarray:
        """Deform the probability landscape with energy potentials."""
        energies = np.array([SAPEnergy.trap_energy(s, x) for s in range(10)])
        return logits - beta * energies
