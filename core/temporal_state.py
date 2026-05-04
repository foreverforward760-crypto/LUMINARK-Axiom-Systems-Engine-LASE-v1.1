"""
LUMINARK TEMPORAL STATE ENGINE
The critical missing architectural layer.
Previous system was stateless. This transforms it into a predictive behavioral model.
Every analysis updates the state. Stage 8 becomes a TRAJECTORY, not a snapshot.
"""

import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class StateSnapshot:
    """Single point in the trajectory timeline."""
    timestamp: float
    macro_stage: int
    micro_stage: int
    trapscore: float
    adaptability: float
    tension: float
    coherence: float
    trap_risk: str
    maat_score: float
    text_preview: str


@dataclass
class LuminarkState:
    """
    Persistent temporal state. This is what transforms LUMINARK from a calculator
    into a predictive behavioral model.
    """
    history: List[StateSnapshot] = field(default_factory=list)
    
    # Trajectory metrics
    risk_momentum: float = 0.0       # Rate of change toward higher risk
    rigidity_index: float = 0.0      # Sustained time at Stage 8
    recovery_index: float = 1.0      # Capacity to recover from traps
    
    # Harrowing: preserved stable configuration
    harrowing_snapshot: Optional[StateSnapshot] = None
    harrowing_active: bool = False
    
    # Session metadata
    session_id: str = ""
    session_start: float = field(default_factory=time.time)
    total_analyses: int = 0

    def record(self, snap: StateSnapshot):
        """Add snapshot and update all trajectory metrics."""
        self.history.append(snap)
        self.total_analyses += 1
        self._update_risk_momentum()
        self._update_rigidity_index(snap)
        self._update_recovery_index(snap)
        self._check_harrowing(snap)

    def _update_risk_momentum(self):
        """Rate of change toward higher risk stages over last 5 readings."""
        if len(self.history) < 2:
            self.risk_momentum = 0.0
            return
        window = self.history[-5:]
        stages = [s.macro_stage for s in window]
        if len(stages) < 2:
            return
        deltas = [stages[i+1] - stages[i] for i in range(len(stages)-1)]
        self.risk_momentum = round(sum(deltas) / len(deltas), 3)

    def _update_rigidity_index(self, snap: StateSnapshot):
        """How long has the system been at Stage 8?"""
        consecutive_8s = 0
        for s in reversed(self.history):
            if s.macro_stage == 8:
                consecutive_8s += 1
            else:
                break
        self.rigidity_index = round(min(consecutive_8s / 10.0, 1.0), 3)

    def _update_recovery_index(self, snap: StateSnapshot):
        """Ability to recover — based on adaptability and post-8 trajectory."""
        if not self.history:
            return
        recent = self.history[-3:]
        avg_adapt = sum(s.adaptability for s in recent) / len(recent)
        # If we were in Stage 8 but came down, recovery is high
        was_in_8 = any(s.macro_stage == 8 for s in self.history[:-3]) if len(self.history) > 3 else False
        now_lower = snap.macro_stage < 8
        bonus = 0.2 if (was_in_8 and now_lower) else 0.0
        self.recovery_index = round(min(avg_adapt + bonus, 1.0), 3)

    def _check_harrowing(self, snap: StateSnapshot):
        """
        Harrowing Protocol: If entering Stage 0 (reset), preserve the last
        stable configuration (Stage 4-6) for recovery.
        """
        if snap.macro_stage == 0 and not self.harrowing_active:
            # Find last stable stage
            for s in reversed(self.history[:-1]):
                if 4 <= s.macro_stage <= 6:
                    self.harrowing_snapshot = s
                    self.harrowing_active = True
                    break

    def detect_yunus_trap(self) -> Tuple[bool, str]:
        """
        Yunus Protocol (TRAJECTORY-BASED, not snapshot).
        Trigger when: sustained upward rigidity + declining adaptability + rising tension.
        Pattern: ascending toward 8, holding at 8, adaptability declining.
        This is the real behavioral signal — not a single Stage 8 reading.
        """
        if len(self.history) < 3:
            return False, "Insufficient history for trajectory analysis."

        recent = self.history[-5:]
        stages = [s.macro_stage for s in recent]
        adaptabilities = [s.adaptability for s in recent]
        tensions = [s.tension for s in recent]

        # Check: are stages trending toward or staying at 8?
        high_stage = all(s >= 7 for s in stages[-3:])
        
        # Check: is adaptability declining?
        adapt_declining = (adaptabilities[0] > adaptabilities[-1]) if len(adaptabilities) >= 2 else False
        
        # Check: is tension rising?
        tension_rising = (tensions[-1] > tensions[0]) if len(tensions) >= 2 else False
        
        # Check: explicit arrogance in recent analyses (rigidity index)
        rigidity_danger = self.rigidity_index > 0.5
        
        if high_stage and adapt_declining and tension_rising:
            return True, (
                "🚨 YUNUS PROTOCOL ACTIVATED (Trajectory-Based): "
                f"Stages {stages} — sustained upper rigidity with declining adaptability "
                f"({adaptabilities[0]:.2f} → {adaptabilities[-1]:.2f}) "
                f"and rising tension ({tensions[0]:.2f} → {tensions[-1]:.2f}). "
                "System on collapse trajectory. Deliberate un-learning required."
            )
        if rigidity_danger:
            return True, (
                f"🚨 YUNUS PROTOCOL WARNING: Rigidity Index {self.rigidity_index:.0%} — "
                "Sustained Stage 8 presence. System approaching compressed tension threshold."
            )
        return False, "Trajectory nominal. No rigidity escalation detected."

    def get_trajectory_summary(self) -> dict:
        """Full trajectory intelligence report."""
        if not self.history:
            return {"status": "No history yet."}

        stages = [s.macro_stage for s in self.history]
        trap_count = sum(1 for s in self.history if s.trap_risk in {"CRITICAL", "HIGH"})
        threshold_crossings = sum(
            1 for i in range(1, len(stages)) if stages[i-1] < 5 <= stages[i]
        )
        yunus_triggered, yunus_msg = self.detect_yunus_trap()

        return {
            "total_readings": len(self.history),
            "stage_trajectory": stages[-10:],
            "current_stage": stages[-1],
            "risk_momentum": self.risk_momentum,
            "rigidity_index": self.rigidity_index,
            "recovery_index": self.recovery_index,
            "trap_events": trap_count,
            "threshold_crossings": threshold_crossings,
            "yunus_triggered": yunus_triggered,
            "yunus_message": yunus_msg,
            "harrowing_active": self.harrowing_active,
            "harrowing_snapshot": (
                {"macro": self.harrowing_snapshot.macro_stage,
                 "micro": self.harrowing_snapshot.micro_stage,
                 "adaptability": self.harrowing_snapshot.adaptability}
                if self.harrowing_snapshot else None
            ),
            "avg_adaptability": round(
                sum(s.adaptability for s in self.history[-5:]) / min(len(self.history), 5), 3
            ),
            "avg_tension": round(
                sum(s.tension for s in self.history[-5:]) / min(len(self.history), 5), 3
            ),
        }
