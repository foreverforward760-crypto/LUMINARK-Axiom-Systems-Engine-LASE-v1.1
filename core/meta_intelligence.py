"""
LUMINARK v4.0 — Meta-Intelligence Engine
10 independent consciousness analysis modules

Founder: Richard L. Stanfield | METATRON Align With Purpose
"""

import re
from typing import Dict, List, Any


def _count(text: str, keywords: List[str]) -> int:
    return sum(text.lower().count(k) for k in keywords)


class ParadoxEngine:
    KEYWORDS = ["both", "simultaneously", "yet", "paradox", "balance", "duality",
                "at once", "contradiction", "opposing", "tension between", "neither"]

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        hits = _count(text, cls.KEYWORDS)
        stage = min(9.9, hits * 1.5)
        return {
            "module": "Paradox",
            "icon": "⟳",
            "stage": round(stage, 1),
            "insight": (
                f"High paradox-holding capacity detected ({hits} markers). Stage 8-9 integrative capacity active."
                if hits >= 3 else
                f"Paradox markers present ({hits}). Both/and thinking emerging." if hits >= 1
                else "Either/or framing dominant. Paradox capacity not yet activated."
            ),
            "keywords_found": hits,
        }


class MythEngine:
    HERO_JOURNEY = {
        "call": ["heard the call", "invitation", "summoned", "beckoned", "called to"],
        "refusal": ["refused", "hesitated", "turned away", "ignored the call", "fear held"],
        "threshold": ["crossed", "stepped through", "entered", "committed", "point of no return"],
        "ordeal": ["trial", "struggle", "battle", "darkest moment", "crisis", "breakdown"],
        "reward": ["insight", "gift", "transformation", "revelation", "breakthrough"],
        "return": ["brought back", "shared", "returned with", "came home"],
        "resurrection": ["reborn", "renewed", "transformed", "emerged", "died and"],
    }

    ARCHETYPES = {
        "Hero": ["courage", "challenge", "overcome", "fight", "protect"],
        "Sage": ["wisdom", "knowledge", "understand", "learn", "truth"],
        "Creator": ["build", "create", "design", "innovate", "make"],
        "Caregiver": ["help", "support", "nurture", "care", "heal"],
        "Explorer": ["discover", "venture", "explore", "freedom", "journey"],
        "Rebel": ["disrupt", "challenge authority", "change system", "break rules"],
        "Innocent": ["hope", "simple", "trust", "optimism", "pure"],
        "Magician": ["transform", "catalyze", "transmute", "alchemy", "vision"],
    }

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        stage_hits = {stage: sum(text_lower.count(kw) for kw in kws)
                      for stage, kws in cls.HERO_JOURNEY.items()}
        active_stage = max(stage_hits, key=stage_hits.get)
        stage_count = sum(1 for v in stage_hits.values() if v > 0)

        arch_hits = {arch: sum(text_lower.count(kw) for kw in kws)
                     for arch, kws in cls.ARCHETYPES.items()}
        top_archetype = max(arch_hits, key=arch_hits.get)

        stage_score = min(9.9, stage_count * 1.2 + stage_hits.get(active_stage, 0) * 0.5)

        return {
            "module": "Myth",
            "icon": "⚔",
            "stage": round(stage_score, 1),
            "insight": f"Hero's Journey — currently at '{active_stage}' stage. Archetype: {top_archetype}.",
            "hero_journey_stage": active_stage,
            "archetype": top_archetype,
        }


class EmotionEngine:
    EMOTIONS = {
        "joy": ["joy", "happiness", "delight", "elation", "grateful"],
        "grief": ["grief", "loss", "mourn", "sorrow", "ache"],
        "anger": ["anger", "fury", "rage", "resentment", "frustration"],
        "fear": ["fear", "anxiety", "dread", "terror", "panic"],
        "hope": ["hope", "possibility", "potential", "optimism", "faith"],
        "shame": ["shame", "guilt", "embarrassment", "worthless"],
        "love": ["love", "compassion", "affection", "tenderness", "care"],
        "awe": ["awe", "wonder", "astonishment", "magnificent", "vast"],
        "disgust": ["disgust", "repelled", "revolted", "nausea"],
        "surprise": ["surprised", "unexpected", "shock", "astonished"],
    }

    PARADOX_PAIRS = [("joy", "grief"), ("fear", "hope"), ("anger", "love"), ("shame", "awe")]

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        emotion_scores = {em: sum(text_lower.count(kw) for kw in kws)
                          for em, kws in cls.EMOTIONS.items()}

        active = [em for em, score in emotion_scores.items() if score > 0]
        granularity = len(active)
        stage = min(9.9, granularity * 0.9)

        paradoxes = [f"{a}+{b}" for a, b in cls.PARADOX_PAIRS
                     if emotion_scores.get(a, 0) > 0 and emotion_scores.get(b, 0) > 0]
        if paradoxes:
            stage = min(9.9, stage + len(paradoxes) * 1.5)

        return {
            "module": "Emotion",
            "icon": "♥",
            "stage": round(stage, 1),
            "insight": (
                f"High emotional granularity ({granularity} emotions). Paradox pairs: {', '.join(paradoxes)}."
                if paradoxes else
                f"{granularity} emotion types detected. Emotional vocabulary at {round(granularity/10*100)}% capacity."
            ),
            "active_emotions": active,
            "paradox_pairs_held": paradoxes,
        }


class TemporalEngine:
    HORIZONS = [
        ("cosmological", ["cosmic", "universal", "eternal", "infinite time", "eons", "geological"], 9.0),
        ("generational", ["generation", "legacy", "ancestors", "descendants", "centuries"], 7.0),
        ("decades", ["decade", "long-term", "twenty years", "thirty years", "lifespan"], 5.5),
        ("years", ["this year", "annual", "next year", "five years"], 4.0),
        ("months", ["this month", "quarterly", "season", "months"], 3.0),
        ("present", ["today", "now", "this moment", "immediate", "current"], 2.0),
    ]

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        detected = [(h, s) for h, kws, s in cls.HORIZONS if any(kw in text_lower for kw in kws)]
        
        if not detected:
            return {"module": "Temporal", "icon": "◷", "stage": 2.0,
                    "insight": "Default temporal orientation. Present-focus dominant.", "horizons": []}

        max_stage = max(s for _, s in detected)
        simultaneity_bonus = 0.5 * (len(detected) - 1) if len(detected) > 1 else 0
        final_stage = min(9.9, max_stage + simultaneity_bonus)

        return {
            "module": "Temporal",
            "icon": "◷",
            "stage": round(final_stage, 1),
            "insight": (
                f"Multiple time horizons held simultaneously: {', '.join(h for h, _ in detected)}. "
                f"Simultaneity bonus: +{simultaneity_bonus}."
                if len(detected) > 1
                else f"Time horizon: {detected[0][0]}."
            ),
            "horizons": [h for h, _ in detected],
        }


class GeometryEngine:
    PATTERNS = {
        "fractal": (["fractal", "recursive", "self-similar", "infinite recursion"], 9.0),
        "spiral": (["spiral", "helix", "cyclical growth", "expanding cycles"], 7.0),
        "mandala": (["mandala", "radial symmetry", "concentric", "center"], 8.0),
        "lattice": (["lattice", "network", "web", "interconnected"], 6.0),
        "void": (["void", "empty", "nothingness", "formless"], 0.5),
        "linear": (["linear", "sequential", "step by step", "one direction"], 3.0),
        "wave": (["wave", "oscillation", "rhythm", "pulse"], 5.5),
    }

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        found = {name: stage for name, (kws, stage) in cls.PATTERNS.items()
                 if any(kw in text_lower for kw in kws)}
        
        if not found:
            return {"module": "Geometry", "icon": "✦", "stage": 3.0,
                    "insight": "No geometric pattern language detected.", "patterns": []}
        
        top = max(found, key=found.get)
        return {
            "module": "Geometry",
            "icon": "✦",
            "stage": round(found[top], 1),
            "insight": f"Primary geometric pattern: {top} (stage {found[top]}). All patterns: {list(found.keys())}.",
            "patterns": list(found.keys()),
        }


class LiminalityEngine:
    MARKERS = ["between", "neither", "not yet", "crossing", "in-between", "liminal",
               "threshold", "transitional", "on the edge", "verge", "cusp", "becoming"]

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        hits = _count(text, cls.MARKERS)
        stage = min(8.5, 4.5 + hits * 0.5)
        return {
            "module": "Liminality",
            "icon": "◈",
            "stage": round(stage, 1),
            "insight": (
                f"Strong liminal awareness ({hits} markers). System is consciously occupying the in-between."
                if hits >= 3 else
                f"Liminal markers present ({hits}). Threshold awareness active." if hits >= 1
                else "No liminal language. Fixed-state orientation dominant."
            ),
            "markers_found": hits,
        }


class LinguisticEngine:
    VMEMES = {
        "beige": (["survive", "basic needs", "hunger", "instinct", "immediate danger"], 1.5),
        "purple": (["tribe", "ritual", "spirits", "ancestors", "sacred tradition", "group bond"], 2.0),
        "red": (["power", "dominate", "control", "alpha", "force", "conquer"], 2.5),
        "blue": (["rules", "order", "authority", "discipline", "duty", "hierarchy", "law"], 3.5),
        "orange": (["optimize", "strategy", "win", "compete", "results", "ROI", "efficiency"], 5.0),
        "green": (["community", "equality", "empathy", "consensus", "inclusion", "harmony"], 6.0),
        "yellow": (["systemic", "integral", "complexity", "emergence", "flow", "functional fit"], 7.5),
        "turquoise": (["holistic", "planetary", "consciousness", "collective", "kosmos"], 8.5),
    }

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        vmeme_scores = {}
        for vmeme, (kws, stage) in cls.VMEMES.items():
            count = sum(text_lower.count(kw) for kw in kws)
            if count > 0:
                vmeme_scores[vmeme] = (count, stage)

        if not vmeme_scores:
            return {"module": "Linguistic", "icon": "✎", "stage": 3.5,
                    "insight": "Blue vMeme baseline. Rule-based orientation.", "vmeme": "blue"}

        top_vmeme = max(vmeme_scores, key=lambda k: vmeme_scores[k][0])
        top_stage = vmeme_scores[top_vmeme][1]

        words = text.split()
        avg_len = sum(len(w) for w in words) / max(1, len(words))
        complexity_bonus = min(1.0, (avg_len - 4) * 0.2) if avg_len > 4 else 0

        final = min(9.9, top_stage + complexity_bonus)
        return {
            "module": "Linguistic",
            "icon": "✎",
            "stage": round(final, 1),
            "insight": f"Dominant vMeme: {top_vmeme.upper()} (stage {top_stage}). Sentence complexity bonus: +{complexity_bonus:.2f}.",
            "vmeme": top_vmeme,
            "all_vmemes": list(vmeme_scores.keys()),
        }


class SomaticEngine:
    STATES = {
        "ventral_vagal": (["safety", "calm", "connected", "grounded", "relaxed", "present"], 8.0),
        "sympathetic": (["fight", "flight", "panic", "overwhelmed", "racing", "urgent", "survival"], 3.0),
        "dorsal_vagal": (["frozen", "shutdown", "numb", "dissociated", "collapsed", "disappeared"], 1.0),
        "mobilized": (["energized", "activated", "ready", "engaged", "alive", "purposeful"], 6.0),
    }

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        state_scores = {state: sum(text_lower.count(kw) for kw in kws)
                        for state, (kws, _) in cls.STATES.items()}
        top_state = max(state_scores, key=state_scores.get)
        stage = cls.STATES[top_state][1]

        return {
            "module": "Somatic",
            "icon": "◎",
            "stage": stage,
            "insight": (
                f"Nervous system state: {top_state.replace('_', ' ').title()} "
                f"(markers: {state_scores[top_state]}). "
                f"Stage {stage} somatic signature."
            ),
            "nervous_system_state": top_state,
        }


class EmergenceEngine:
    SIGNALS = ["tipping point", "critical mass", "breakthrough", "suddenly", "phase transition",
               "emergence", "spontaneous", "threshold crossed", "cascade", "avalanche effect",
               "inflection", "pivot point", "non-linear change"]

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        hits = _count(text, cls.SIGNALS)
        stage = min(9.5, 5.0 + hits * 0.8)
        return {
            "module": "Emergence",
            "icon": "✺",
            "stage": round(stage, 1),
            "insight": (
                f"Strong emergence signals ({hits}). Phase transition in progress or imminent."
                if hits >= 3 else
                f"Emergence indicators present ({hits}). System approaching phase transition." if hits >= 1
                else "No emergence signals. System in stable operation mode."
            ),
            "signals_found": hits,
        }


class MetaCognitionEngine:
    MARKERS = ["i notice", "i observe", "zooming out", "multiple perspectives",
               "meta-level", "aware that", "watching myself", "from above",
               "recursive", "thinking about my thinking", "second order", "witnessing"]

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        hits = _count(text, cls.MARKERS)
        stage = min(9.9, 4.0 + hits * 1.2)
        return {
            "module": "MetaCognition",
            "icon": "∞",
            "stage": round(stage, 1),
            "insight": (
                f"Deep recursive self-awareness ({hits} markers). Stage 8-9 meta-cognitive capacity active."
                if hits >= 3 else
                f"Meta-awareness present ({hits}). Witnessing perspective active." if hits >= 1
                else "Immersive perspective dominant. Meta-awareness not yet activated."
            ),
            "markers_found": hits,
        }


class MetaIntelligenceEngine:

    MODULES = [
        ParadoxEngine, MythEngine, EmotionEngine, TemporalEngine,
        GeometryEngine, LiminalityEngine, LinguisticEngine,
        SomaticEngine, EmergenceEngine, MetaCognitionEngine,
    ]

    @classmethod
    def analyze_all(cls, text: str) -> Dict[str, Any]:
        results = {}
        stages = []

        for module_class in cls.MODULES:
            result = module_class.analyze(text)
            name = result["module"]
            results[name] = result
            stages.append(result["stage"])

        avg_stage = round(sum(stages) / len(stages), 2)
        sorted_by_stage = sorted(results.items(), key=lambda x: x[1]["stage"], reverse=True)

        return {
            "modules": results,
            "avg_stage": avg_stage,
            "leading_edge": sorted_by_stage[0][0] if sorted_by_stage else "None",
            "growing_edge": sorted_by_stage[-1][0] if sorted_by_stage else "None",
            "module_count": len(results),
            "synthesis": (
                f"Meta-intelligence center of gravity: Stage {avg_stage}. "
                f"Strongest signal: {sorted_by_stage[0][0]} ({sorted_by_stage[0][1]['stage']}). "
                f"Lowest activation: {sorted_by_stage[-1][0]} ({sorted_by_stage[-1][1]['stage']})."
            ),
        }
