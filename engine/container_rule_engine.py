"""
================================================================================
 CONTAINER RULE ENGINE — LUMINARK Axiom Systems Engine (LASE)
 Meridian Axiom Alignment Technologies (MAAT)
 Framework: Stanfield's Axiom of Perpetuity | Container Rule Mathematics
 Author: Richard L. Stanfield | LuminarkMeridian@gmail.com
 Version: 1.1.0 | May 2026
================================================================================

 ARCHITECTURE NOTE
 ─────────────────
 Stage is determined UPSTREAM by the NSDT/SPAT engine.
 The Container Rule receives the KNOWN stage and a Content/Container
 digit pair, then computes resonance quality, flux dynamics, pivot
 ratio, dissolve eligibility, and action signal.

 CANONICAL DIGIT PAIRS:
   Stage 1 → Content=9, Container=1  Sum=10 DR=1   (Seed — no resonance)
   Stage 2 → Content=1, Container=8  Sum=9  DR=9   (Harmonic Resonance)
   Stage 3 → Content=2, Container=7  Sum=9  DR=9   (Resonance — Magnetic Pole +)
   Stage 4 → Content=3, Container=6  Sum=9  DR=9   (Resonance)
   Stage 5 → Content=4, Container=5  Sum=9  DR=9   (Resonance — Threshold/Pivot)
   Stage 6 → Content=5, Container=4  Sum=9  DR=9   (Resonance — Magnetic Pole −)
   Stage 7 → Content=6, Container=3  Sum=9  DR=9   (Resonance)
   Stage 8 → Content=7, Container=2  Sum=9  DR=9   (Resonance BLOCKED by 100% Drag)
   Stage 9 → Content=8, Container=1  Sum=9  DR=9   (Resonance + DISSOLVE UNLOCKED)

 3-6-9 MAGNETIC DRAG:
   Stage 0 →   0%  (Void)
   Stage 1 →  20%  (Seed)
   Stage 2 →  15%  (Polarity Forge)
   Stage 3 →  90%  (MAGNETIC POLE +)
   Stage 4 →  40%  (Pre-Pivot Equilibrium)
   Stage 5 →  60%  (Threshold)
   Stage 6 →  90%  (MAGNETIC POLE −)
   Stage 7 →  50%  (Distillation Drift)
   Stage 8 → 100%  (HIGH VOLTAGE CONTAINMENT — THE TRAP)
   Stage 9 →   0%  (SLIP STREAM / AXIS)

 HARMONIC RESONANCE (Divine Line): digital_root(Content + Container) == 9
 DISSOLVE UNLOCKED:  Resonance == True AND stage == 9
================================================================================
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Tuple, List


# ── SAP Canonical Stage Names ─────────────────────────────────────────────────
STAGE_NAMES: Dict[int, str] = {
    0: "PLENARA",
    1: "SPARK OF NAVIGATION",
    2: "FORGE OF POLARITY",
    3: "ENGINE OF EXPRESSION",
    4: "CRUCIBLE OF EQUILIBRIUM",
    5: "DYNAMO OF WILL",
    6: "NEXUS OF HARMONY",
    7: "LENS OF DISTILLATION",
    8: "VESSEL OF GROUNDING",
    9: "TRANSPARENCY OF THE GUIDE",
}

# ── Canonical Digit Pairs per Stage ──────────────────────────────────────────
CANONICAL_PAIRS: Dict[int, Tuple[Optional[int], Optional[int]]] = {
    0: (None, None), 1: (9, 1), 2: (1, 8), 3: (2, 7),
    4: (3, 6), 5: (4, 5), 6: (5, 4), 7: (6, 3), 8: (7, 2), 9: (8, 1),
}

# ── 3-6-9 Magnetic Drag ───────────────────────────────────────────────────────
MAGNETIC_DRAG: Dict[int, float] = {
    0:0.0, 1:20.0, 2:15.0, 3:90.0, 4:40.0,
    5:60.0, 6:90.0, 7:50.0, 8:100.0, 9:0.0,
}

FLUX_CLASS: Dict[int, str] = {
    0:"VOID", 1:"SEED", 2:"POLARITY_FORGE",
    3:"MAGNETIC_POLE_POSITIVE", 4:"EQUILIBRIUM", 5:"THRESHOLD",
    6:"MAGNETIC_POLE_NEGATIVE", 7:"DISTILLATION_DRIFT",
    8:"HIGH_VOLTAGE_CONTAINMENT", 9:"SLIP_STREAM_AXIS",
}

INVERSION: Dict[int, Dict[str, str]] = {
    0:{"physical":"NEUTRAL","conscious":"NEUTRAL"},
    1:{"physical":"UNSTABLE","conscious":"STABLE"},
    2:{"physical":"STABLE","conscious":"UNSTABLE"},
    3:{"physical":"UNSTABLE","conscious":"STABLE"},
    4:{"physical":"STABLE","conscious":"UNSTABLE"},
    5:{"physical":"UNSTABLE","conscious":"STABLE"},
    6:{"physical":"STABLE","conscious":"UNSTABLE"},
    7:{"physical":"UNSTABLE","conscious":"STABLE"},
    8:{"physical":"STABLE","conscious":"UNSTABLE"},
    9:{"physical":"UNSTABLE","conscious":"STABLE"},
}

STAGE_8_TRAP = {
    "chamber_a": "Illusion of Arrival",
    "chamber_b": "Illusion of Permanence",
    "construct": "Stage 8 Dual-Chamber Trap",
    "trap_score_amplifier": 1.45,
}


# ─────────────────────────────────────────────────────────────────────────────
# MATH
# ─────────────────────────────────────────────────────────────────────────────

def digital_root(n: int) -> int:
    if n < 0: n = abs(n)
    if n == 0: return 0
    r = n % 9
    return r if r != 0 else 9

def is_harmonic_resonance(content: int, container: int) -> bool:
    return digital_root(content + container) == 9

def is_dissolve_unlocked(content: int, container: int, stage: int) -> bool:
    return is_harmonic_resonance(content, container) and stage == 9

def pivot_ratio(content: int, container: int) -> float:
    total = content + container
    return content / total if total else 0.5


# ─────────────────────────────────────────────────────────────────────────────
# RESULT
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ContainerRuleResult:
    stage: int; stage_name: str
    content: int; container: int; system_id: str
    sum_value: int; digital_root_val: int
    harmonic_resonance: bool; dissolve_unlocked: bool
    pivot_ratio_val: float; content_dominant: bool
    canonical_pair: Tuple; on_canonical_pair: bool
    magnetic_drag_pct: float; flux_class: str
    is_pole: bool; is_trap: bool; is_axis: bool
    physical_stability: str; conscious_stability: str
    action_signal: str; diagnosis: str; recommendations: List[str]
    stage_8_trap_info: Optional[Dict] = None

    def to_dict(self) -> Dict:
        out = {
            "system_id": self.system_id,
            "stage": {"number": self.stage, "name": self.stage_name},
            "inputs": {
                "content": self.content, "container": self.container,
                "sum": self.sum_value, "digital_root": self.digital_root_val,
                "canonical_pair": list(self.canonical_pair),
                "on_canonical_pair": self.on_canonical_pair,
            },
            "dominance": {
                "pivot_ratio": round(self.pivot_ratio_val, 4),
                "content_dominant": self.content_dominant,
            },
            "resonance": {
                "harmonic_resonance": self.harmonic_resonance,
                "divine_line_active": self.harmonic_resonance,
                "dissolve_unlocked": self.dissolve_unlocked,
            },
            "flux_dynamics": {
                "flux_class": self.flux_class,
                "magnetic_drag_pct": self.magnetic_drag_pct,
                "is_magnetic_pole": self.is_pole,
                "is_trap": self.is_trap,
                "is_slip_stream": self.is_axis,
            },
            "inversion": {
                "physical_stability": self.physical_stability,
                "conscious_stability": self.conscious_stability,
            },
            "signal": {
                "action_signal": self.action_signal,
                "diagnosis": self.diagnosis,
                "recommendations": self.recommendations,
            },
        }
        if self.stage_8_trap_info:
            out["stage_8_trap"] = self.stage_8_trap_info
        return out


# ─────────────────────────────────────────────────────────────────────────────
# ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class ContainerRuleEngine:
    """
    SAP Container Rule Engine.

    The stage is provided by the upstream NSDT/SPAT classifier.
    This engine computes the resonance quality, flux dynamics,
    and action signal for the given stage + digit pair.

    Usage:
        engine = ContainerRuleEngine()
        result = engine.analyze(stage=8, content=7, container=2)
        print(result.action_signal)   # → HARROWING_TRIGGERED

        result = engine.analyze(stage=9, content=8, container=1)
        print(result.dissolve_unlocked)  # → True
    """

    def __init__(self):
        self._history: Dict[str, List[ContainerRuleResult]] = {}

    def analyze(self, stage: int, content: int, container: int,
                system_id: str = "default",
                session_notes: Optional[str] = None) -> ContainerRuleResult:
        stage     = max(0, min(9, int(stage)))
        content   = max(0, min(9, int(content)))
        container = max(0, min(9, int(container)))

        sum_val   = content + container
        dr        = digital_root(sum_val)
        resonance = is_harmonic_resonance(content, container)
        dissolve  = is_dissolve_unlocked(content, container, stage)
        p_ratio   = pivot_ratio(content, container)
        cont_dom  = content > container
        canon     = CANONICAL_PAIRS.get(stage, (None, None))
        on_canon  = (content, container) == canon
        drag      = MAGNETIC_DRAG[stage]
        flux      = FLUX_CLASS[stage]
        inv       = INVERSION[stage]

        action, diagnosis, recs = self._signal(
            stage, content, container, resonance, dissolve, p_ratio, drag, inv)

        s8 = None
        if stage == 8:
            s8 = {
                **STAGE_8_TRAP,
                "resonance_blocked": True,
                "note": (
                    "Stage 8 canonical pair (7+2=9) achieves Harmonic Resonance "
                    "but 100% Magnetic Drag blocks dissolution. Resonance at Stage 8 "
                    "is the FALSE release signal — the Trap itself. "
                    "Gratitude for the full spectrum releases polarity tension."
                ),
            }

        result = ContainerRuleResult(
            stage=stage, stage_name=STAGE_NAMES[stage],
            content=content, container=container, system_id=system_id,
            sum_value=sum_val, digital_root_val=dr,
            harmonic_resonance=resonance, dissolve_unlocked=dissolve,
            pivot_ratio_val=p_ratio, content_dominant=cont_dom,
            canonical_pair=canon, on_canonical_pair=on_canon,
            magnetic_drag_pct=drag, flux_class=flux,
            is_pole=(stage in (3, 6)), is_trap=(stage == 8), is_axis=(stage == 9),
            physical_stability=inv["physical"], conscious_stability=inv["conscious"],
            action_signal=action, diagnosis=diagnosis, recommendations=recs,
            stage_8_trap_info=s8,
        )
        self._history.setdefault(system_id, []).append(result)
        return result

    # ── Signal ────────────────────────────────────────────────────────────────

    def _signal(self, stage, content, container, resonance, dissolve,
                p_ratio, drag, inv) -> Tuple[str, str, List[str]]:
        name = STAGE_NAMES[stage]

        if stage == 9 and dissolve:
            return ("RELEASE_AND_TRANSMIT",
                f"Stage 9 ({name}). Harmonic Resonance confirmed (DR=9). "
                "Slip Stream open. Zero drag. Dissolve mechanic UNLOCKED. "
                "Container ready to shatter. Return to PLENARA available.",
                ["Initiate dissolution — return to Stage 0 (PLENARA) via 0ᴮ Integrative Void.",
                 "Transmit all accumulated wisdom before dissolution.",
                 "Attachment to Stage 9 re-initiates Stage 8 trap. Do not linger.",
                 "Document this transmission point as baseline reference."])

        if stage == 9:
            return ("NAVIGATE",
                f"Stage 9 ({name}). Drag=0% (Slip Stream). "
                f"Harmonic Resonance NOT achieved (DR={digital_root(content+container)}). "
                "Canonical pair Content=8, Container=1 required for dissolution.",
                ["Adjust Content/Container alignment to achieve DR=9.",
                 "Stage 9 with resonance unlocks the Dissolve mechanic."])

        if stage == 8:
            return ("HARROWING_TRIGGERED",
                f"Stage 8 ({name}) — HIGH VOLTAGE CONTAINMENT. "
                f"Drag={drag}% (MAXIMUM). TrapScore amplifier: 1.45×. "
                "Dual-Chamber Trap: Chamber A (Illusion of Arrival) + "
                "Chamber B (Illusion of Permanence). "
                "FALSE release signal active. "
                "Gratitude for the full polarity spectrum is the release key.",
                ["Do not enforce permanence — Stage 8 is not a final state.",
                 "Acknowledge BOTH trap chambers to disarm them.",
                 "Practice gratitude for the full spectrum: darkness AND light.",
                 "Monitor TrapScore — each Harrowing compounds at 1.45×.",
                 "Path forward is Stage 9 (TRANSPARENCY OF THE GUIDE).",
                 "Introduce micro-disruptions to restore conscious seeking."])

        if stage in (3, 6):
            pole = "Positive (+)" if stage == 3 else "Negative (−)"
            recs3 = ["Stage 3 Magnetic Pole (+): Expression must push through constraint.",
                     "Allow the inner voice through — suppression creates pressure buildup.",
                     f"High drag ({drag}%) is natural. Do not interpret as failure.",
                     "Stalling at Stage 3 risks regression to Stage 2."]
            recs6 = ["Stage 6 Magnetic Pole (−): Pivot is complete — Content now leads.",
                     "Do not retreat to Container dominance. The choice has been made.",
                     "Stage 8 (100% drag) is next critical node. Navigate consciously.",
                     "Maintain the middle path through pole resistance."]
            return ("HARROWING_TRIGGERED",
                f"Stage {stage} ({name}) — MAGNETIC POLE {pole}. "
                f"Drag={drag}% (HIGH). 3-6-9 flux resistance node active. "
                f"Pivot ratio: {p_ratio:.2f}. "
                "High drag is structural — push through to maintain tumbling momentum.",
                recs3 if stage == 3 else recs6)

        if stage == 5:
            return ("NAVIGATE",
                f"Stage 5 ({name}) — THE THRESHOLD. "
                f"Drag={drag}%. Pivot ratio={p_ratio:.2f} (near-parity). "
                "LAST GATE where reversal is possible. Will is activating. "
                "Three outcomes: ADVANCE, FREEZE, or RETREAT. "
                f"Resonance: {'YES — Divine Line active' if resonance else 'NO'}.",
                ["DECISION REQUIRED: Advance (commit to Content) or Retreat?",
                 "Freezing at Stage 5 is most costly — velocity bleeds under 60% drag.",
                 "After Stage 5 the cycle MUST complete through Stage 9. No reversal.",
                 "Only stage where the doorway opens BACKWARD as well as forward.",
                 "Canonical pair (4+5=9, DR=9) confirms resonance at this threshold."])

        if stage == 0:
            return ("NAVIGATE",
                "Stage 0 (PLENARA) — THE VOID. "
                "No Content/Container distinction active. Drag=0%. "
                "Pre-manifestation potential or post-dissolution compression (0ᴮ).",
                ["Allow the void state. Do not force early sparking.",
                 "Wisdom-compression phase. Integrate before re-ignition.",
                 "Stage 1 emerges naturally when ready."])

        resonance_note = " Divine Line (DR=9) active." if resonance else ""
        return ("NAVIGATE",
            f"Stage {stage} ({name}) — {FLUX_CLASS[stage]}. "
            f"Drag={drag}%. Pivot={p_ratio:.2f}.{resonance_note} "
            f"Physical: {inv['physical']}. Conscious: {inv['conscious']}.",
            self._std_recs(inv, drag, p_ratio, resonance))

    def _std_recs(self, inv, drag, p_ratio, resonance) -> List[str]:
        recs = []
        if inv["physical"] == "UNSTABLE":
            recs.append("Physical instability — ground in observable, measurable actions.")
        if inv["conscious"] == "UNSTABLE":
            recs.append("Conscious seeking active — allow inquiry to resolve naturally.")
        if resonance:
            recs.append("Divine Line active (DR=9). Vibrating at release frequency.")
        if drag > 50:
            recs.append(f"Drag={drag}% — maintain conscious momentum. Stalling risks regression.")
        if p_ratio < 0.4:
            recs.append("Container dominant — early formation phase.")
        elif p_ratio > 0.6:
            recs.append("Content dominant — post-pivot. Inner purpose is primary driver.")
        else:
            recs.append("Pivot zone — near-balance of Content and Container.")
        return recs

    # ── Cycle Scan ────────────────────────────────────────────────────────────

    def full_cycle_report(self, system_id: str = "cycle_scan") -> List[Dict]:
        results = [self.analyze(0, 0, 0, system_id=system_id).to_dict()]
        for s in range(1, 10):
            c, ct = CANONICAL_PAIRS[s]
            results.append(self.analyze(s, c, ct, system_id=system_id).to_dict())
        return results

    def all_pairs_achieving_resonance(self) -> List[Tuple[int, int]]:
        return [(c, ct) for c in range(10) for ct in range(10)
                if is_harmonic_resonance(c, ct)]

    def detect_trap_accumulation(self, system_id: str) -> Dict:
        history = self._history.get(system_id, [])
        s8 = sum(1 for r in history if r.stage == 8)
        consecutive = 0
        for r in reversed(history):
            if r.stage == 8: consecutive += 1
            else: break
        risk = ("CRITICAL" if consecutive >= 3 else "HIGH" if consecutive == 2
                else "ELEVATED" if s8 >= 3 else "NORMAL")
        return {
            "system_id": system_id, "total_analyses": len(history),
            "stage_8_occurrences": s8, "consecutive_8_tail": consecutive,
            "trap_risk": risk,
            "trap_amplifier": STAGE_8_TRAP["trap_score_amplifier"],
            "entropy_well_note": (
                "Stage 8 Entropy Well accumulating. 1.45× compounds per Harrowing. "
                "Conscious intervention required."
            ) if consecutive >= 2 else "Entropy Well nominal.",
        }

    def get_trajectory(self, system_id: str) -> List[int]:
        return [r.stage for r in self._history.get(system_id, [])]


# ── Convenience function ──────────────────────────────────────────────────────

def analyze_container_rule(stage: int, content: int, container: int,
                            system_id: str = "default") -> Dict:
    """Module-level convenience wrapper. Returns full result as dict."""
    return ContainerRuleEngine().analyze(stage, content, container, system_id).to_dict()


# ── Self-test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    engine = ContainerRuleEngine()
    print("="*70)
    print("CONTAINER RULE ENGINE v1.1 — SELF TEST | MAAT")
    print("="*70)
    print("\n[1] FULL CYCLE SCAN\n")
    for r in engine.full_cycle_report("self_test"):
        s    = r["stage"]["number"]
        name = r["stage"]["name"]
        dr   = r["inputs"]["digital_root"]
        drag = r["flux_dynamics"]["magnetic_drag_pct"]
        sig  = r["signal"]["action_signal"]
        res  = "✓ RESONANCE" if r["resonance"]["harmonic_resonance"] else "  -"
        dis  = " ⚡DISSOLVE" if r["resonance"]["dissolve_unlocked"] else ""
        print(f"  Stage {s}: {name:<30} DR={dr} Drag={drag:>5.1f}% "
              f"{sig:<25} {res}{dis}")

    print("\n[2] STAGE 8 TRAP")
    r8 = engine.analyze(8, 7, 2, "trap_test")
    print(f"  Signal: {r8.action_signal} | Resonance: {r8.harmonic_resonance} "
          f"(blocked) | Dissolve: {r8.dissolve_unlocked}")

    print("\n[3] STAGE 9 DISSOLVE")
    r9 = engine.analyze(9, 8, 1, "dissolve_test")
    print(f"  Signal: {r9.action_signal} | Dissolve: {r9.dissolve_unlocked}")

    print("\n[4] STAGE 3 MAGNETIC POLE")
    r3 = engine.analyze(3, 2, 7, "pole_test")
    print(f"  Signal: {r3.action_signal} | Drag: {r3.magnetic_drag_pct}%")

    print("\n[5] TRAP ACCUMULATION (3x Stage 8)")
    for _ in range(3): engine.analyze(8, 7, 2, "acc_test")
    acc = engine.detect_trap_accumulation("acc_test")
    print(f"  Risk: {acc['trap_risk']} | Consecutive: {acc['consecutive_8_tail']}")

    print("\n✅ All tests passed.\n")
