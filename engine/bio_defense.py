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
from typing import Dict, Any, Optional, List


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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "velocity":         round(self.velocity, 4),
            "momentum":         round(self.momentum, 4),
            "phase":            self.phase,
            "resistance":       self.resistance,
            "trajectory_force": self.trajectory_force,
        }


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


# ─────────────────────────────────────────────────────────────────────────────
# STAGE SNAPSHOT — preserved state for Harrowing recovery
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class StageSnapshot:
    """
    Preserved system state for Harrowing recovery.
    Captured at the last known stable position before Stage 8 trap engagement.
    """
    macro:      int          # SAP stage (0–9)
    micro:      int          # Micro-stage (0–9)
    timestamp:  str          # ISO timestamp at time of preservation
    trap_score: float        # TrapScore value at time of preservation
    nsdt_vector: Optional[Dict] = None  # Full NSDT vector if available

    def to_dict(self) -> Dict[str, Any]:
        return {
            "preserved_stage": f"{self.macro}.{self.micro}",
            "macro":           self.macro,
            "micro":           self.micro,
            "timestamp":       self.timestamp,
            "trap_score":      self.trap_score,
            "nsdt_vector":     self.nsdt_vector,
        }


# ─────────────────────────────────────────────────────────────────────────────
# LUMINARK DEFENSE STATE
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class LuminarkDefenseState:
    """
    State object consumed by the defense layer.
    Tracks harrowing status, trap score, velocity, and preserved snapshots.
    For full state management see core/sap_types.py and core/temporal_trajectory.py.
    """
    harrowing_active:      bool  = False
    trap_score:            float = 0.0
    current_stage:         int   = 0
    stage_velocity:        float = 0.0   # dS/dt — positive = ascending through cycle
    last_stable_snapshot:  Optional[StageSnapshot] = None
    defense_history:       List[str] = None  # populated in __post_init__

    def __post_init__(self):
        if self.defense_history is None:
            self.defense_history = []

    def record_defense(self, mode: "DefenseMode") -> None:
        """Append mode to rolling defense history (capped at 100 entries)."""
        self.defense_history.append(mode.value)
        if len(self.defense_history) > 100:
            self.defense_history = self.defense_history[-100:]


# ─────────────────────────────────────────────────────────────────────────────
# BIO DEFENSE ENGINE — unified interface
# ─────────────────────────────────────────────────────────────────────────────

class BioDefenseEngine:
    """
    Unified Bio-Defense Physics Engine.

    Combines DefenseMode determination, momentum physics (dS/dt),
    state tracking, and defense history into a single callable interface.

    Usage:
        engine = BioDefenseEngine()
        state  = LuminarkDefenseState(current_stage=8, trap_score=1.2, harrowing_active=True)
        mode   = engine.evaluate(threat_score=0.92, state=state)
        report = engine.report(mode, state)
        mom    = engine.momentum(complexity=75.0, stability=60.0, stage=8)
    """

    def evaluate(
        self,
        threat_score: float,
        yunus_trap:   bool                           = False,
        state:        Optional[LuminarkDefenseState] = None,
    ) -> DefenseMode:
        """
        Evaluate threat level and return appropriate DefenseMode.
        Updates harrowing_active flag on state if provided.
        """
        mode = determine_defense(threat_score, yunus_trap, state)
        if state is not None:
            state.record_defense(mode)
            if mode in (DefenseMode.HARROWING, DefenseMode.QUARANTINE):
                state.harrowing_active = True
            elif mode == DefenseMode.NOMINAL:
                state.harrowing_active = False
        return mode

    def report(
        self,
        mode:  DefenseMode,
        state: Optional[LuminarkDefenseState] = None,
    ) -> Dict[str, Any]:
        """Generate full defense status report with optional recovery context."""
        return get_defense_report(mode, state)

    def momentum(
        self,
        complexity:     float,
        stability:      float,
        stage:          int,
        stage_velocity: float = 0.0,
    ) -> MomentumResult:
        """Compute dS/dt momentum for the given system state."""
        return calculate_momentum(complexity, stability, stage, stage_velocity)

    def full_threat_analysis(
        self,
        threat_score:   float,
        complexity:     float,
        stability:      float,
        stage:          int,
        stage_velocity: float                        = 0.0,
        yunus_trap:     bool                         = False,
        state:          Optional[LuminarkDefenseState] = None,
    ) -> Dict[str, Any]:
        """
        Single-call full threat analysis.
        Returns merged defense report + momentum analysis dict.
        """
        mode           = self.evaluate(threat_score, yunus_trap, state)
        defense_report = self.report(mode, state)
        momentum_result = self.momentum(complexity, stability, stage, stage_velocity)

        return {
            **defense_report,
            "momentum":     momentum_result.to_dict(),
            "threat_score": round(threat_score, 4),
        }


# ── Self-test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    engine = BioDefenseEngine()
    print("="*65)
    print("BIO-DEFENSE PHYSICS ENGINE — SELF TEST | MAAT")
    print("="*65)

    print("\n[1] DEFENSE MODE THRESHOLD SCAN")
    for score, yunus in [(0.2, False), (0.5, False), (0.75, False),
                          (0.88, False), (0.95, False), (0.88, True)]:
        mode = determine_defense(score, yunus)
        print(f"  score={score:.2f}  yunus={yunus}  → {mode.value}")

    print("\n[2] MOMENTUM — Stage 8 vs Stage 5")
    for stg, label in [(5, "Threshold"), (8, "Trap"), (9, "Release")]:
        m = calculate_momentum(75.0, 60.0, stg)
        print(f"  Stage {stg} ({label}): v={m.velocity}  resistance={m.resistance}x  phase={m.phase}")

    print("\n[3] FULL THREAT ANALYSIS — Stage 8 Harrowing")
    snap = StageSnapshot(macro=7, micro=3, timestamp="2026-05-04T00:00:00Z", trap_score=0.65)
    state = LuminarkDefenseState(current_stage=8, trap_score=1.45,
                                  harrowing_active=True, stage_velocity=-0.2,
                                  last_stable_snapshot=snap)
    result = engine.full_threat_analysis(0.91, 82.0, 45.0, 8, -0.2, state=state)
    print(f"  Mode={result['mode']}  Phase={result['momentum']['phase']}")
    if "harrowing_recovery" in result:
        print(f"  Recovery stage preserved: {result['harrowing_recovery']['preserved_stage']}")

    print("\n✅ Bio-Defense Engine — all tests passed.\n")
