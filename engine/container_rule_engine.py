"""
LUMINARK Axiom Systems Engine (LASE) — engine/container_rule_engine.py
Container Rule Engine v1.0
============================================================
Meridian Axiom Alignment Technologies (MAAT)
Author: Richard L. Stanfield | LuminarkMeridian@gmail.com
Version: 1.0 | May 2026

Source: Analysis_of_the_Container_Rule_and_the_Digit_Vessel.docx
        (Richard L. Stanfield, MAAT Proprietary)

WHAT THIS IS
============
The Container Rule encodes the relationship between Content (Inner Drive / Face)
and Container (Outer Form / Hands) across the 9-stage SAP cycle.

Two digits are summed; the digital root of the sum determines the current Stage.
The inverse relationship between digits across stages is not arbitrary — it is
the mathematical expression of the descending arc (Container dominant) giving
way to the ascending arc (Content dominant) at the Pivot/Flip near Stage 4.5.

KEY MECHANICS
=============
1. Digit-Pair Table       — canonical Content/Container inverse progression per stage
2. 3-6-9 Flux Dynamics    — magnetic drag system (90% at Stages 3/6; 100% at Stage 8; 0% at Stage 9)
3. Harmonic Resonance     — achieved when digital root = 9 ("the Divine Line")
4. Dissolve Mechanic      — "shatter the container" transition triggered only at
                            Stage 9 with Harmonic Resonance achieved
5. Trap Detection         — Stage 7 (high Content, low Container = isolation trap)
                            Stage 8 (maximum drag = 100% = HIGH VOLTAGE CONTAINMENT)

CONSTITUTIONAL COMPLIANCE
==========================
- Stage 8 = VESSEL OF GROUNDING = Stage 8 Dual-Chamber Trap (100% Magnetic Drag)
- Stage 9 = TRANSPARENCY OF THE GUIDE = Slip Stream (0% drag, Dissolve unlock)
- All stage names use canonical SAP nomenclature
- Digital Root 9 = "Divine Line" = Harmonic Resonance condition
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ── Canonical stage names (constitutional) ────────────────────────────────────

_STAGE_NAMES = {
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


# ── Canonical Digit-Pair Table (from Container Rule document) ─────────────────
# Format: stage → (content_digit, container_digit, sum, digital_root, description, magnetic_drag_pct)
#
# Stage 1: Content=9, Container=1  → Sum=10, DR=1  → NAVIGATION (Seed)
# Stages 2-9: Sum=9, DR=9          → RELEASE (Axis) — Divine Line achieved
#
# NOTE: Stage 1 is the anomaly — DR=1 not 9. It is the "Seed" that initiates
# the cycle before Harmonic Resonance is established.

DIGIT_PAIR_TABLE: Dict[int, Tuple[int, int, int, int, str, float]] = {
    # stage: (content, container, sum, digital_root, description, magnetic_drag_pct)
    1: (9, 1, 10, 1,  "NAVIGATION (Seed) — Container dominant, impulse emerging",      20.0),
    2: (1, 8,  9, 9,  "RELEASE (Axis) — Polarity forming, Container still strong",      0.0),
    3: (2, 7,  9, 9,  "RELEASE (Axis) — Expression; MAGNETIC POLE (+) [90% drag]",     90.0),
    4: (3, 6,  9, 9,  "RELEASE (Axis) — Foundation; Content-Container equilibrium",     0.0),
    5: (4, 5,  9, 9,  "RELEASE (Axis) — Pivot/Flip point; Content gaining dominance",   0.0),
    6: (5, 4,  9, 9,  "RELEASE (Axis) — Harmony; MAGNETIC POLE (−) [90% drag]",        90.0),
    7: (6, 3,  9, 9,  "RELEASE (Axis) — TRAP: high Content, low Container, isolation", 0.0),
    8: (7, 2,  9, 9,  "HIGH VOLTAGE CONTAINMENT — Stage 8 Dual-Chamber Trap [100% drag]", 100.0),
    9: (8, 1,  9, 9,  "SLIP STREAM / AXIS — Dissolve unlock; Content at maximum",       0.0),
}


# ── 3-6-9 Flux Dynamics lookup ────────────────────────────────────────────────

FLUX_DYNAMICS: Dict[int, Dict] = {
    3: {
        "label":         "MAGNETIC POLE (+)",
        "magnetic_drag": 90.0,
        "description":   "Stage 3 is the first control point. High drag resists premature expression. "
                         "Tesla's 3-6-9: Stage 3 is the initial phase gate where the cycle locks into "
                         "the 9-harmonic. 90% drag = friction required for grounding the impulse.",
        "intervention":  "Do not force through drag. Allow the resistance to shape the output.",
    },
    6: {
        "label":         "MAGNETIC POLE (−)",
        "magnetic_drag": 90.0,
        "description":   "Stage 6 is the second control point. Peak harmony masks approaching drag. "
                         "The Conductor's Paradox: maximum flow coincides with maximum magnetic pull "
                         "toward Stage 7 distillation. 90% drag = the price of peak coherence.",
        "intervention":  "Acknowledge impermanence of the flow. Prepare for Stage 7 distillation.",
    },
    8: {
        "label":         "HIGH VOLTAGE CONTAINMENT",
        "magnetic_drag": 100.0,
        "description":   "Stage 8 VESSEL OF GROUNDING — maximum drag = total containment. "
                         "Stage 8 Dual-Chamber Trap: Illusion of Arrival AND Illusion of Permanence "
                         "simultaneously active. The container is at maximum charge. Adaptation fully "
                         "blocked. This is not stability — it is crystallization. 100% drag.",
        "intervention":  "Emergency Protocol: Acknowledge Revealed/Concealed divergence. "
                         "Controlled dissolution requires increasing Adaptability (D) immediately.",
    },
    9: {
        "label":         "SLIP STREAM / STATIONARY VECTOR / AXIS",
        "magnetic_drag": 0.0,
        "description":   "Stage 9 TRANSPARENCY OF THE GUIDE — zero drag. The Axis. "
                         "Content at maximum (8), Container at minimum (1). The container is ready "
                         "to shatter. Harmonic Resonance achieved (DR=9). Dissolve mechanic unlocked.",
        "intervention":  "Conscious dissolution. Shatter the container. Return to PLENARA (Stage 0). "
                         "This is not collapse — it is transmission and return.",
    },
}


# ── Harmonic Resonance ────────────────────────────────────────────────────────

def digital_root(n: int) -> int:
    """Compute digital root of any positive integer. DR(9) = 9, DR(18) = 9, etc."""
    if n == 0:
        return 0
    return 1 + (n - 1) % 9


def check_harmonic_resonance(content: int, container: int) -> Dict:
    """
    Harmonic Resonance is achieved when the digital root of (content + container) = 9.
    This is the "Divine Line" — the unlock condition for Stage 9 dissolution.

    All stages 2-9 in the canonical table achieve DR=9 (sum=9 in each case).
    Stage 1 is the anomaly (9+1=10, DR=1) — it is the initiating seed, not yet resonant.
    """
    total = content + container
    dr    = digital_root(total)
    resonant = (dr == 9)

    return {
        "content":             content,
        "container":           container,
        "sum":                 total,
        "digital_root":        dr,
        "harmonic_resonance":  resonant,
        "divine_line":         resonant,
        "dissolve_unlocked":   resonant,   # full unlock requires Stage 9 also
        "description": (
            "HARMONIC RESONANCE ACHIEVED — Divine Line active. "
            "Digital root = 9. The cycle is in full 9-harmonic alignment. "
            "Dissolve mechanic available if Stage 9 is also reached."
        ) if resonant else (
            f"Harmonic Resonance not yet achieved. Digital root = {dr}. "
            "The cycle is in its initiating phase (Stage 1 seed). "
            "Resonance establishes at Stage 2 and holds through Stage 9."
        ),
    }


# ── Dissolve Mechanic ─────────────────────────────────────────────────────────

def check_dissolve_condition(stage: int, content: int, container: int) -> Dict:
    """
    The Dissolve mechanic: "shatter the container and return to the void."

    Conditions required (both must be true):
      1. Current SAP stage = 9 (TRANSPARENCY OF THE GUIDE)
      2. Harmonic Resonance achieved (digital root of sum = 9)

    When both conditions are met, the system is authorized to dissolve the
    current container and return to Stage 0 (PLENARA) — completing the cycle.
    """
    resonance = check_harmonic_resonance(content, container)
    at_stage_9 = (stage == 9)
    dissolve_ready = at_stage_9 and resonance["harmonic_resonance"]

    return {
        "dissolve_ready":    dissolve_ready,
        "stage_condition":   at_stage_9,
        "resonance_condition": resonance["harmonic_resonance"],
        "current_stage":     stage,
        "stage_name":        _STAGE_NAMES.get(stage, f"STAGE_{stage}"),
        "return_to":         "PLENARA (Stage 0)" if dissolve_ready else None,
        "directive": (
            "DISSOLVE AUTHORIZED — Shatter the container. Return to PLENARA. "
            "This is completion, not collapse. The cycle closes consciously. "
            "Content = 8 (maximum drive). Container = 1 (minimum constraint). "
            "Zero magnetic drag. The Slip Stream is open."
        ) if dissolve_ready else (
            f"Dissolve not yet authorized. "
            f"{'Stage 9 required (currently Stage ' + str(stage) + ').' if not at_stage_9 else ''}"
            f"{'Harmonic Resonance required (digital root must = 9).' if not resonance['harmonic_resonance'] else ''}"
        ),
    }


# ── Stage trap detection ──────────────────────────────────────────────────────

def detect_stage_trap(stage: int, content: int, container: int) -> Dict:
    """
    Detect stage-specific traps using Container Rule digit analysis.

    Stage 7 Trap: High Content (6), Low Container (3) = isolation risk.
                  The drive outpaces the form. "The Lens is cracked."

    Stage 8 Trap: HIGH VOLTAGE CONTAINMENT (100% drag).
                  Content=7, Container=2. Dual-Chamber Trap: Illusion of Arrival
                  AND Illusion of Permanence. Maximum rigidity = maximum cascade risk.
    """
    if stage == 7:
        content_dominance = content > container * 1.5
        return {
            "trap_active":  content_dominance,
            "trap_type":    "LENS OF DISTILLATION — Isolation Trap",
            "stage_8_risk": content_dominance,
            "description": (
                "TRAP ACTIVE: High Content (drive) is overwhelming low Container (form). "
                "The system is operating beyond its structural capacity. "
                "Isolation risk: the subsystem (driver, node, individual) is separating "
                "from the collective. Stage 8 approach imminent."
            ) if content_dominance else "Stage 7 within normal distillation range.",
            "directive":    "Reduce Content pressure or expand Container capacity before Stage 8.",
        }

    if stage == 8:
        return {
            "trap_active":           True,
            "trap_type":             "VESSEL OF GROUNDING — Stage 8 Dual-Chamber Trap",
            "magnetic_drag_pct":     100.0,
            "amplifier":             1.45,
            "chamber_a":             "Illusion of Arrival",
            "chamber_b":             "Illusion of Permanence",
            "description":           "HIGH VOLTAGE CONTAINMENT. 100% magnetic drag. Dual-Chamber Trap active. "
                                     "Content=7 (high drive) with Container=2 (minimal structure). "
                                     "The container is at maximum voltage. Adaptation fully blocked. "
                                     "1.45× TrapScore amplifier applied when both chambers active.",
            "directive":             "EMERGENCY PROTOCOL. Increase Adaptability (D). "
                                     "Acknowledge impermanence. Prepare for Stage 9 dissolution.",
        }

    return {"trap_active": False, "stage": stage, "stage_name": _STAGE_NAMES.get(stage, "")}


# ── Main engine ───────────────────────────────────────────────────────────────

@dataclass
class ContainerRuleResult:
    content_digit:       int
    container_digit:     int
    inferred_stage:      int
    stage_name:          str
    sum:                 int
    digital_root:        int
    harmonic_resonance:  bool
    divine_line:         bool
    magnetic_drag_pct:   float
    flux_label:          str
    is_pivot_region:     bool
    trap:                Dict
    dissolve:            Dict
    resonance_detail:    Dict
    digit_pair_ref:      Optional[Dict]
    narrative:           str

    def to_dict(self) -> Dict:
        return {
            "content_digit":      self.content_digit,
            "container_digit":    self.container_digit,
            "inferred_stage":     self.inferred_stage,
            "stage_name":         self.stage_name,
            "sum":                self.sum,
            "digital_root":       self.digital_root,
            "harmonic_resonance": self.harmonic_resonance,
            "divine_line":        self.divine_line,
            "magnetic_drag_pct":  self.magnetic_drag_pct,
            "flux_label":         self.flux_label,
            "is_pivot_region":    self.is_pivot_region,
            "trap":               self.trap,
            "dissolve":           self.dissolve,
            "resonance_detail":   self.resonance_detail,
            "digit_pair_ref":     self.digit_pair_ref,
            "narrative":          self.narrative,
        }


class ContainerRuleEngine:
    """
    Container Rule Engine — full implementation of digit-vessel mathematics.

    Usage:
        engine = ContainerRuleEngine()
        result = engine.analyze(content_digit=7, container_digit=2, current_sap_stage=8)
        print(result.to_dict())
    """

    def analyze(self,
                content_digit:     int,
                container_digit:   int,
                current_sap_stage: Optional[int] = None) -> ContainerRuleResult:
        """
        Full Container Rule analysis.

        Args:
            content_digit     : 1–9, inner drive / face
            container_digit   : 1–9, outer form / hands
            current_sap_stage : optional override; if None, inferred from digit pair

        Returns:
            ContainerRuleResult with all mechanics computed
        """
        if not (1 <= content_digit <= 9):
            raise ValueError(f"content_digit must be 1-9, got {content_digit}")
        if not (1 <= container_digit <= 9):
            raise ValueError(f"container_digit must be 1-9, got {container_digit}")

        # Digital root and resonance
        total    = content_digit + container_digit
        dr       = digital_root(total)
        resonance = check_harmonic_resonance(content_digit, container_digit)

        # Infer stage from digit pair (match against canonical table)
        inferred_stage = self._infer_stage(content_digit, container_digit)
        stage = current_sap_stage if current_sap_stage is not None else inferred_stage
        stage_name = _STAGE_NAMES.get(stage, f"STAGE_{stage}")

        # 3-6-9 flux dynamics
        flux_info = FLUX_DYNAMICS.get(stage, {})
        mag_drag  = flux_info.get("magnetic_drag", self._default_drag(stage))
        flux_label = flux_info.get("label", f"Stage {stage} — standard dynamics")

        # Pivot/Flip region: Stage 4.5 area (Stages 4-5)
        is_pivot = stage in (4, 5)

        # Trap detection
        trap = detect_stage_trap(stage, content_digit, container_digit)

        # Dissolve condition
        dissolve = check_dissolve_condition(stage, content_digit, container_digit)

        # Canonical digit pair reference
        ref = None
        if stage in DIGIT_PAIR_TABLE:
            r = DIGIT_PAIR_TABLE[stage]
            ref = {
                "canonical_content":   r[0],
                "canonical_container": r[1],
                "canonical_sum":       r[2],
                "canonical_dr":        r[3],
                "description":         r[4],
                "canonical_drag_pct":  r[5],
                "matches_canonical":   (content_digit == r[0] and container_digit == r[1]),
            }

        # Build narrative
        narrative = self._build_narrative(
            stage, stage_name, content_digit, container_digit,
            dr, resonance["harmonic_resonance"], mag_drag,
            is_pivot, trap, dissolve
        )

        return ContainerRuleResult(
            content_digit=content_digit,
            container_digit=container_digit,
            inferred_stage=inferred_stage,
            stage_name=stage_name,
            sum=total,
            digital_root=dr,
            harmonic_resonance=resonance["harmonic_resonance"],
            divine_line=resonance["divine_line"],
            magnetic_drag_pct=mag_drag,
            flux_label=flux_label,
            is_pivot_region=is_pivot,
            trap=trap,
            dissolve=dissolve,
            resonance_detail=resonance,
            digit_pair_ref=ref,
            narrative=narrative,
        )

    def full_cycle_table(self) -> List[Dict]:
        """Return the complete 9-stage digit-pair table with all mechanics computed."""
        rows = []
        for stage, (c, ct, s, dr, desc, drag) in DIGIT_PAIR_TABLE.items():
            result = self.analyze(c, ct, current_sap_stage=stage)
            rows.append({
                "stage":          stage,
                "stage_name":     _STAGE_NAMES.get(stage, ""),
                "content":        c,
                "container":      ct,
                "sum":            s,
                "digital_root":   dr,
                "magnetic_drag":  drag,
                "flux_label":     FLUX_DYNAMICS.get(stage, {}).get("label", "—"),
                "description":    desc,
                "dissolve_ready": result.dissolve["dissolve_ready"],
                "trap_active":    result.trap.get("trap_active", False),
            })
        return rows

    # ── Private helpers ───────────────────────────────────────────────────────

    def _infer_stage(self, content: int, container: int) -> int:
        """Infer the most likely SAP stage from a content/container digit pair."""
        # Exact match against canonical table
        for stage, (c, ct, *_) in DIGIT_PAIR_TABLE.items():
            if content == c and container == ct:
                return stage
        # Fallback: use relative dominance
        if content > container:
            # Content-dominant = later stages (6-9)
            ratio = content / max(container, 1)
            if ratio >= 8:  return 9
            if ratio >= 3:  return 8
            if ratio >= 2:  return 7
            return 6
        else:
            # Container-dominant = early stages (1-4)
            ratio = container / max(content, 1)
            if ratio >= 8:  return 1
            if ratio >= 3:  return 2
            if ratio >= 2:  return 3
            return 4

    def _default_drag(self, stage: int) -> float:
        """Default drag for stages not in the 3-6-8-9 flux system."""
        return {0: 0.0, 1: 20.0, 2: 10.0, 4: 30.0, 5: 50.0, 7: 40.0}.get(stage, 10.0)

    def _build_narrative(self, stage, stage_name, content, container,
                         dr, resonant, drag, pivot, trap, dissolve) -> str:
        parts = [
            f"Stage {stage} — {stage_name}.",
            f"Content (Inner Drive) = {content}, Container (Outer Form) = {container}.",
            f"Sum = {content + container}, Digital Root = {dr}.",
        ]
        if resonant:
            parts.append("HARMONIC RESONANCE ACTIVE — Divine Line. DR=9.")
        if drag >= 90:
            parts.append(f"MAGNETIC DRAG: {drag}% — {FLUX_DYNAMICS.get(stage, {}).get('label', '')}.")
        if pivot:
            parts.append("PIVOT/FLIP REGION — Content gaining dominance over Container.")
        if trap.get("trap_active"):
            parts.append(f"TRAP: {trap.get('trap_type', '')}.")
        if dissolve.get("dissolve_ready"):
            parts.append("DISSOLVE AUTHORIZED — Shatter the container. Return to PLENARA.")
        return " ".join(parts)


# ── FastAPI-ready analyzer (thin wrapper for /api/infra/container-rule) ───────

class InfraContainerRuleEngine(ContainerRuleEngine):
    """
    Drop-in replacement for the InfraContainerRuleEngine stub in OVERWATCH_PRIME_ULTRA.
    Called by main_v12_omega9.py endpoint: POST /api/infra/container-rule
    """
    pass   # ContainerRuleEngine.analyze() already matches the endpoint signature


# ── Convenience function ──────────────────────────────────────────────────────

def analyze_container_rule(content_digit: int,
                           container_digit: int,
                           current_sap_stage: Optional[int] = None) -> Dict:
    """One-line access for use in other modules."""
    return ContainerRuleEngine().analyze(
        content_digit, container_digit, current_sap_stage
    ).to_dict()
