"""
backend/luminark/inversion_analyzer.py – SAP Stage + Trap Analyzer for AYB

Applies the Stanfield Axiom of Perpetuity (SAP) to an NSDTVector to determine
the current system stage, trap state, and recommended logistics action.

This module bridges the LUMINARK engine's mathematical core with the Axiom Yield
Broker's logistics vocabulary. It uses the same centroid-distance and energy-field
logic as the LuminarkHybridEngine, adapted for the carrier/freight domain.

SAP STAGE → LOGISTICS TRANSLATION:
    Stage 0–2 : Low activity / reserve margin
    Stage 3–4 : Normal operations, growth phase
    Stage 5    : Threshold — monitor closely, pivot point
    Stage 6    : Adaptive stress — compensating, watch
    Stage 7    : Crisis trajectory — INTERVENE NOW
    Stage 8    : Illusion of Permanence (Crystallization Paradox) — appears stable, failure imminent
    Stage 9    : Catastrophic release — immediate load recovery
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import math

from backend.luminark.nsdt_calculator import NSDTVector


class SAPStage(int, Enum):
    PLENARA            = 0
    SPARK_OF_NAVIGATION    = 1
    FORGE_OF_POLARITY      = 2
    ENGINE_OF_EXPRESSION   = 3
    CRUCIBLE_OF_EQUILIBRIUM = 4
    DYNAMO_OF_WILL         = 5
    NEXUS_OF_HARMONY       = 6
    LENS_OF_DISTILLATION   = 7
    VESSEL_OF_GROUNDING    = 8
    TRANSPARENCY_OF_THE_GUIDE = 9


# Canonical stage centroids (5D: C, S, T, A, Coh) — from LUMINARK v6.5
_CENTROIDS = {
    0: [0.0, 0.0, 0.0, 0.0, 0.0],
    1: [1.0, 8.0, 1.0, 1.0, 1.0],
    2: [2.0, 7.0, 2.0, 2.0, 2.0],
    3: [4.0, 7.0, 2.5, 3.0, 4.0],
    4: [3.5, 6.5, 3.0, 3.5, 5.0],
    5: [5.0, 4.0, 5.0, 5.0, 4.5],
    6: [6.0, 5.5, 4.0, 6.0, 6.5],
    7: [6.5, 3.0, 7.0, 7.0, 3.5],
    8: [7.5, 7.0, 8.0, 2.0, 2.0],
    9: [8.0, 2.0, 8.5, 1.5, 1.5],
}

_WEIGHTS = [1.0, 1.5, 1.5, 1.0, 0.8]
_SCALE   = 10.0


@dataclass
class SAPState:
    """Result of SAP stage analysis."""
    stage:              SAPStage
    is_trap:            bool
    trap_reason:        Optional[str]
    physical_stability: float   # [0, 1] — higher = more stable
    conscious_stability: float  # [0, 1]
    recommended_action: str
    confidence:         float   # [0, 1]


def _weighted_distance(x: list, centroid: list) -> float:
    return math.sqrt(
        sum(_WEIGHTS[i] * ((x[i] - centroid[i]) / _SCALE) ** 2 for i in range(5))
    )


def _inversion_tension(stage: SAPStage) -> tuple:
    """
    Even stages: physically stable, consciously unstable.
    Odd stages:  physically unstable, consciously stable.
    Returns (physical_stability, conscious_stability).
    """
    if stage.value % 2 == 0:   # even
        return 1.0, 0.0
    else:                       # odd
        return 0.0, 1.0


def _trap_detection(nsdt: NSDTVector, stage: SAPStage) -> tuple:
    """
    Detect SAP trap states (Stages 7, 8, 9 in logistics context).
    Returns (is_trap, reason).
    """
    if stage == SAPStage.VESSEL_OF_GROUNDING:
        # Stage 8: high stability + high tension = false permanence
        if nsdt.stability >= 7.0 and nsdt.tension >= 6.0 and nsdt.adaptability <= 3.0:
            return True, "Stage 8 Illusion of Permanence: system appears stable but has zero adaptive capacity — failure within 24-48h"
        return True, "Stage 8: structural trap active — do not assign high-value loads"

    if stage == SAPStage.TRANSPARENCY_OF_THE_GUIDE:
        return True, "Stage 9: catastrophic release imminent — immediate load recovery required"

    if stage == SAPStage.LENS_OF_DISTILLATION:
        if nsdt.tension >= 7.5 and nsdt.adaptability <= 2.5:
            return True, "Stage 7 URI pattern: tension spike + collapsed adaptability — INTERVENE NOW"

    return False, None


def _recommended_action(stage: SAPStage, is_trap: bool, nsdt: NSDTVector) -> str:
    if stage == SAPStage.TRANSPARENCY_OF_THE_GUIDE:
        return "EMERGENCY: Trigger immediate load recovery protocol. Do not dispatch."
    if stage == SAPStage.VESSEL_OF_GROUNDING or (is_trap and stage == SAPStage.LENS_OF_DISTILLATION):
        return "CRITICAL: Do not assign high-value or time-sensitive loads. Escalate to safety review."
    if stage == SAPStage.LENS_OF_DISTILLATION:
        return "URGENT: Reduce load complexity. Check in with driver every 30 minutes."
    if stage == SAPStage.NEXUS_OF_HARMONY:
        return "WATCH: Monitor closely. Assign lighter loads. Flag for next check-in."
    if stage == SAPStage.DYNAMO_OF_WILL:
        return "CAUTION: Pivot point reached. Verify driver willingness to continue. Offer rest option."
    if stage in (SAPStage.CRUCIBLE_OF_EQUILIBRIUM, SAPStage.ENGINE_OF_EXPRESSION):
        return "ROUTINE: Standard assignment. Schedule next check-in per protocol."
    if stage in (SAPStage.FORGE_OF_POLARITY, SAPStage.SPARK_OF_NAVIGATION):
        return "OPTIMIZE: Driver underutilized. Consider additional loads or reposition."
    if stage == SAPStage.PLENARA:
        return "RESERVE: Driver in rest/reset cycle. Do not dispatch until Stage 1+."
    return "MONITOR: Standard observation."


class InversionAnalyzer:
    """
    Applies SAP stage classification and trap detection to an NSDTVector.
    """

    @staticmethod
    def compute_stage(nsdt: NSDTVector) -> SAPState:
        """
        Classify the current SAP stage and detect trap conditions.

        Uses weighted centroid distance (same algorithm as LuminarkHybridEngine v6.5).
        No numpy dependency — pure Python math for edge/ELD compatibility.

        Parameters
        ----------
        nsdt : NSDTVector — 5D state vector in [0, 10]

        Returns
        -------
        SAPState — complete stage analysis result
        """
        x = nsdt.to_list()

        # Find closest centroid
        distances = {
            stage: _weighted_distance(x, centroid)
            for stage, centroid in _CENTROIDS.items()
        }
        best_stage_int = min(distances, key=distances.get)
        stage = SAPStage(best_stage_int)

        # Confidence: inverse normalised distance to closest centroid
        min_dist  = distances[best_stage_int]
        max_dist  = max(distances.values())
        confidence = 1.0 - (min_dist / max_dist) if max_dist > 0 else 1.0

        physical_s, conscious_s = _inversion_tension(stage)
        is_trap, trap_reason    = _trap_detection(nsdt, stage)
        action                  = _recommended_action(stage, is_trap, nsdt)

        return SAPState(
            stage=stage,
            is_trap=is_trap,
            trap_reason=trap_reason,
            physical_stability=round(physical_s, 2),
            conscious_stability=round(conscious_s, 2),
            recommended_action=action,
            confidence=round(confidence, 3),
        )
