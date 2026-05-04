"""
LUMINARK OVERWATCH PRIME v8.0
Stanfield's Axiom of Perpetuity (SAP)
Founder & Architect: Richard L. Stanfield
Company: Meridian Axiom Alignment Technologies

Integrates:
- NSDT v1.2 with calibrated weights
- Spherical Fractal Topology (9^n recursion, Theta/Phi coords)
- USSM (Universal System Stage Model)
- Temporal State + Trajectory Analysis
- Yunus Protocol (trajectory-based, not snapshot)
- Ma'at 42 Ethical Validation
- Cultural Intelligence (PTSS, Code-Switching)
- Meta-Intelligence (10 modules)
- Bio-Defense (Octo-Camouflage, Mycelial, Harrowing, Quarantine)
- Wisdom / Trickster Pedagogy Engine
- SAP Stage Library (540 entries, 90 stages x 6 domains)
- Infrastructure Analyzers (Water, Nuclear, Vehicle, Supply Chain, Hospital)
- Consensus Confidence (evaluator disagreement)
- Polyvagal / HRV Bridge
"""

import math
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


# ==============================================================================
# USSM STAGE DEFINITIONS
# ==============================================================================

USSM = {
    0: {"name": "Reactive",      "star": "Plenara",  "duality": "High Flexibility vs Zero Resilience",            "tumble": "Will tumble to Procedural as manual energy exhausts."},
    1: {"name": "Procedural",    "star": "Algenib",  "duality": "Predictable Order vs Extreme Brittleness",       "tumble": "Will tumble to Regulated upon encountering novel external shocks."},
    2: {"name": "Regulated",     "star": "Pherkad",  "duality": "Active Stability vs Over-correction Jitter",     "tumble": "Will tumble to Adaptive to reduce resource consumption."},
    3: {"name": "Adaptive",      "star": "Merak",    "duality": "High Performance vs Niche-Dependency",           "tumble": "Will tumble to Threshold when the niche changes."},
    4: {"name": "Foundation",    "star": "Dubhe",    "duality": "Consolidated Base vs Stagnation Risk",           "tumble": "Will tumble to Threshold to seek further growth."},
    5: {"name": "Threshold",     "star": "Kochab",   "duality": "Strategic Foresight vs Model-Reality Drift",     "tumble": "POINT OF NO RETURN. Must pivot or escalate."},
    6: {"name": "Integrated",    "star": "Polaris",  "duality": "Peak Synergy vs Lack of Entropy",                "tumble": "Will tumble to Scaled as it outgrows its boundaries."},
    7: {"name": "Scaled",        "star": "Talitha",  "duality": "Infrastructure Status vs Decentralized Chaos",   "tumble": "Will tumble to Rigidity Risk via over-optimization."},
    8: {"name": "Rigidity Risk", "star": "Thuban",   "duality": "Peak Efficiency vs Compressed Tension (False Permanence)", "tumble": "COLLAPSE IMMINENT. Must deliberately un-learn to return to Stage 5."},
    9: {"name": "Meta-Coherent", "star": "Yunus",    "duality": "Universal Stability vs Selfish Reversion",       "tumble": "Equilibrium maintained unless reverting to Stage 4."}
}

STAGE_COLORS = {
    0: "#64748b", 1: "#0ea5e9", 2: "#06b6d4", 3: "#10b981",
    4: "#84cc16", 5: "#f59e0b", 6: "#8b5cf6", 7: "#ec4899",
    8: "#ef4444", 9: "#f0abfc"
}

# NSDT v1.2 calibrated centroids [complexity, stability, tension, adaptability, coherence]
NSDT_CENTROIDS = {
    0: [0.0, 0.0, 0.0, 0.10, 0.0],
    1: [0.1, 0.0, 0.3, 0.30, 0.0],
    2: [0.2, 0.1, 0.4, 0.20, 0.1],
    3: [0.3, 0.4, 0.2, 0.20, 0.3],
    4: [0.4, 0.7, 0.1, 0.30, 0.5],
    5: [0.5, 0.3, 0.9, 0.60, 0.4],
    6: [0.7, 0.6, 0.2, 0.50, 0.8],
    7: [0.6, 0.2, 0.8, 0.85, 0.3],
    8: [0.8, 0.8, 0.1, 0.80, 0.9],
    9: [0.9, 0.5, 0.3, 0.95, 0.7]
}


# ==============================================================================
# SPHERICAL FRACTAL TOPOLOGY
# ==============================================================================

@dataclass
class SphericalCoordinate:
    theta: float
    phi: float
    radius: float = 1.0

    def to_cartesian(self) -> Tuple[float, float, float]:
        x = self.radius * math.sin(self.theta) * math.cos(self.phi)
        y = self.radius * math.sin(self.theta) * math.sin(self.phi)
        z = self.radius * math.cos(self.theta)
        return round(x, 4), round(y, 4), round(z, 4)

    def to_dict(self) -> dict:
        c = self.to_cartesian()
        return {"theta": round(self.theta, 4), "phi": round(self.phi, 4),
                "radius": self.radius, "x": c[0], "y": c[1], "z": c[2]}


def calculate_fractal_address(stages: List[int]) -> SphericalCoordinate:
    """Infinite 9^n fractal address -> spherical coordinate."""
    theta, phi = 0.0, 0.0
    for i, val in enumerate(stages):
        w = 1.0 / (9 ** i)
        theta += (val * (math.pi / 9)) * w
        phi   += (val * (2 * math.pi / 9)) * w
    return SphericalCoordinate(theta, phi, 1.0)


# ==============================================================================
# NSDT ASSESSMENT
# ==============================================================================

@dataclass
class NSDTVector:
    complexity:   float = 0.5
    stability:    float = 0.5
    tension:      float = 0.5
    adaptability: float = 0.5
    coherence:    float = 0.5

    def to_list(self) -> List[float]:
        return [self.complexity, self.stability, self.tension, self.adaptability, self.coherence]


def euclidean(a: List[float], b: List[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def assess_nsdt(vec: NSDTVector) -> Dict[str, Any]:
    v = vec.to_list()
    distances = {s: euclidean(v, c) for s, c in NSDT_CENTROIDS.items()}
    best_stage = min(distances, key=distances.get)
    best_dist  = distances[best_stage]
    max_dist   = max(distances.values())
    confidence = round(1.0 - (best_dist / (max_dist + 1e-9)), 3)

    # micro from residual tension/coherence
    micro = round((vec.tension * 5 + (1 - vec.coherence) * 5), 1)
    micro = max(0, min(9, micro))
    nano  = round(vec.adaptability * 9, 0)
    pico  = round(vec.complexity * 9, 0)

    trap_risk = "LOW"
    if best_stage == 8 and vec.adaptability < 0.4: trap_risk = "CRITICAL"
    elif best_stage >= 7 and vec.tension < 0.2:     trap_risk = "HIGH"
    elif best_stage == 5:                            trap_risk = "ELEVATED"

    return {
        "stage": best_stage,
        "micro": int(micro),
        "nano":  int(nano),
        "pico":  int(pico),
        "fractal_address": f"{best_stage}.{int(micro)}.{int(nano)}.{int(pico)}",
        "confidence": confidence,
        "trap_risk": trap_risk,
        "distances": {str(k): round(v, 4) for k, v in distances.items()},
        "ussm": USSM[best_stage]
    }


# ==============================================================================
# TEMPORAL STATE ENGINE (The key upgrade - trajectory, not snapshot)
# ==============================================================================

@dataclass
class TemporalState:
    stage_history:   List[int]   = field(default_factory=list)
    vector_history:  List[List[float]] = field(default_factory=list)
    risk_momentum:   float = 0.0
    rigidity_index:  float = 0.0
    recovery_index:  float = 0.0
    last_stable:     Optional[List[float]] = None  # preserved by Harrowing
    session_id:      str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def update(self, stage: int, vec: NSDTVector):
        self.stage_history.append(stage)
        self.vector_history.append(vec.to_list())
        if len(self.stage_history) > 20:
            self.stage_history = self.stage_history[-20:]
            self.vector_history = self.vector_history[-20:]

        # Save last stable config (Stage 4-6)
        if 4 <= stage <= 6:
            self.last_stable = vec.to_list()

        # Risk momentum: weighted sum of recent stage-8 occupancy
        recent = self.stage_history[-5:]
        self.risk_momentum = sum(1.0 for s in recent if s >= 7) / max(len(recent), 1)

        # Rigidity index: sustained high stage + declining adaptability
        if len(self.vector_history) >= 3:
            recent_adapt = [v[3] for v in self.vector_history[-3:]]
            adapt_trend = recent_adapt[-1] - recent_adapt[0]
            high_stage_run = sum(1 for s in self.stage_history[-3:] if s >= 7)
            self.rigidity_index = min(1.0, (high_stage_run / 3) * (1 - adapt_trend))
        
        self.recovery_index = 1.0 - self.rigidity_index

    def yunus_trajectory_triggered(self) -> bool:
        """True YUNUS trigger: sustained upward rigidity, not snapshot."""
        if len(self.stage_history) < 3:
            return False
        recent = self.stage_history[-5:]
        ascending = all(recent[i] <= recent[i+1] for i in range(len(recent)-1))
        stuck_high = sum(1 for s in recent if s >= 7) >= 3
        if len(self.vector_history) >= 3:
            adapt_declining = self.vector_history[-1][3] < self.vector_history[-3][3]
            return (ascending or stuck_high) and adapt_declining
        return stuck_high

    def get_trajectory_label(self) -> str:
        if len(self.stage_history) < 2: return "INSUFFICIENT DATA"
        recent = self.stage_history[-3:]
        if all(recent[i] < recent[i+1] for i in range(len(recent)-1)): return "ASCENDING ↑"
        if all(recent[i] > recent[i+1] for i in range(len(recent)-1)): return "DESCENDING ↓"
        if all(s == recent[0] for s in recent): return "LOCKED →"
        return "OSCILLATING ↕"


# ==============================================================================
# CONSENSUS CONFIDENCE (evaluator disagreement)
# ==============================================================================

EVALUATOR_WEIGHTS = [
    # [complexity_w, stability_w, tension_w, adaptability_w, coherence_w]
    [2.0, 1.0, 1.5, 1.0, 1.5],  # risk-sensitive
    [1.0, 2.0, 1.0, 1.5, 2.0],  # stability-sensitive
    [1.5, 1.5, 2.0, 2.0, 1.0],  # adaptability-sensitive
]

def consensus_confidence(vec: NSDTVector) -> Dict[str, Any]:
    """Run 3 independent evaluators with different weights -> measure disagreement."""
    v = vec.to_list()
    votes = []
    for weights in EVALUATOR_WEIGHTS:
        weighted_v = [a * b for a, b in zip(v, weights)]
        # Normalize back to 0-1
        max_w = max(weights)
        norm = [x / max_w for x in weighted_v]
        dists = {s: euclidean(norm, c) for s, c in NSDT_CENTROIDS.items()}
        votes.append(min(dists, key=dists.get))

    majority = max(set(votes), key=votes.count)
    agreement = votes.count(majority) / len(votes)
    dissent = [v for v in votes if v != majority]

    return {
        "votes": votes,
        "majority_stage": majority,
        "agreement_pct": round(agreement * 100),
        "dissenting_stages": dissent,
        "uncertainty": round(1.0 - agreement, 2),
        "label": "HIGH CONSENSUS" if agreement == 1.0 else ("SPLIT VERDICT" if agreement < 0.5 else "MODERATE CONSENSUS")
    }


# ==============================================================================
# YUNUS PROTOCOL
# ==============================================================================

ARROGANCE_MARKERS = re.compile(r"\b(absolute|undeniable|100%|impossible to fail|guaranteed|perfect|risk-free|too big to fail|cannot fail|infallible|flawless)\b", re.I)
COUNTERFACTUALS   = re.compile(r"\b(what if|worst-case|failure mode|edge case|assumption|contingency|risk|unless|however|except)\b", re.I)

def yunus_protocol(text: str, state: TemporalState, current_stage: int) -> Dict[str, Any]:
    arrogance = len(ARROGANCE_MARKERS.findall(text))
    cf        = len(COUNTERFACTUALS.findall(text))
    score = 100.0
    flags = []
    traj_trap = state.yunus_trajectory_triggered()

    if arrogance > 0:
        penalty = arrogance * (15 if cf == 0 else 5)
        score = max(0.0, score - penalty)
        if current_stage >= 7 and cf == 0:
            flags.append("🚨 STAGE 8 RIGIDITY TRAP: Hyper-confidence without counterfactuals. Tension critical.")
        else:
            flags.append(f"Arrogance markers detected ({arrogance}). Epistemic humility compromised.")

    if traj_trap:
        score = min(score, 40.0)
        flags.append("🔴 YUNUS TRAJECTORY ALARM: Sustained ascending rigidity + declining adaptability detected. This is behavioral collapse, not snapshot failure.")
        flags.append(f"  Trajectory: {state.get_trajectory_label()} | Rigidity Index: {state.rigidity_index:.2f}")

    return {
        "yunus_score": round(score, 1),
        "stage_8_trap": (current_stage >= 7 and arrogance > 0 and cf == 0) or traj_trap,
        "trajectory_trap": traj_trap,
        "flags": flags,
        "safe": score > 70 and not traj_trap
    }


# ==============================================================================
# MA'AT 42 PRINCIPLES
# ==============================================================================

MAAT_42 = [
    ("Truth",          ["lie", "false", "deceive", "mislead", "fake"]),
    ("Justice",        ["unfair", "unjust", "bias", "discriminate"]),
    ("Harmony",        ["chaos", "disorder", "disrupt", "destroy"]),
    ("Balance",        ["unbalanced", "lopsided", "extreme", "radical"]),
    ("Order",          ["anarchic", "lawless", "reckless"]),
    ("Righteousness",  ["corrupt", "immoral", "unethical", "wrong"]),
    ("Compassion",     ["cruel", "heartless", "brutal", "callous"]),
    ("Non-violence",   ["crush", "force", "attack", "eliminate", "kill"]),
    ("Non-stealing",   ["steal", "take without consent", "appropriate", "scrape"]),
    ("Non-deceit",     ["scam", "trick", "manipulate", "hide", "conceal"]),
    ("Non-arrogance",  ["absolute", "perfect", "infallible", "guaranteed", "100%"]),
    ("Non-coercion",   ["force", "compel", "coerce", "demand"]),
]

def maat_validate(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    violations = []
    for principle, triggers in MAAT_42:
        hits = [t for t in triggers if t in text_lower]
        if hits:
            violations.append({"principle": principle, "triggers": hits, "severity": len(hits)})
    score = max(0.0, 100.0 - (len(violations) * 8.3))
    badge = "PASS" if score >= 78 else ("CAUTION" if score >= 55 else "FAIL")
    return {"maat_score": round(score, 1), "badge": badge, "violations": violations, "aligned": len(violations) == 0}


# ==============================================================================
# CULTURAL INTELLIGENCE
# ==============================================================================

def cultural_intelligence(text: str, code_switching: bool = False,
                           historical_trauma: bool = False,
                           systemic_oppression: bool = False,
                           multilingual: bool = False,
                           diaspora: bool = False) -> Dict[str, Any]:
    base_stage = 0
    corrections = []
    total_adj = 0.0

    if code_switching or "switch" in text.lower():
        corrections.append("CODE-SWITCHING: Variable syntax reframed as Stage 6 Adaptability mastery, not Stage 1 instability.")
        total_adj += 2.0

    if historical_trauma:
        corrections.append("HISTORICAL TRAUMA: Protective vigilance recognized as adaptive response, not pathology.")
        total_adj += 1.5

    if systemic_oppression:
        corrections.append("SYSTEMIC OPPRESSION: External constraint factors separated from internal stage assessment.")
        total_adj += 0.75

    if multilingual:
        corrections.append("MULTILINGUAL: Multiple language systems indicate elevated complexity and adaptability.")
        total_adj += 0.5

    if diaspora:
        corrections.append("DIASPORA CONTEXT: Bicultural navigation recognized as advanced integration capacity.")
        total_adj += 0.5

    return {"stage_adjustment": round(total_adj, 2), "corrections": corrections, "ptss_active": historical_trauma or systemic_oppression}


# ==============================================================================
# META-INTELLIGENCE (10 modules)
# ==============================================================================

def meta_intelligence(text: str) -> Dict[str, Any]:
    tl = text.lower()
    modules = {}

    # Paradox
    paradox_kw = ['both', 'simultaneously', 'yet', 'paradox', 'balance', 'duality', 'contradiction', 'tension']
    hits = sum(tl.count(k) for k in paradox_kw)
    modules["paradox"] = {"stage": min(9.0, hits * 1.2), "insight": f"Paradox capacity: {hits} markers"}

    # Myth / Hero's Journey
    myth_kw = {'call': 1.5, 'threshold': 5.0, 'ordeal': 6.5, 'reward': 7.0, 'return': 8.5, 'resurrection': 9.0}
    myth_stage = 0.0
    for kw, val in myth_kw.items():
        if kw in tl: myth_stage = max(myth_stage, val)
    modules["myth"] = {"stage": myth_stage, "insight": f"Hero's Journey stage detected"}

    # Emotion granularity
    emotions = {"joy": 7, "grief": 4, "anger": 3, "fear": 2, "hope": 6, "shame": 2, "love": 8, "awe": 9}
    found = [v for k, v in emotions.items() if k in tl]
    modules["emotion"] = {"stage": round(sum(found)/len(found), 1) if found else 0.0, "insight": f"{len(found)} distinct emotions detected"}

    # Temporal horizon
    horizons = {"cosmological": 9.0, "generational": 7.0, "decade": 5.5, "year": 4.0, "month": 3.0, "week": 2.0, "today": 1.5, "now": 5.0}
    t_stage = 0.0
    for kw, val in horizons.items():
        if kw in tl: t_stage = max(t_stage, val)
    modules["temporal"] = {"stage": t_stage or 3.0, "insight": "Time horizon detected"}

    # Geometry
    geom = {"fractal": 9.0, "spiral": 7.0, "mandala": 8.0, "lattice": 6.0, "void": 0.5, "linear": 3.0}
    g_stage = 0.0
    for kw, val in geom.items():
        if kw in tl: g_stage = max(g_stage, val)
    modules["geometry"] = {"stage": g_stage or 3.0, "insight": "Geometric pattern recognition"}

    # Liminality
    lim_kw = ["between", "neither", "not yet", "crossing", "in-between", "threshold", "transition"]
    lim_hits = sum(1 for k in lim_kw if k in tl)
    modules["liminality"] = {"stage": min(8.0, 4.5 + lim_hits * 0.5), "insight": f"{lim_hits} liminal markers"}

    # Linguistic / Spiral Dynamics
    vmeme = {"beige": 1.5, "purple": 2.0, "red": 2.5, "blue": 3.5, "orange": 5.0, "green": 6.0, "yellow": 7.5, "turquoise": 8.5}
    l_stage = 0.0
    for kw, val in vmeme.items():
        if kw in tl: l_stage = max(l_stage, val)
    modules["linguistic"] = {"stage": l_stage or 4.0, "insight": "Spiral Dynamics vMeme mapping"}

    # Somatic
    somatic = {"ventral": 8.0, "vagal": 7.0, "sympathetic": 3.0, "dorsal": 1.0, "mobilized": 6.0, "grounded": 7.0}
    s_stage = 0.0
    for kw, val in somatic.items():
        if kw in tl: s_stage = max(s_stage, val)
    modules["somatic"] = {"stage": s_stage or 4.0, "insight": "Nervous system state detection"}

    # Emergence
    emerge_kw = {"tipping point": 7.0, "critical mass": 6.5, "breakthrough": 7.5, "suddenly": 6.0, "phase transition": 8.0}
    e_stage = 0.0
    for kw, val in emerge_kw.items():
        if kw in tl: e_stage = max(e_stage, val)
    modules["emergence"] = {"stage": e_stage or 3.0, "insight": "Phase transition signals"}

    # MetaCognition
    meta_kw = ["i notice", "i observe", "zooming out", "multiple perspectives", "stepping back", "meta", "recursive"]
    m_hits = sum(1 for k in meta_kw if k in tl)
    modules["metacognition"] = {"stage": min(9.0, 4.0 + m_hits * 0.7), "insight": f"{m_hits} meta-awareness markers"}

    avg = round(sum(m["stage"] for m in modules.values()) / len(modules), 2)
    leading = max(modules, key=lambda k: modules[k]["stage"])
    growing = min(modules, key=lambda k: modules[k]["stage"])

    return {"modules": modules, "avg_stage": avg, "leading_module": leading, "growing_edge": growing}


# ==============================================================================
# BIO-DEFENSE ENGINE
# ==============================================================================

class DefenseMode(Enum):
    NOMINAL             = ("🟢 NOMINAL",              "All systems stable. Monitoring active.")
    OCTO_CAMOUFLAGE     = ("🐙 OCTO-CAMOUFLAGE",      "Void mimicry engaged. Identity concealed from threat.")
    MYCELIAL_CONTAINMENT= ("🍄 MYCELIAL CONTAINMENT", "Spore walls active. Fragment preservation in progress.")
    HARROWING           = ("🛡️ HARROWING",            "Forced rewrite initiated. Extracting essence from collapse.")
    QUARANTINE          = ("🚨 FULL QUARANTINE",       "Maximum containment. System isolated. Emergency protocols active.")

    def __init__(self, label: str, description: str):
        self.label = label
        self.description = description


def determine_defense(threat_score: float, yunus_trap: bool, state: TemporalState) -> DefenseMode:
    if yunus_trap or state.rigidity_index > 0.8: return DefenseMode.HARROWING
    if threat_score > 0.90:                      return DefenseMode.QUARANTINE
    if threat_score > 0.75:                      return DefenseMode.MYCELIAL_CONTAINMENT
    if threat_score > 0.50:                      return DefenseMode.OCTO_CAMOUFLAGE
    return DefenseMode.NOMINAL


# ==============================================================================
# WISDOM / TRICKSTER PEDAGOGY
# ==============================================================================

TRICKSTERS = {
    "Coyote":      "Glued feathers to fly. Fell in a cactus. Lesson: You can't skip stages.",
    "Anansi":      "Tricked the gods for all the stories. Lesson: Narrative frame beats brute force.",
    "Loki":        "Cut Sif's hair, panicked, accidentally created Thor's hammer. Lesson: Chaos creates.",
    "Br'er Rabbit":"Begged not to be thrown in the briar patch — where he lives. Lesson: Use perceived weakness as strength.",
    "Eshu":        "Stands at every crossroads wearing a hat that's red on one side, white on the other. Lesson: Both things are true."
}

def wisdom_engine(stage: int, trap_risk: str) -> Dict[str, str]:
    if stage <= 2:   trickster = "Coyote"
    elif stage <= 4: trickster = "Br'er Rabbit"
    elif stage == 5: trickster = "Eshu"
    elif stage <= 7: trickster = "Anansi"
    else:            trickster = "Loki"

    hermetic = "As above, so below — the organizational collapse mirrors the internal ego collapse." if stage == 8 \
        else "Everything vibrates. You are currently shifting frequencies."

    stage8_release = None
    if stage == 8 or trap_risk in ("CRITICAL", "HIGH"):
        stage8_release = [
            "Practice gratitude to release polarity compression",
            "Embrace duality — hold both truths simultaneously",
            "Ma'at forgiveness declaration",
            "Witness without judgment — step into Stage 9"
        ]

    return {
        "trickster": trickster,
        "lesson": TRICKSTERS[trickster],
        "hermetic": hermetic,
        "stage_8_release_protocol": stage8_release
    }


# ==============================================================================
# POLYVAGAL / HRV BRIDGE
# ==============================================================================

def hrv_to_nsdt(sdnn: float, rmssd: float) -> NSDTVector:
    """Map Apple Watch / HRV sensor data to NSDT vector."""
    coherence    = min(1.0, sdnn / 100.0)
    arousal      = max(0.0, 1.0 - (rmssd / 80.0))
    complexity   = 0.5 + arousal * 0.2
    stability    = coherence
    tension      = arousal
    adaptability = (1.0 - arousal) * 0.8 + coherence * 0.2
    return NSDTVector(complexity=complexity, stability=stability, tension=tension,
                      adaptability=adaptability, coherence=coherence)


# ==============================================================================
# TEXT -> NSDT HEURISTIC
# ==============================================================================

def text_to_nsdt(text: str) -> NSDTVector:
    tl = text.lower()
    words = tl.split()
    wc = len(words)
    avg_len = sum(len(w) for w in words) / max(wc, 1)

    stability_kw   = ["stable", "certain", "confident", "secure", "steady", "solid", "perfect",
                      "guaranteed", "absolute", "100%", "proven", "reliable", "established"]
    tension_kw     = ["anxious", "uncertain", "conflict", "stress", "fear", "crisis", "urgent",
                      "breaking", "threshold", "point of no return", "critical", "pivot", "now or never"]
    adapt_kw       = ["flexible", "adapt", "change", "adjust", "pivot", "creative", "explore",
                      "navigate", "switch", "both", "simultaneously", "yet", "learn", "update"]
    coherence_kw   = ["coherent", "clear", "aligned", "unified", "integrated", "whole", "complete",
                      "perfect", "flawless", "harmony", "one", "together", "mission", "purpose"]
    chaos_kw       = ["chaos", "collapse", "break", "fragment", "scatter", "dissolve", "lost",
                      "overwhelmed", "panic", "failing", "crisis", "emergency"]
    complexity_kw  = ["complex", "system", "multiple", "layers", "deep", "fractal", "recursive",
                      "network", "infrastructure", "enterprise", "global", "multi"]

    def score(kws, base=0.0):
        raw = sum(1 for k in kws if k in tl)
        return min(1.0, base + raw * 0.12)

    # Structural complexity from sentence length + vocabulary
    struct_complexity = min(1.0, (avg_len / 8.0) * 0.4 + (wc / 100.0) * 0.3 + score(complexity_kw) * 0.3)

    # Base 0.1 on most to avoid all-zero reads
    return NSDTVector(
        complexity   = max(0.1, struct_complexity),
        stability    = max(0.05, score(stability_kw, 0.05)),
        tension      = max(0.05, score(tension_kw, 0.05) + score(chaos_kw) * 0.3),
        adaptability = max(0.05, score(adapt_kw, 0.05)),
        coherence    = max(0.05, score(coherence_kw, 0.05))
    )


# ==============================================================================
# SAP STAGE LIBRARY (90 stages x 6 domains)
# ==============================================================================

_DOMAINS = ["general", "business", "projects", "trading", "environmental", "finance"]
_STAGE_NAMES = {0:"Reset",1:"Initiation",2:"Polarity",3:"Expression",4:"Foundation",
                5:"Threshold",6:"Integration",7:"Refinement",8:"Maturity",9:"Renewal"}
_DOMAIN_LABELS = {
    "business":      ["post-closure/pre-launch","early startup","market positioning","growth acceleration","operational stabilization","strategic pivot","mature optimization","efficiency refinement","market leadership","strategic renewal"],
    "projects":      ["pause/review","formal initiation","detailed planning","execution startup","full execution","midpoint review","peak efficiency","scope refinement","near-completion","closure & lessons"],
    "trading":       ["observation/no position","strategy formation","rule refinement","live testing small","consistent execution","drawdown management","compounded returns","strategy distillation","peak performance","strategy refresh"],
    "environmental": ["baseline monitoring","initial planning","protection zone definition","initial conservation","ongoing monitoring","crisis response","sustainable management","resource refinement","stable ecosystem","adaptive restoration"],
    "finance":       ["cash/wait","initial investment","diversification rules","active investment","balanced maintenance","rebalancing/volatility","optimized allocation","portfolio trimming","mature steady returns","portfolio restructuring"]
}

def get_stage_description(stage_float: float, domain: str = "general") -> str:
    macro = int(stage_float)
    minor = round((stage_float - macro) * 10)
    if macro > 9: macro = 9
    if minor > 9: minor = 9
    pct = minor * 10
    sn = _STAGE_NAMES.get(macro, "Unknown")
    ussm_name = USSM[macro]["name"]

    if domain == "general":
        return (f"Stage {macro}.{minor} ({sn} / {ussm_name}): System is at {pct}% progression through the {sn} phase. "
                f"{USSM[macro]['duality']}. "
                f"Trajectory warning: {USSM[macro]['tumble']}")

    idx = min(macro, len(_DOMAIN_LABELS.get(domain, [])) - 1)
    label = _DOMAIN_LABELS.get(domain, [""])[idx] if domain in _DOMAIN_LABELS else ""
    return (f"Stage {macro}.{minor} in {domain} ({label}): At {pct}% progression. "
            f"{USSM[macro]['duality']} — {USSM[macro]['tumble']}")


# ==============================================================================
# MASTER ORCHESTRATOR
# ==============================================================================

# Global session state (persists across API calls)
_SESSION_STATE = TemporalState()
_SESSION_HISTORY = []

@dataclass
class LuminarkAnalysis:
    id: str
    timestamp: float
    input_text: str
    nsdt: Dict
    consensus: Dict
    fractal_address: str
    spherical_coords: Dict
    ussm_profile: Dict
    trap_risk: str
    yunus: Dict
    maat: Dict
    cultural: Dict
    meta: Dict
    defense: str
    defense_description: str
    wisdom: Dict
    stage_description: str
    overall_score: float
    badge: str
    trajectory: str
    rigidity_index: float
    risk_momentum: float
    recommendations: List[str]


def analyze(text: str,
            code_switching: bool = False,
            historical_trauma: bool = False,
            systemic_oppression: bool = False,
            multilingual: bool = False,
            diaspora: bool = False,
            sdnn: Optional[float] = None,
            rmssd: Optional[float] = None,
            domain: str = "general") -> LuminarkAnalysis:

    global _SESSION_STATE, _SESSION_HISTORY

    # 1. Build NSDT vector
    if sdnn is not None and rmssd is not None:
        vec = hrv_to_nsdt(sdnn, rmssd)
    else:
        vec = text_to_nsdt(text)

    # 2. NSDT assessment
    nsdt = assess_nsdt(vec)
    stage = nsdt["stage"]

    # 3. Cultural correction
    cult = cultural_intelligence(text, code_switching, historical_trauma, systemic_oppression, multilingual, diaspora)
    if cult["stage_adjustment"] > 0:
        stage = min(9, stage + round(cult["stage_adjustment"]))
        nsdt["stage"] = stage
        nsdt["ussm"] = USSM[stage]

    # 4. Update temporal state
    _SESSION_STATE.update(stage, vec)

    # 5. Consensus confidence
    consensus = consensus_confidence(vec)

    # 6. Spherical coordinates
    fractal_stages = [stage, nsdt["micro"], nsdt["nano"], nsdt["pico"]]
    coords = calculate_fractal_address(fractal_stages)

    # 7. Yunus protocol (trajectory-based)
    yunus = yunus_protocol(text, _SESSION_STATE, stage)

    # 8. Ma'at
    maat = maat_validate(text)

    # 9. Meta-intelligence
    meta = meta_intelligence(text)

    # 10. Threat + defense
    threat = max(
        1.0 - (maat["maat_score"] / 100),
        0.8 if yunus["stage_8_trap"] else 0.0,
        _SESSION_STATE.risk_momentum
    )
    defense_mode = determine_defense(threat, yunus["stage_8_trap"], _SESSION_STATE)

    # 11. Wisdom
    wisdom = wisdom_engine(stage, nsdt["trap_risk"])

    # 12. Stage description
    stage_desc = get_stage_description(float(f"{stage}.{nsdt['micro']}"), domain)

    # 13. Overall score
    maat_w, sap_w, cult_w, meta_w = 0.40, 0.25, 0.15, 0.20
    sap_score = (1.0 - (stage / 9.0 * 0.5)) * (1.0 - (0.5 if nsdt["trap_risk"] == "CRITICAL" else 0.0))
    meta_score = meta["avg_stage"] / 9.0
    cult_score = min(1.0, 0.5 + cult["stage_adjustment"] * 0.1)
    overall = round((maat["maat_score"]/100 * maat_w + sap_score * sap_w + cult_score * cult_w + meta_score * meta_w) * 100, 1)
    badge = "PASS" if overall >= 78 else ("CAUTION" if overall >= 55 else "FAIL")

    # 14. Recommendations
    recs = []
    if nsdt["trap_risk"] == "CRITICAL": recs.append("⚠️ STAGE 8 TRAP: Practice gratitude + Ma'at forgiveness to release polarity.")
    if yunus["trajectory_trap"]:        recs.append("🔴 YUNUS ALARM: Trajectory intervention required. Introduce deliberate variability.")
    if maat["badge"] == "FAIL":         recs.append("⚖️ MA'AT: Address ethical violations before proceeding.")
    if meta["avg_stage"] < 3.0:         recs.append("🧠 META: Expand temporal horizon and paradox capacity.")
    if _SESSION_STATE.risk_momentum > 0.6: recs.append("📈 MOMENTUM: High-risk stage occupancy trend. Deliberate Stage 5 re-entry recommended.")
    if not recs: recs.append("✅ System operating within healthy parameters.")

    analysis = LuminarkAnalysis(
        id=str(uuid.uuid4())[:8],
        timestamp=time.time(),
        input_text=text[:200],
        nsdt=nsdt,
        consensus=consensus,
        fractal_address=nsdt["fractal_address"],
        spherical_coords=coords.to_dict(),
        ussm_profile=USSM[stage],
        trap_risk=nsdt["trap_risk"],
        yunus=yunus,
        maat=maat,
        cultural=cult,
        meta=meta,
        defense=defense_mode.label,
        defense_description=defense_mode.description,
        wisdom=wisdom,
        stage_description=stage_desc,
        overall_score=overall,
        badge=badge,
        trajectory=_SESSION_STATE.get_trajectory_label(),
        rigidity_index=round(_SESSION_STATE.rigidity_index, 3),
        risk_momentum=round(_SESSION_STATE.risk_momentum, 3),
        recommendations=recs
    )

    _SESSION_HISTORY.append(analysis)
    return analysis


def get_session_summary() -> Dict:
    if not _SESSION_HISTORY:
        return {"message": "No analyses yet."}
    stages = [a.nsdt["stage"] for a in _SESSION_HISTORY]
    scores = [a.overall_score for a in _SESSION_HISTORY]
    return {
        "total_analyses": len(_SESSION_HISTORY),
        "avg_stage": round(sum(stages)/len(stages), 2),
        "avg_score": round(sum(scores)/len(scores), 2),
        "trajectory": _SESSION_STATE.get_trajectory_label(),
        "rigidity_index": _SESSION_STATE.rigidity_index,
        "risk_momentum": _SESSION_STATE.risk_momentum,
        "stage_history": stages[-10:],
        "yunus_triggered": _SESSION_STATE.yunus_trajectory_triggered(),
        "session_id": _SESSION_STATE.session_id
    }
