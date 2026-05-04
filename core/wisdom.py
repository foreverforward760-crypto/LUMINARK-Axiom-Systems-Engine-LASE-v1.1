"""
LUMINARK v4.0 — Wisdom & Trickster Pedagogy Engine
Stage-appropriate wisdom, hermetic laws, trickster archetypes

Founder: Richard L. Stanfield | METATRON Align With Purpose
"""

from typing import Dict, Any


# =============================================================================
# TRICKSTER ARCHETYPES
# =============================================================================

TRICKSTERS = {
    "Coyote": {
        "origin": "Native American (Navajo, Lakota)",
        "lesson": "You can't skip stages. Coyote glued feathers to fly. Fell into the cactus below.",
        "application": "Stop bypassing the foundation work. The shortcut IS the long road.",
        "stage_range": [0, 2],
    },
    "Br'er Rabbit": {
        "origin": "African American (Joel Chandler Harris / West African Anansi tradition)",
        "lesson": "Begged not to be thrown in the briar patch — where he lives. Perceived weakness is your greatest strength.",
        "application": "Your constraints are not prison walls. They are your home territory.",
        "stage_range": [3, 5],
    },
    "Anansi": {
        "origin": "West African / Ashanti",
        "lesson": "Tricked the Sky God for ownership of all stories. Narrative frame beats brute force every time.",
        "application": "You don't need more power. You need a better story about the power you have.",
        "stage_range": [6, 7],
    },
    "Loki": {
        "origin": "Norse",
        "lesson": "Cut Sif's hair. Panicked. Accidentally invented Thor's hammer trying to fix it. Chaos is a generative force.",
        "application": "The thing you broke open will become the greatest gift — but only if you stop trying to un-break it.",
        "stage_range": [8, 9],
    },
}

# =============================================================================
# HERMETIC LAWS BY STAGE
# =============================================================================

HERMETIC_LAWS = {
    0: ("Mentalism", "All is mind. Your reset is not emptiness — it is the purest form of potential."),
    1: ("Correspondence", "As above, so below. The small system you are building mirrors the cosmos."),
    2: ("Vibration", "Nothing rests. The boundary you drew is itself vibrating — and will need revision."),
    3: ("Polarity", "Everything has its opposite. Your growth creates its own resistance. Both are needed."),
    4: ("Rhythm", "The pendulum swings. The stability you built will require deliberate instability to grow."),
    5: ("Cause & Effect", "Nothing is chance. This threshold existed before you arrived at it. Your choice now echoes backward and forward."),
    6: ("Gender", "Every mind contains both creative and receptive principles. Your integration is never complete — only deepening."),
    7: ("Vibration", "Higher vibration burns away lower forms. What remains after refinement is your actual architecture."),
    8: ("Mentalism + Rhythm", "As above, so below. The organizational collapse mirrors the internal ego collapse. The pendulum has been held too long — release it now."),
    9: ("Correspondence", "As above, so below. The cycle completing here mirrors a thousand cycles completing simultaneously at other scales."),
}

# =============================================================================
# STAGE-SPECIFIC WISDOM
# =============================================================================

STAGE_WISDOM = {
    0: "The void is not your enemy. It is the womb of your next form.",
    1: "The first act of creation is naming. Name what you are building clearly.",
    2: "A boundary is not a wall — it is a conversation between inside and outside.",
    3: "Creative tension is the engine. Do not resolve it too soon.",
    4: "The foundation is complete when it can hold weight you haven't planned for yet.",
    5: "At the threshold, inaction is itself a choice. The neutral option no longer exists.",
    6: "Integration is not harmony. It is the productive co-existence of tensions that used to cancel each other.",
    7: "Refinement is surgical. You are not cutting away the bad — you are revealing the essential.",
    8: "The trap at Stage 8 is believing you have arrived. Arrival is an illusion. Gratitude for what was built, and release of what was, is the only key.",
    9: "Transformation does not destroy what came before. It harvests it.",
}


# =============================================================================
# WISDOM ENGINE
# =============================================================================

class WisdomEngine:

    @classmethod
    def get_insight(cls, stage: int, trap_active: bool = False) -> Dict[str, Any]:
        stage = max(0, min(9, stage))
        
        # Select trickster by stage range
        trickster_name = "Coyote"
        for name, data in TRICKSTERS.items():
            if data["stage_range"][0] <= stage <= data["stage_range"][1]:
                trickster_name = name
                break
        
        trickster = TRICKSTERS[trickster_name]
        law_name, law_text = HERMETIC_LAWS[stage]
        wisdom = STAGE_WISDOM[stage]
        
        # Override for trap condition
        if trap_active and stage >= 7:
            trickster_name = "Loki"
            trickster = TRICKSTERS["Loki"]
            wisdom = (
                "False permanence is the Stage 8 narcotic. "
                "The system has convinced itself that perfection equals completion. "
                "Only the conscious decision to dissolve what was built — with gratitude, not destruction — "
                "opens the passage to Stage 9."
            )
        
        return {
            "trickster": trickster_name,
            "trickster_origin": trickster["origin"],
            "trickster_lesson": trickster["lesson"],
            "trickster_application": trickster["application"],
            "hermetic_law": law_name,
            "hermetic_text": law_text,
            "stage_wisdom": wisdom,
            "trap_override": trap_active and stage >= 7,
        }
