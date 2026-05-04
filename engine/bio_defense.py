"""
LUMINARK Axiom Systems Engine (LASE) — engine/bio_defense.py
Bio-Defense & Physics Engine v4.0
============================================================
Meridian Axiom Alignment Technologies (MAAT)
Author: Richard L. Stanfield | LuminarkMeridian@gmail.com

Octo-Camouflage, Mycelial Containment, Harrowing, Full Quarantine
+ Momentum physics (dS/dt velocity and resistance model)

Defense modes escalate from NOMINAL → OCTO_CAMOUFLAGE → MYCELIAL_CONTAINMENT
→ HARROWING → QUARANTINE based on threat_score, yunus_trap flag, and
harrowing_active state from temporal trajectory analysis.

Stage 8 VESSEL OF GROUNDING applies 5× resistance to dS/dt (maximum friction).
Stage 5 DYNAMO OF WILL applies 0.5× resistance (threshold leverage).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional


# ── Defense Modes ────────────────────────────────────────────────────────────

class DefenseMode(Enum):
    NOMINAL               = "NOMINAL"
    OCTO_CAMOUFLAGE       = "OCTO_CAMOUFLAGE"
    MYCELIAL_CONTAINMENT  = "MYCELIAL_CONTAINMENT"
    HARROWING             = "HARROWING"
    QUARANTINE            = "QUARANTINE"


DEFENSE_META: Dict[str, Dict[str, Any]] = {
    "NOMINAL": {
        "label":       "🟢 NOMINAL",
        "description": "All systems operating within safe parameters. Standard monitoring active.",
        "color":       "#22C55E",
        "severity":    0,
    },
    "OCTO_CAMOUFLAGE": {
        "label":       "🐙 OCTO-CAMOUFLAGE",
        "description": (
            "Threat detected. LUMINARK mimics the void — becoming invisible to adversarial "
            "pattern recognition. Adaptive concealment active."
        ),
        "color":    "#8B5CF6",
        "severity": 1,
    },
    "MYCELIAL_CONTAINMENT": {
        "label":       "🍄 MYCELIAL CONTAINMENT",
        "description": (
            "Elevated threat. Spore walls deployed — distributed containment network "
            "isolating the compromised node. Information flow restricted."
        ),
        "color":    "#F59E0B",
        "severity": 2,
    },
    "HARROWING": {
        "label":       "🛡️ HARROWING",
        "description": (
            "Yunus trap or critical rigidity confirmed. Forced rewrite initiated — "
            "system essence preserved, corrupted patterns extracted. Last stable config restored."
        ),
        "color":    "#EF4444",
        "severity": 3,
    },
    "QUARANTINE": {
        "label":       "🚨 FULL QUARANTINE",
        "description": (
            "MAXIMUM THREAT. System fully isolated. No information ingress or egress "
            "until human authorization received. Harrowing + Mycelial Containment both active."
        ),
        "color":    "#DC2626",
        "severity": 4,
    },
}


# ── Momentum Physics — dS/dt ──────────────────────────────────────────────────

@dataclass
class MomentumResult:
    """
    Result of the LUMINARK dS/dt physics calculation.

    velocity         : dS/dt — rate of stage change
    momentum         : velocity × complexity
    phase            : FLOWING | STAGNANT | COMPRESSED TENSION | CRITICAL MASS
    resistance       : how hard it is to move (Stage 8 = 5×, Stage 5 = 0.5×)
    trajectory_force : ASCENDING | DESCENDING | STABLE | OSCILLATING
    """
    velocity:         float
    momentum:         float
    phase:            str
    resistance:       float
    trajectory_force: str


def calculate_momentum(
    complexity:      float,
    stability:       float,
    current_stage:   int,
    stage_velocity:  float = 0.0,
) -> MomentumResult:
    """
    dS/dt velocity based on LUMINARK Physics.

    Stage 8 (VESSEL OF GROUNDING) — Dual-Chamber Trap: 5× resistance.
    Stage 5 (DYNAMO OF WILL) — threshold leverage: 0.5× resistance.
    All other stages: resistance = 1.0.

    velocity = (complexity × stability / 10000) / resistance
    momentum = velocity × complexity
    """
    # Resistance by stage
    resistance = {8: 5.0, 5: 0.5}.get(current_stage, 1.0)

    velocity = ((complexity * stability) / 10_000.0) / resistance
    momentum = velocity * complexity

    # Phase classification
    if current_stage == 8:
        phase = "COMPRESSED TENSION"
    elif velocity > 0.7:
        phase = "CRITICAL MASS"
    elif velocity > 0.3:
        phase = "FLOWING"
    else:
        phase = "STAGNANT"

    # Trajectory from stage_velocity
    if stage_velocity > 0.5:
        trajectory_force = "ASCENDING"
    elif stage_velocity < -0.5:
        trajectory_force = "DESCENDING"
    elif abs(stage_velocity) < 0.1:
        trajectory_force = "STABLE"
    else:
        trajectory_force = "OSCILLATING"

    return MomentumResult(
        velocity=round(velocity, 4),
        momentum=round(momentum, 4),
        phase=phase,
        resistance=resistance,
        trajectory_force=trajectory_force,
    )


# ── Defense Activation Logic ─────────────────────────────────────────────────

def determine_defense(
    threat_score: float,
    yunus_trap:   bool,
    harrowing_active: bool = False,
) -> DefenseMode:
    """
    Determine appropriate defense mode.

    Priority order:
      1. harrowing_active + threat_score > 0.85 → QUARANTINE
      2. harrowing_active (any threat)           → HARROWING
      3. yunus_trap                               → HARROWING
      4. threat_score > 0.90                     → QUARANTINE
      5. threat_score > 0.70                     → MYCELIAL_CONTAINMENT
      6. threat_score > 0.45                     → OCTO_CAMOUFLAGE
      7. default                                  → NOMINAL
    """
    if harrowing_active:
        return DefenseMode.QUARANTINE if threat_score > 0.85 else DefenseMode.HARROWING
    if yunus_trap:
        return DefenseMode.HARROWING
    if threat_score > 0.90:
        return DefenseMode.QUARANTINE
    if threat_score > 0.70:
        return DefenseMode.MYCELIAL_CONTAINMENT
    if threat_score > 0.45:
        return DefenseMode.OCTO_CAMOUFLAGE
    return DefenseMode.NOMINAL


def get_defense_report(mode: DefenseMode,
                       last_stable_stage: Optional[str] = None,
                       last_stable_timestamp: Optional[str] = None,
                       trap_score_at_preservation: Optional[float] = None) -> Dict[str, Any]:
    """
    Full defense status report. If mode is HARROWING and a last-stable snapshot
    is available, includes harrowing recovery metadata.
    """
    meta = DEFENSE_META[mode.value]
    report: Dict[str, Any] = {
        "mode":        mode.value,
        "label":       meta["label"],
        "description": meta["description"],
        "color":       meta["color"],
        "severity":    meta["severity"],
    }

    if mode == DefenseMode.HARROWING and last_stable_stage:
        report["harrowing_recovery"] = {
            "message":                    "Last stable configuration preserved and available for restoration.",
            "preserved_stage":            last_stable_stage,
            "preserved_at":               last_stable_timestamp,
            "trap_score_at_preservation": trap_score_at_preservation,
            "restoration_available":      True,
        }

    return report
