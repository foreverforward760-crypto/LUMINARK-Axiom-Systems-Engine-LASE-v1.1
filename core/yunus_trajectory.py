"""
LUMINARK v4.0 — Yunus Protocol (Proper Trajectory Implementation)
CRITICAL FIX from technical review:
  OLD: triggered on single Stage 8 snapshot
  NEW: triggered on sustained upward rigidity trajectory

The Yunus story is not about a snapshot failure.
It is about runaway escalation followed by voluntary interruption.

Founder: Richard L. Stanfield | METATRON Align With Purpose
"""

import re
from typing import Dict, List, Any, Optional
from luminark.state import LuminarkState, StateSnapshot


# =============================================================================
# LINGUISTIC RISK PATTERNS
# =============================================================================

ARROGANCE_PATTERNS = re.compile(
    r"\b(absolute|undeniable|100%|impossible to fail|guaranteed|perfect|"
    r"risk-free|too big to fail|foolproof|unbreakable|flawless|"
    r"cannot fail|will never fail|infallible)\b",
    re.IGNORECASE
)

COUNTERFACTUAL_PATTERNS = re.compile(
    r"\b(what if|worst-case|failure mode|edge case|assumption|contingency|"
    r"however|unless|except|risk|caveat|downside|limitation|"
    r"could fail|might not|uncertain|possibly)\b",
    re.IGNORECASE
)

ELIMINATION_FRAMING = re.compile(
    r"\b(crush|destroy|eliminate|dominate|obliterate|wipe out|eradicate)\b",
    re.IGNORECASE
)

INVULNERABILITY_LANGUAGE = re.compile(
    r"\b(nothing can stop|unstoppable|inevitable|certain victory|no alternative)\b",
    re.IGNORECASE
)


# =============================================================================
# TRAJECTORY PATTERNS (the core innovation)
# =============================================================================

def _detect_sustained_rigidity(snapshots: List[StateSnapshot]) -> Dict[str, Any]:
    """
    Detects sustained upward rigidity — the true Yunus trigger.
    Pattern: ascending stages 6→7→8→8→8 WITH decreasing adaptability AND rising tension.
    This is a behavioral trajectory, not a snapshot.
    """
    if len(snapshots) < 3:
        return {"detected": False, "confidence": 0.0, "pattern": []}
    
    recent = snapshots[-5:]  # Last 5 readings
    stages = [s.macro for s in recent]
    adaptabilities = [s.adaptability for s in recent]
    tensions = [s.tension for s in recent]
    
    # Check: stages are high (>= 6) and not decreasing
    high_stage = all(s >= 6 for s in stages)
    stage_ascending = stages[-1] >= stages[0]
    
    # Check: adaptability is decreasing
    adapt_declining = adaptabilities[-1] < adaptabilities[0] if len(adaptabilities) >= 2 else False
    
    # Check: tension is rising
    tension_rising = tensions[-1] > tensions[0] if len(tensions) >= 2 else False
    
    # Check: stage 8 sustained (stuck)
    stage_8_sustained = sum(1 for s in stages if s >= 8) >= 2
    
    detected = high_stage and stage_ascending and adapt_declining and stage_8_sustained
    
    confidence = 0.0
    if high_stage: confidence += 0.3
    if stage_ascending: confidence += 0.2
    if adapt_declining: confidence += 0.25
    if tension_rising: confidence += 0.15
    if stage_8_sustained: confidence += 0.1
    
    return {
        "detected": detected,
        "confidence": round(confidence, 2),
        "pattern": stages,
        "adaptability_trend": round(adaptabilities[-1] - adaptabilities[0], 3) if len(adaptabilities) >= 2 else 0,
        "tension_trend": round(tensions[-1] - tensions[0], 3) if len(tensions) >= 2 else 0,
    }


# =============================================================================
# YUNUS PROTOCOL — Full Analysis
# =============================================================================

class YunusProtocol:
    """
    Full epistemic humility and rigidity trap detection.
    Combines linguistic analysis WITH trajectory analysis.
    """

    @classmethod
    def analyze(
        cls,
        text: str,
        current_stage: int,
        state: Optional[LuminarkState] = None,
    ) -> Dict[str, Any]:
        
        arrogance_hits = len(ARROGANCE_PATTERNS.findall(text))
        cf_hits = len(COUNTERFACTUAL_PATTERNS.findall(text))
        elim_hits = len(ELIMINATION_FRAMING.findall(text))
        invuln_hits = len(INVULNERABILITY_LANGUAGE.findall(text))
        
        score = 100.0
        flags = []
        stage_8_snapshot_trap = False
        trajectory_trap = False
        trajectory_data = {}

        # ── LINGUISTIC ANALYSIS ──────────────────────────────────────────────
        if arrogance_hits > 0:
            penalty = arrogance_hits * (15 if cf_hits == 0 else 5)
            score = max(0.0, score - penalty)
            
            if current_stage >= 7 and cf_hits == 0:
                stage_8_snapshot_trap = True
                flags.append(
                    f"⚠ RIGIDITY LANGUAGE: {arrogance_hits} arrogance marker(s) "
                    f"detected at Stage {current_stage} with zero counterfactuals. "
                    f"Epistemic humility compromised."
                )
            else:
                flags.append(f"Arrogance markers detected ({arrogance_hits}). "
                             f"Counterfactuals present ({cf_hits}) — partially mitigated.")

        if elim_hits > 0:
            score = max(0.0, score - elim_hits * 10)
            flags.append(f"Elimination framing detected ({elim_hits}). "
                         f"Coercive/absolute language reduces epistemic safety.")

        if invuln_hits > 0:
            score = max(0.0, score - invuln_hits * 12)
            flags.append(f"Invulnerability language detected ({invuln_hits}). "
                         f"System claiming exemption from failure modes.")

        # ── TRAJECTORY ANALYSIS (the real Yunus trigger) ─────────────────────
        if state and len(state.snapshots) >= 3:
            trajectory_data = _detect_sustained_rigidity(state.snapshots)
            
            if trajectory_data["detected"]:
                trajectory_trap = True
                pattern_str = " → ".join(f"Stage {s}" for s in trajectory_data["pattern"])
                flags.insert(0,
                    f"🚨 YUNUS PROTOCOL ACTIVATED: Sustained rigidity trajectory detected. "
                    f"Pattern: {pattern_str}. "
                    f"Adaptability trend: {trajectory_data['adaptability_trend']:+.2f}. "
                    f"Tension trend: {trajectory_data['tension_trend']:+.2f}. "
                    f"Confidence: {trajectory_data['confidence']*100:.0f}%. "
                    f"Runaway escalation in progress — voluntary interruption required now."
                )
                score = max(0.0, score - 40)
            
            elif trajectory_data["confidence"] > 0.4:
                flags.append(
                    f"⚠ EARLY RIGIDITY WARNING: Pattern trending toward Yunus trap. "
                    f"Confidence {trajectory_data['confidence']*100:.0f}%. "
                    f"Pattern: {' → '.join(str(s) for s in trajectory_data['pattern'])}."
                )

        # ── RIGIDITY INDEX from state ────────────────────────────────────────
        if state and state.rigidity_index > 0.6:
            score = max(0.0, score - 20)
            flags.append(
                f"Rigidity Index = {state.rigidity_index:.2f}. "
                f"System has been locked in high stages with low adaptability "
                f"for extended period."
            )

        is_trap = trajectory_trap or (stage_8_snapshot_trap and arrogance_hits >= 2)

        # ── RELEASE RECOMMENDATIONS ──────────────────────────────────────────
        release_protocol = []
        if is_trap:
            release_protocol = [
                "Practice gratitude for the current stage's gifts before demanding Stage 9.",
                "Consciously name the duality you are refusing to hold.",
                "Identify what you would need to un-learn to move forward.",
                "Use the Ma'at forgiveness declaration for self-directed rigidity.",
                "Introduce intentional entropy — something you haven't optimized yet.",
            ]

        return {
            "yunus_score": round(score, 1),
            "is_trap": is_trap,
            "trajectory_trap": trajectory_trap,
            "snapshot_trap": stage_8_snapshot_trap,
            "trajectory_data": trajectory_data,
            "flags": flags,
            "release_protocol": release_protocol,
            "safe": score > 70 and not is_trap,
            "arrogance_count": arrogance_hits,
            "counterfactual_count": cf_hits,
        }
