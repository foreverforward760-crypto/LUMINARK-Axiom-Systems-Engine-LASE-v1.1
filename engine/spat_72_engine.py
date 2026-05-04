"""
LUMINARK Axiom Systems Engine (LASE) — engine/spat_72_engine.py
72-Stage Personal Assessment Tool (72-SPAT) — Diagnostic Engine v1.0
============================================================
Meridian Axiom Alignment Technologies (MAAT)
Author: Richard L. Stanfield | LuminarkMeridian@gmail.com
Version: 1.0 | May 2026

Source: 72_SPAT.docx (Richard L. Stanfield, MAAT Proprietary)

WHAT THIS IS
============
The 72-SPAT maps individuals, organizations, or systems across 8 nested
cycles × 9 stages = 72 canonical positions. It provides higher resolution
than the 9-stage macro model while remaining operationally navigable.

MATHEMATICAL FOUNDATION
=======================
  72 = 8 × 9 (trap × renewal — the two critical stages)
  72 ÷ 9 = 8  (eight complete 9-stage cycles)
  Digital root of 72: 7+2=9 (eternal return/completion)

TRAP STAGES (every 8th stage, starting at 8):
  8, 17, 26, 35, 44, 53, 62, 71
  → High stability + low adaptability = permanence illusion

THRESHOLD STAGES (every stage mod 9 = 5, starting at 5):
  5, 14, 23, 32, 41, 50, 59, 68
  → Bilateral threshold: progress / graceful regression / crisis

RENEWAL STAGES (every stage mod 9 = 0, after stage 0):
  9, 18, 27, 36, 45, 54, 63
  → Intentional dissolution — chaos precedes rebirth

THE 8 CYCLES
============
  Cycle 1 (0-8):   Primordial Emergence
  Cycle 2 (9-17):  Biological Consciousness
  Cycle 3 (18-26): Civilizational Emergence
  Cycle 4 (27-35): Knowledge Systems
  Cycle 5 (36-44): Colonial/Extraction (historical analysis)
  Cycle 6 (45-53): Personal Consciousness (lifespan)
  Cycle 7 (54-62): Technological Consciousness
  Cycle 8 (63-71): Cosmic Return

5 CRITERIA (all 0-10)
=====================
  Complexity (N):   Interdependence of variables in current life/system
  Stability (S):    Consistency of current patterns
  Tension (T):      Degree of internal/external pressure
  Adaptability (D): Flexibility in response to change
  Coherence (C):    Internal alignment and sense of purpose

CONSTITUTIONAL NOTE
===================
The 72-SPAT is an extension of the canonical SAP 9-stage framework.
All 9-stage constitutional directives (stage names, deprecated terms,
Stage 8 dual-chamber naming) apply to this module equally.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any


# ── 72-Stage canonical table ──────────────────────────────────────────────────
# Format: stage → (cycle, cycle_name, stage_label, harmonic_hz, is_trap, is_threshold, is_renewal)

_CYCLE_NAMES = {
    1: "Primordial Emergence",
    2: "Biological Consciousness",
    3: "Civilizational Emergence",
    4: "Knowledge Systems",
    5: "Colonial/Extraction",
    6: "Personal Consciousness",
    7: "Technological Consciousness",
    8: "Cosmic Return",
}

_SOLFEGGIO = [174, 285, 396, 417, 528, 639, 741, 852, 963]

_STAGE_LABELS: Dict[int, str] = {
    # Cycle 1
    0:  "Absolute Plenara (Undifferentiated Void)",
    1:  "Quantum Fluctuation (First Tremor)",
    2:  "Vibrational Coherence (Pattern Formation)",
    3:  "Conscious Separation (The First 'No')",
    4:  "Material Foundation (Density Locks)",
    5:  "Primordial Choice (First Bilateral Threshold)",
    6:  "Life Emergence (Biological Integration)",
    7:  "Complexity Mastery (Ecosystem Formation)",
    8:  "Permanence Illusion (The First Trap)",
    # Cycle 2
    9:  "Extinction/Reset (Return to Potential)",
    10: "Mammalian Dawn (New Template)",
    11: "Social Bonding (Pack Formation)",
    12: "Tool Recognition (Hand-Mind Link)",
    13: "Fire Mastery (Energy Control)",
    14: "Symbolic Threshold (Language Birth)",
    15: "Mythic Integration (Story Consciousness)",
    16: "Ritual Mastery (Pattern Control)",
    17: "Religious Permanence (Doctrinal Trap)",
    # Cycle 3
    18: "Agricultural Revolution (Settled Reset)",
    19: "Village Formation (Community Root)",
    20: "Craft Development (Skill Coherence)",
    21: "Trade Networks (Connection Spark)",
    22: "Writing Systems (Memory Foundation)",
    23: "Urban Threshold (City-State Choice)",
    24: "Empire Integration (Multi-ethnic Harmony)",
    25: "Classical Peak (Cultural Mastery)",
    26: "Imperial Permanence (Rome Forever Trap)",
    # Cycle 4
    27: "Dark Ages Release (Knowledge Diaspora)",
    28: "Monastic Preservation (Hidden Root)",
    29: "Islamic Golden Age (Translation Movement)",
    30: "Renaissance Spark (Rediscovery)",
    31: "Scientific Method (Empirical Foundation)",
    32: "Enlightenment Threshold (Reason vs Faith)",
    33: "Industrial Integration (Machine-Human Symbiosis)",
    34: "Modern Mastery (Theory of Everything Pursuit)",
    35: "Technological Permanence (Silicon Trap)",
    # Cycle 5
    36: "Colonial Reset (Extraction Economics)",
    37: "Plantation Root (Chattel Foundation)",
    38: "Knowledge Appropriation",
    39: "Resistance Spark (Maroon Communities)",
    40: "Abolition Foundation (Legal Change)",
    41: "Civil Rights Threshold (Integration vs Separation)",
    42: "Post-Racial Integration (Colorblind Mythology)",
    43: "Diversity Mastery (Corporate Inclusion Theater)",
    44: "Meritocracy Trap (Bootstrap Permanence)",
    # Cycle 6 — Personal lifespan
    45: "Birth/Rebirth (Personal Reset)",
    46: "Attachment Root (Ages 0-7)",
    47: "Play Coherence (Ages 7-14)",
    48: "Identity Spark (Ages 14-21)",
    49: "Career Foundation (Ages 21-28)",
    50: "Partnership Threshold (Ages 28-35)",
    51: "Generativity Integration (Ages 35-49)",
    52: "Wisdom Mastery (Ages 49-63)",
    53: "Legacy Trap (Ages 63-72+)",
    # Cycle 7
    54: "Digital Reset (Internet Revolution)",
    55: "Platform Root (Web 2.0)",
    56: "Algorithm Coherence (Recommendation Engines)",
    57: "AI Spark (Machine Learning Breakthrough)",
    58: "Data Foundation (Everything Tracked)",
    59: "AGI Threshold (Consciousness or Simulation?)",
    60: "Human-AI Integration (Cyborg Harmony)",
    61: "Superintelligence Mastery (Godlike AI)",
    62: "Singularity Trap (Technological Permanence)",
    # Cycle 8
    63: "Ecological Collapse (Planetary Reset)",
    64: "Survival Root (Post-Collapse Communities)",
    65: "Regenerative Coherence (Healing Systems)",
    66: "Interspecies Spark (Beyond Human Supremacy)",
    67: "Planetary Foundation (Earth Governance)",
    68: "Cosmic Threshold (Extraterrestrial Contact?)",
    69: "Universal Integration (Consciousness as Substrate)",
    70: "Dimensional Mastery (Multiverse Navigation)",
    71: "Heat Death Trap (Entropy's Final Illusion)",
    # Great Return
    72: "The Great Return (Plenara Reclaimed — 72 = Stage 0)",
}

# Expected NSDT profiles per stage [N, S, T, D, C] all 0-10
# Key stages only — others interpolated
_EXPECTED_PROFILES: Dict[int, List[float]] = {
    0:  [0.0, 0.0, 0.0, 10.0, 0.0],  # Pure void, maximum adaptability
    5:  [3.5, 4.5, 7.5, 7.5, 5.5],   # Threshold: high T, high D required
    8:  [6.5, 9.5, 2.5, 1.5, 9.5],   # TRAP: max S, max C, min D
    9:  [5.0, 1.5, 8.5, 8.5, 3.5],   # Renewal: chaos, forced high D
    14: [3.5, 4.5, 7.5, 7.5, 5.5],   # Threshold (cycle 2)
    17: [6.0, 9.0, 2.5, 2.0, 9.0],   # Doctrinal trap
    26: [7.0, 9.5, 2.0, 1.5, 9.5],   # Imperial permanence trap
    32: [5.5, 5.0, 7.5, 7.0, 6.0],   # Enlightenment threshold
    35: [8.0, 9.0, 3.0, 2.0, 9.0],   # Silicon trap
    44: [7.5, 9.0, 2.5, 2.5, 8.5],   # Meritocracy trap
    50: [6.5, 5.5, 7.5, 6.5, 6.5],   # Partnership threshold
    53: [8.5, 9.5, 3.0, 1.5, 9.5],   # Legacy trap
    59: [9.0, 5.5, 7.5, 6.5, 7.0],   # AGI threshold
    62: [9.5, 8.5, 3.5, 2.5, 9.5],   # Singularity trap
    68: [9.0, 5.0, 7.5, 7.0, 7.0],   # Cosmic threshold
    71: [9.5, 8.0, 1.5, 2.0, 5.0],   # Heat death trap
}


def _get_stage_type(stage: int) -> Tuple[bool, bool, bool]:
    """Returns (is_trap, is_threshold, is_renewal)."""
    mod  = stage % 9
    trap       = (mod == 8) and (stage > 0)
    threshold  = (mod == 5)
    renewal    = (mod == 0) and (stage > 0)
    return trap, threshold, renewal


def _get_cycle(stage: int) -> int:
    return min(8, (stage // 9) + 1)


def _get_harmonic(stage: int) -> int:
    """Solfeggio frequency for stage (cycles through 174-963 Hz per 9 stages)."""
    return _SOLFEGGIO[stage % 9]


def _build_default_profile(stage: int) -> List[float]:
    """Interpolate expected profile for stages not in _EXPECTED_PROFILES."""
    if stage in _EXPECTED_PROFILES:
        return _EXPECTED_PROFILES[stage]
    # Find nearest anchors
    keys   = sorted(_EXPECTED_PROFILES.keys())
    lower  = max((k for k in keys if k <= stage), default=keys[0])
    upper  = min((k for k in keys if k >= stage), default=keys[-1])
    if lower == upper:
        return _EXPECTED_PROFILES[lower]
    t = (stage - lower) / (upper - lower)
    lo = _EXPECTED_PROFILES[lower]
    hi = _EXPECTED_PROFILES[upper]
    return [lo[i] + t * (hi[i] - lo[i]) for i in range(5)]


# ── Scoring engine ────────────────────────────────────────────────────────────

def _cosine_similarity(a: List[float], b: List[float],
                        weights: Optional[List[float]] = None) -> float:
    if weights is None:
        weights = [1.0, 1.2, 1.0, 1.5, 1.0]
    wa = [a[i] * weights[i] for i in range(5)]
    wb = [b[i] * weights[i] for i in range(5)]
    dot  = sum(wa[i] * wb[i] for i in range(5))
    ma   = math.sqrt(sum(x ** 2 for x in wa))
    mb   = math.sqrt(sum(x ** 2 for x in wb))
    if ma == 0 or mb == 0:
        return 0.0
    return dot / (ma * mb)


def _age_stage_prior(age: int) -> int:
    """Map biological age to most likely Cycle 6 stage."""
    if age < 7:    return 46
    if age < 14:   return 47
    if age < 21:   return 48
    if age < 28:   return 49
    if age < 35:   return 50
    if age < 49:   return 51
    if age < 63:   return 52
    return 53


# ── Assessment dataclasses ────────────────────────────────────────────────────

@dataclass
class CrisisAlert:
    crisis_type:  str    # TRAP_STATE | THRESHOLD_CRISIS | RENEWAL_STATE
    severity:     str    # CRITICAL | HIGH | TRANSFORMATIVE
    description:  str
    intervention: str
    cycle:        int


@dataclass
class SPAT72Result:
    primary_stage:    int
    primary_label:    str
    cycle:            int
    cycle_name:       str
    confidence:       float
    is_trap:          bool
    is_threshold:     bool
    is_renewal:       bool
    harmonic_hz:      int
    crisis_alert:     Optional[CrisisAlert]
    secondary_stages: List[Tuple[int, float]]    # (stage, confidence)
    user_scores:      List[float]                # [N, S, T, D, C]
    expected_scores:  List[float]
    criteria_match:   Dict[str, str]
    recommendation:   str
    next_stage_probs: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_stage":   self.primary_stage,
            "primary_label":   self.primary_label,
            "cycle":           self.cycle,
            "cycle_name":      self.cycle_name,
            "confidence":      round(self.confidence, 3),
            "is_trap":         self.is_trap,
            "is_threshold":    self.is_threshold,
            "is_renewal":      self.is_renewal,
            "harmonic_hz":     self.harmonic_hz,
            "crisis_alert":    (self.crisis_alert.__dict__ if self.crisis_alert else None),
            "secondary_stages": [(s, round(c, 3)) for s, c in self.secondary_stages],
            "criteria_match":  self.criteria_match,
            "recommendation":  self.recommendation,
            "next_stage_probs": self.next_stage_probs,
        }


# ── Main engine ───────────────────────────────────────────────────────────────

class SPAT72Engine:
    """
    72-Stage Personal Assessment Tool diagnostic engine.

    Usage:
        engine = SPAT72Engine()
        result = engine.assess(
            complexity=7, stability=6, tension=8, adaptability=7, coherence=6,
            age=32
        )
        print(result.to_dict())
        print(engine.full_cycle_table())
    """

    def assess(self,
               complexity:    float,
               stability:     float,
               tension:       float,
               adaptability:  float,
               coherence:     float,
               age:           Optional[int] = None,
               context_text:  str = "") -> SPAT72Result:
        """
        Run full 72-SPAT assessment.

        Args:
            complexity   : 0-10
            stability    : 0-10
            tension      : 0-10
            adaptability : 0-10
            coherence    : 0-10
            age          : optional biological age (applies Cycle 6 prior)
            context_text : optional free-text for keyword boost

        Returns:
            SPAT72Result with primary stage, crisis alert, recommendations.
        """
        user_scores = [complexity, stability, tension, adaptability, coherence]

        # Score all 72 stages
        matches: List[Tuple[int, float]] = []
        for s in range(73):
            profile    = _build_default_profile(s)
            similarity = _cosine_similarity(user_scores, profile)
            if context_text:
                similarity += self._keyword_boost(context_text, s) * similarity
            matches.append((s, similarity))

        # Age prior
        if age is not None:
            expected = _age_stage_prior(age)
            matches = [
                (s, sim * (1.0 + max(0.0, 0.3 - 0.1 * abs(s - expected))))
                for s, sim in matches
            ]

        matches.sort(key=lambda x: x[1], reverse=True)
        primary_stage, primary_conf = matches[0]
        secondary = [(s, c) for s, c in matches[1:6] if s != primary_stage]

        trap, threshold, renewal = _get_stage_type(primary_stage)
        cycle      = _get_cycle(primary_stage)
        harmonic   = _get_harmonic(primary_stage)
        expected   = _build_default_profile(primary_stage)

        # Criteria match annotation
        dims = ["Complexity(N)", "Stability(S)", "Tension(T)", "Adaptability(D)", "Coherence(C)"]
        criteria_match = {}
        for i, dim in enumerate(dims):
            diff = abs(user_scores[i] - expected[i])
            criteria_match[dim] = ("✓ aligned" if diff <= 2.0
                                   else ("⚠ slightly off" if diff <= 3.5 else "✗ divergent"))

        # Crisis detection
        crisis = self._detect_crisis(primary_stage, user_scores, cycle)

        # Recommendation
        rec = self._build_recommendation(primary_stage, trap, threshold, renewal,
                                         user_scores, crisis)

        # Next-stage probabilities (simplified)
        next_probs = self._forecast_next(primary_stage, user_scores)

        return SPAT72Result(
            primary_stage=primary_stage,
            primary_label=_STAGE_LABELS.get(primary_stage, f"Stage {primary_stage}"),
            cycle=cycle,
            cycle_name=_CYCLE_NAMES.get(cycle, ""),
            confidence=primary_conf,
            is_trap=trap,
            is_threshold=threshold,
            is_renewal=renewal,
            harmonic_hz=harmonic,
            crisis_alert=crisis,
            secondary_stages=secondary,
            user_scores=user_scores,
            expected_scores=expected,
            criteria_match=criteria_match,
            recommendation=rec,
            next_stage_probs=next_probs,
        )

    # ── Keyword boost ─────────────────────────────────────────────────────────

    def _keyword_boost(self, text: str, stage: int) -> float:
        kw_map: Dict[int, List[str]] = {
            0:  ["void", "empty", "nothing", "blank", "potential"],
            5:  ["choice", "decide", "crossroads", "threshold"],
            8:  ["permanent", "forever", "arrived", "complete", "established"],
            9:  ["ending", "loss", "breakdown", "release", "collapse"],
            26: ["empire", "too big to fail", "we will last"],
            35: ["technology", "tech will solve", "disruption"],
            44: ["meritocracy", "just work harder", "earned it"],
            50: ["marriage", "commitment", "children", "partner"],
            53: ["legacy", "my way", "back in my day", "young people"],
            62: ["singularity", "AGI", "upload", "immortal"],
        }
        keywords = kw_map.get(stage, [])
        t = text.lower()
        hits = sum(1 for kw in keywords if kw in t)
        return min(hits * 0.15, 0.5)

    # ── Crisis detection ──────────────────────────────────────────────────────

    def _detect_crisis(self, stage: int, scores: List[float],
                        cycle: int) -> Optional[CrisisAlert]:
        N, S, T, D, C = scores
        trap, threshold, renewal = _get_stage_type(stage)

        if trap and S >= 8 and D <= 3:
            return CrisisAlert(
                crisis_type  = "TRAP_STATE",
                severity     = "CRITICAL",
                description  = (
                    f"Stage {stage} permanence trap detected. "
                    f"High stability ({S:.1f}) with critically low adaptability ({D:.1f}). "
                    "Stage 8 Dual-Chamber Trap mechanics apply."
                ),
                intervention = (
                    f"Initiate controlled Stage {stage + 1} reset. "
                    "Reduce stability, increase adaptability. "
                    "Acknowledge Illusion of Permanence."
                ),
                cycle=cycle,
            )

        if threshold and T >= 7:
            return CrisisAlert(
                crisis_type  = "THRESHOLD_CRISIS",
                severity     = "HIGH",
                description  = (
                    f"Stage {stage} bilateral threshold with high tension ({T:.1f}). "
                    "Three paths available: progress, graceful regression, or crisis."
                ),
                intervention = (
                    "Apply Stage 5 DYNAMO OF WILL protocols. "
                    "Establish Witness Position before proceeding. "
                    "Define success/regression criteria explicitly."
                ),
                cycle=cycle,
            )

        if renewal and S <= 3 and T >= 7:
            return CrisisAlert(
                crisis_type  = "RENEWAL_STATE",
                severity     = "TRANSFORMATIVE",
                description  = (
                    f"Stage {stage} renewal/reset. Dissolution is intentional. "
                    "Low stability ({S:.1f}) and high tension ({T:.1f}) indicate necessary chaos."
                ),
                intervention = (
                    "Support dissolution. Do NOT attempt to restabilize prematurely. "
                    "Trust the PLENARA process. Renewal requires full release."
                ),
                cycle=cycle,
            )

        return None

    # ── Recommendation builder ────────────────────────────────────────────────

    def _build_recommendation(self, stage: int, trap: bool, threshold: bool,
                               renewal: bool, scores: List[float],
                               crisis: Optional[CrisisAlert]) -> str:
        N, S, T, D, C = scores
        if crisis and crisis.crisis_type == "TRAP_STATE":
            return (
                f"URGENT: You are in a Stage {stage} permanence trap. "
                "Immediately increase adaptability. Acknowledge that the current stable state "
                "is temporary — Illusion of Permanence is active. "
                f"Recommended harmonic: {_get_harmonic(stage)} Hz. "
                "Apply Gratitude Mechanism. Prepare for conscious dissolution."
            )
        if crisis and crisis.crisis_type == "THRESHOLD_CRISIS":
            return (
                f"Stage {stage} threshold requires conscious navigation. "
                "Three paths exist — the Middle Path (progression) requires D > 6 and T < 8. "
                "Your current D={:.1f} and T={:.1f}. ".format(D, T) +
                "Establish Witness Position before making threshold decisions."
            )
        if renewal:
            return (
                f"Stage {stage}: You are in a dissolution/renewal cycle. "
                "This chaos is necessary and not a failure. "
                "Allow completion of the old form before attempting reconstruction."
            )
        return (
            f"Stage {stage} ({_STAGE_LABELS.get(stage, '')}) — {_CYCLE_NAMES.get(_get_cycle(stage), '')}. "
            f"Recommended harmonic: {_get_harmonic(stage)} Hz. "
            f"Primary focus: {'Build adaptability' if D < 5 else 'Maintain coherence' if C < 6 else 'Navigate with awareness'}."
        )

    # ── Next-stage forecasting ────────────────────────────────────────────────

    def _forecast_next(self, stage: int, scores: List[float]) -> Dict[str, float]:
        N, S, T, D, C = scores
        trap, threshold, _ = _get_stage_type(stage)

        if threshold:
            p_prog = min(0.90, max(0.05, ((D + C - T) / 20.0 + 0.5)))
            p_reg  = min(0.50, max(0.05, ((10 - D + 10 - C) / 30.0)))
            p_cris = max(0.05, 1.0 - p_prog - p_reg)
            return {
                f"progress_to_stage_{stage + 1}": round(p_prog, 2),
                f"regress_to_stage_{stage - 1}":  round(p_reg, 2),
                "crisis":                          round(p_cris, 2),
            }
        if trap:
            p_stay = min(0.60, (S / 10.0) * (1.0 - D / 10.0))
            p_cont = max(0.10, 1.0 - p_stay)
            return {
                f"remain_at_stage_{stage}":     round(p_stay, 2),
                f"continue_to_stage_{stage+1}": round(p_cont, 2),
            }
        p_prog = min(0.80, D / 10.0 * 0.8 + C / 10.0 * 0.2)
        return {
            f"progress_to_stage_{stage + 1}": round(p_prog, 2),
            f"remain_at_stage_{stage}":       round(1.0 - p_prog, 2),
        }

    # ── Reference utilities ───────────────────────────────────────────────────

    def full_cycle_table(self) -> List[Dict[str, Any]]:
        """Return all 72 stages with type flags and harmonics."""
        rows = []
        for s in range(73):
            trap, threshold, renewal = _get_stage_type(s)
            rows.append({
                "stage":      s,
                "cycle":      _get_cycle(s),
                "cycle_name": _CYCLE_NAMES.get(_get_cycle(s), ""),
                "label":      _STAGE_LABELS.get(s, f"Stage {s}"),
                "harmonic_hz": _get_harmonic(s),
                "is_trap":    trap,
                "is_threshold": threshold,
                "is_renewal": renewal,
            })
        return rows

    def get_trap_stages(self) -> List[int]:
        """Return all 8 trap stages: 8, 17, 26, 35, 44, 53, 62, 71."""
        return [s for s in range(72) if _get_stage_type(s)[0]]

    def get_threshold_stages(self) -> List[int]:
        """Return all 8 threshold stages: 5, 14, 23, 32, 41, 50, 59, 68."""
        return [s for s in range(73) if _get_stage_type(s)[1]]


# ── Convenience wrapper ───────────────────────────────────────────────────────

def assess_72_spat(complexity: float, stability: float, tension: float,
                   adaptability: float, coherence: float,
                   age: Optional[int] = None) -> Dict[str, Any]:
    """One-line access for API endpoints."""
    return SPAT72Engine().assess(
        complexity, stability, tension, adaptability, coherence, age
    ).to_dict()
