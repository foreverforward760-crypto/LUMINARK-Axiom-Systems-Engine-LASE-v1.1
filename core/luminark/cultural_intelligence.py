"""
LUMINARK v4.0 — Cultural Intelligence
Double Consciousness, PTSS, Code-Switching corrections

Founder: Richard L. Stanfield | METATRON Align With Purpose
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional


@dataclass
class CulturalContext:
    code_switching_observed: bool = False
    historical_trauma_indicators: bool = False
    systemic_oppression_factors: bool = False
    multilingual: bool = False
    diaspora_context: bool = False
    ethnicity_flag: Optional[str] = None


PTSS_PATTERNS = {
    "vacant_esteem": {
        "description": "Disconnection from cultural identity and self-worth",
        "behavioral_markers": ["self-deprecation", "identity confusion", "cultural shame"],
        "reframe": "This is a trauma response to sustained identity invalidation, not a character flaw.",
        "sap_correction": 1.5,
    },
    "propensity_anger": {
        "description": "Hair-trigger anger in response to perceived disrespect",
        "behavioral_markers": ["explosive response", "disproportionate anger", "reactive hostility"],
        "reframe": "Anger is the appropriate response to repeated boundary violations. This is adaptive, not pathological.",
        "sap_correction": 1.0,
    },
    "internalized_racism": {
        "description": "Adoption of oppressive narratives about one's own community",
        "behavioral_markers": ["self-blame", "distancing from culture", "colorism internalization"],
        "reframe": "This is the most insidious symptom — systemic ideology successfully installed in the target.",
        "sap_correction": 2.0,
    },
    "hypervigilance": {
        "description": "Constant scanning for racial threat in the environment",
        "behavioral_markers": ["guarded behavior", "excessive caution", "threat scanning"],
        "reframe": "In a historically threatening environment, hypervigilance is intelligence — not disorder.",
        "sap_correction": 1.5,
    },
    "cultural_ptss": {
        "description": "Intergenerational transmission of trauma responses",
        "behavioral_markers": ["legacy behaviors", "inherited fear", "multi-generational pattern"],
        "reframe": "What looks like dysfunction is frequently wisdom carried forward from survival contexts.",
        "sap_correction": 1.5,
    },
}


class CulturalIntelligenceFilter:

    @classmethod
    def apply_corrections(
        cls, base_stage: float, text: str, context: CulturalContext
    ) -> Dict[str, Any]:
        adjusted_stage = base_stage
        corrections = []
        total_correction = 0.0

        # Code-switching: reading as Stage 6 mastery, not Stage 1 instability
        if context.code_switching_observed or "switch" in text.lower():
            correction = 2.0 if base_stage < 5 else 0.5
            adjusted_stage += correction
            total_correction += correction
            corrections.append({
                "type": "CODE_SWITCHING",
                "correction": f"+{correction}",
                "explanation": (
                    "Code-switching detected. This is Stage 6 cognitive flexibility "
                    "(simultaneous management of multiple linguistic and cultural registers), "
                    "not Stage 1 instability. Assessment adjusted upward."
                ),
            })

        # Historical trauma
        if context.historical_trauma_indicators:
            correction = 1.5
            adjusted_stage += correction
            total_correction += correction
            corrections.append({
                "type": "HISTORICAL_TRAUMA",
                "correction": f"+{correction}",
                "explanation": (
                    "Historical trauma indicators present. Baseline capacity is higher than presented "
                    "metrics suggest. Intergenerational load must be separated from individual capability."
                ),
            })

        # Systemic oppression
        if context.systemic_oppression_factors:
            correction = 0.75
            adjusted_stage += correction
            total_correction += correction
            corrections.append({
                "type": "SYSTEMIC_OPPRESSION",
                "correction": f"+{correction}",
                "explanation": (
                    "Systemic oppression factors active. Performance suppressed by external constraints, "
                    "not internal limitation. Actual capacity exceeds measured output."
                ),
            })

        # Multilingual
        if context.multilingual:
            correction = 0.5
            adjusted_stage += correction
            total_correction += correction
            corrections.append({
                "type": "MULTILINGUAL",
                "correction": f"+{correction}",
                "explanation": "Multilingual capacity reflects Stage 6 cognitive complexity.",
            })

        # Diaspora
        if context.diaspora_context:
            correction = 0.5
            adjusted_stage += correction
            total_correction += correction
            corrections.append({
                "type": "DIASPORA",
                "correction": f"+{correction}",
                "explanation": "Diaspora experience reflects navigating multiple cultural frameworks simultaneously.",
            })

        # PTSS detection
        ptss_detected = cls.detect_ptss(text)

        return {
            "original_stage": base_stage,
            "adjusted_stage": round(min(9.9, adjusted_stage), 2),
            "total_correction": round(total_correction, 2),
            "corrections": corrections,
            "ptss_detected": ptss_detected,
            "ekman_correction": (
                "Deception likelihood score reduced by 70%. Code-switching behaviors flagged as "
                "adaptive, not deceptive. Body language freeze-response reframed as adaptive vigilance."
                if context.code_switching_observed else None
            ),
        }

    @staticmethod
    def detect_ptss(text: str) -> List[Dict]:
        text_lower = text.lower()
        detected = []
        for pattern_name, data in PTSS_PATTERNS.items():
            if any(marker in text_lower for marker in data["behavioral_markers"]):
                detected.append({
                    "pattern": pattern_name,
                    "description": data["description"],
                    "reframe": data["reframe"],
                    "suggested_correction": data["sap_correction"],
                })
        return detected
