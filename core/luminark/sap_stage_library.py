"""
LUMINARK v4.0 — SAP Engine + 540-Entry Stage Library
Stanfield's Axiom of Perpetuity — full implementation

Founder: Richard L. Stanfield | METATRON Align With Purpose
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


NSDT_CENTROIDS: Dict[int, List[float]] = {
    0: [0.15, 0.20, 0.10, 0.30, 0.15],
    1: [0.25, 0.55, 0.20, 0.35, 0.30],
    2: [0.35, 0.65, 0.30, 0.40, 0.50],
    3: [0.55, 0.50, 0.45, 0.55, 0.55],
    4: [0.50, 0.70, 0.35, 0.50, 0.65],
    5: [0.75, 0.40, 0.75, 0.65, 0.50],
    6: [0.70, 0.65, 0.50, 0.70, 0.75],
    7: [0.65, 0.70, 0.55, 0.60, 0.80],
    8: [0.80, 0.85, 0.70, 0.30, 0.85],
    9: [0.75, 0.75, 0.40, 0.80, 0.90],
}

STAGE_NAMES = {
    0: "Plenara", 1: "Algenib", 2: "Pherkad", 3: "Merak", 4: "Dubhe",
    5: "Kochab", 6: "Polaris", 7: "Talitha", 8: "Thuban", 9: "Yunus",
}

STAGE_COLORS = {
    0: "#6B7280", 1: "#60A5FA", 2: "#34D399", 3: "#F59E0B", 4: "#A78BFA",
    5: "#EF4444", 6: "#06B6D4", 7: "#F97316", 8: "#DC2626", 9: "#8B5CF6",
}

TRAP_CELLS = {(5, 5), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4),
              (8, 5), (8, 6), (8, 7), (8, 8), (8, 9)}

THRESHOLD_CELLS = {(5, 0), (5, 1), (5, 2), (5, 3), (5, 4),
                   (5, 6), (5, 7), (5, 8), (5, 9)}

TRAP_RISK_LEVELS = [
    ("CRITICAL", 0.75, "#DC2626"),
    ("HIGH", 0.50, "#EF4444"),
    ("ELEVATED", 0.30, "#F59E0B"),
    ("WATCH", 0.15, "#60A5FA"),
    ("LOW", 0.0, "#22C55E"),
]


@dataclass
class NSDTVector:
    complexity: float
    stability: float
    tension: float
    adaptability: float
    coherence: float

    def to_list(self):
        return [self.complexity, self.stability, self.tension,
                self.adaptability, self.coherence]


@dataclass
class SAPPosition:
    macro: int
    micro: int
    nano: int
    pico: int
    stage_float: float
    stage_name: str
    stage_color: str
    confidence: float
    trap_risk: str
    trap_risk_color: str
    fractal_address: str
    trap_score: float
    is_trap_cell: bool
    is_threshold: bool
    distances: Dict[int, float]


def trapscore(stagnation, rigidity, adaptability):
    return round(stagnation * rigidity * (1.0 - adaptability), 4)


def compute_trap_risk_level(score):
    for level, threshold, color in TRAP_RISK_LEVELS:
        if score >= threshold:
            return level, color
    return "LOW", "#22C55E"


class SAPStageDetector:

    @staticmethod
    def euclidean(a, b):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    @classmethod
    def assess(cls, vector: NSDTVector) -> SAPPosition:
        vec = vector.to_list()
        distances = {s: round(cls.euclidean(vec, c), 4) for s, c in NSDT_CENTROIDS.items()}
        sorted_stages = sorted(distances.items(), key=lambda x: x[1])
        macro = sorted_stages[0][0]
        best_dist = sorted_stages[0][1]
        second_dist = sorted_stages[1][1] if len(sorted_stages) > 1 else 1.0

        micro = round((1 - best_dist / (best_dist + second_dist)) * 9)
        nano = min(9, int(vector.tension * 10))
        pico = min(9, int(vector.coherence * 10))

        max_dist = math.sqrt(5)
        confidence = round(max(0.0, 1.0 - best_dist / max_dist), 3)
        stage_float = round(macro + micro / 10, 1)

        stagnation = vector.tension
        rigidity = 1.0 - vector.stability
        ts = trapscore(stagnation, rigidity, vector.adaptability)
        trap_risk, trap_color = compute_trap_risk_level(ts)

        return SAPPosition(
            macro=macro, micro=micro, nano=nano, pico=pico,
            stage_float=stage_float,
            stage_name=STAGE_NAMES.get(macro, "Unknown"),
            stage_color=STAGE_COLORS.get(macro, "#6B7280"),
            confidence=confidence,
            trap_risk=trap_risk, trap_risk_color=trap_color,
            fractal_address=f"{macro}.{micro}.{nano}.{pico}",
            trap_score=ts,
            is_trap_cell=(macro, micro) in TRAP_CELLS,
            is_threshold=(macro, micro) in THRESHOLD_CELLS,
            distances=distances,
        )

    @classmethod
    def assess_from_text(cls, text: str) -> NSDTVector:
        words = text.lower().split()
        word_count = max(1, len(words))
        avg_word_len = sum(len(w) for w in words) / word_count
        unique_ratio = len(set(words)) / word_count
        complexity = min(1.0, (avg_word_len / 10) * 0.5 + unique_ratio * 0.5)

        stable_kw = ["stable", "consistent", "reliable", "foundation", "steady", "certain", "solid", "proven"]
        stability = min(1.0, 0.3 + sum(text.lower().count(k) for k in stable_kw) * 0.07)

        tension_kw = ["crisis", "urgent", "critical", "risk", "threat", "collapse", "breaking", "tension", "conflict"]
        tension = min(1.0, sum(text.lower().count(k) for k in tension_kw) * 0.12)

        adapt_kw = ["adapt", "flexible", "pivot", "change", "evolve", "adjust", "agile", "iterate"]
        adaptability = min(1.0, 0.3 + sum(text.lower().count(k) for k in adapt_kw) * 0.07)

        coh_kw = ["integrate", "coherent", "aligned", "unified", "connected", "holistic", "systemic"]
        coherence = min(1.0, 0.3 + sum(text.lower().count(k) for k in coh_kw) * 0.08)

        return NSDTVector(complexity, stability, tension, adaptability, coherence)


# ── STAGE LIBRARY ─────────────────────────────────────────────────────────────

_STAGE_DEFS = {
    0: ("Plenara / Reset", "System has cleared previous patterns. Quiet. Available. Not empty — potential in its purest form."),
    1: ("Algenib / Initiation", "Basic structure forming. Low complexity, high flexibility. Testing viability through simple actions."),
    2: ("Pherkad / Regulation", "Clear boundaries and feedback loops established. Homeostatic control active. Rules are forming."),
    3: ("Merak / Adaptive Growth", "Creative expansion underway. System tests capabilities against reality. Tension is productive here."),
    4: ("Dubhe / Foundation", "Consolidated, stable architecture. Reliable. The platform for everything above it."),
    5: ("Kochab / Threshold", "Point of no return. Bifurcation point. Small actions carry massive consequence. No neutral option."),
    6: ("Polaris / Integration", "Peak synergy. Harmonious, high-coherence operation. The system works as a unified whole."),
    7: ("Talitha / Distillation", "System becomes infrastructure. Refined to its essence. Distributed. Carrying others."),
    8: ("Thuban / Rigidity Trap", "Peak efficiency masking compressed tension. False permanence. System believes it has arrived. Dangerous."),
    9: ("Yunus / Meta-Coherence", "Conscious renewal. Paradox held without collapse. Transformation harvests everything built."),
}

_DOMAINS = {
    "general": "At {pct}% progression, the defining dynamic is: {desc} Core signal: honest assessment before new commitment.",
    "business": "In business, Stage {stage}: {desc} Strategic priority — match operational decisions to actual maturity, not aspiration.",
    "projects": "In project management, Stage {stage}: {desc} Adjust scope, risk tolerance, and stakeholder expectations accordingly.",
    "trading": "In trading, Stage {stage}: {desc} Position sizing, validation rigor, and hedging requirements all shift here.",
    "environmental": "In environmental protection, Stage {stage}: {desc} Intervention intensity and monitoring frequency follow this profile.",
    "finance": "In finance, Stage {stage}: {desc} Capital allocation, risk exposure, and portfolio structure should match this phase.",
}


def _build_library():
    lib = {}
    for macro in range(10):
        name, desc = _STAGE_DEFS[macro]
        for minor in range(10):
            key = f"{macro}.{minor}"
            pct = minor * 10
            lib[key] = {}
            for domain, template in _DOMAINS.items():
                lib[key][domain] = (
                    f"Stage {macro}.{minor} — {name}. "
                    + template.format(stage=f"{macro}.{minor}", pct=pct, desc=desc)
                )
    return lib


_STAGE_LIBRARY = _build_library()


def get_stage_description(stage: float, domain: str = "general") -> str:
    key = f"{stage:.1f}"
    entry = _STAGE_LIBRARY.get(key)
    if not entry:
        return f"Stage {stage} not found."
    return entry.get(domain, entry["general"])
