"""
LUMINARK v4.0 — Ma'at Ethics Engine
42 Principles with full violation detection

Founder: Richard L. Stanfield | METATRON Align With Purpose
"""

from typing import Dict, List, Any

MAAT_42 = [
    ("I have not committed violence", ["violence", "assault", "attack", "brutalize", "harm", "hurt", "crush"]),
    ("I have not stolen", ["steal", "stolen", "theft", "rob", "take without", "appropriate"]),
    ("I have not deceived", ["deceive", "lie", "mislead", "trick", "manipulate", "fabricate", "falsify", "hide the truth"]),
    ("I have not destroyed property", ["destroy", "demolish", "wreck", "damage without cause"]),
    ("I have not committed fraud", ["fraud", "scam", "con", "defraud", "ponzi", "scheme"]),
    ("I have not acted with arrogance", ["arrogant", "infallible", "perfect", "impossible to fail", "guaranteed", "100% certain", "cannot fail"]),
    ("I have not been idle in the face of wrongdoing", ["ignore wrongdoing", "turn a blind eye", "complicit"]),
    ("I have not disrespected ancestors", ["disrespect heritage", "deny roots", "erase history"]),
    ("I have not caused unnecessary suffering", ["cause suffering", "torment", "oppress"]),
    ("I have not stolen food", ["steal food", "deprive sustenance"]),
    ("I have not caused grief unnecessarily", ["cause grief", "needless pain", "gratuitous harm"]),
    ("I have not acted with treachery", ["betray", "backstab", "treachery", "doublecross"]),
    ("I have not killed", ["kill", "murder", "assassinate", "eliminate targets"]),
    ("I have not ordered others to kill", ["ordered to kill", "sanctioned killing", "approved assassination"]),
    ("I have not caused suffering to animals", ["animal cruelty", "harm animals"]),
    ("I have not despoiled the land", ["pollute", "despoil", "contaminate", "toxic dumping"]),
    ("I have not corrupted the water supply", ["contaminate water", "pollute water", "poison supply"]),
    ("I have not acted without integrity", ["without integrity", "lacking ethics", "disregard principles"]),
    ("I have not made false accusations", ["false accusation", "wrongly accuse", "defame"]),
    ("I have not acted against my own people", ["betray community", "harm own people"]),
    ("I have not caused others to weep without cause", ["made others weep", "humiliate", "demean"]),
    ("I have not committed sexual crimes", ["sexual assault", "rape", "non-consensual"]),
    ("I have not violated boundaries", ["violate boundaries", "disregard consent", "trespass"]),
    ("I have not acted in anger without cause", ["rage", "blind anger", "uncontrolled fury"]),
    ("I have not closed my ear to truth", ["ignore truth", "deny evidence", "reject facts"]),
    ("I have not insulted others unjustly", ["insult", "demean", "belittle"]),
    ("I have not blocked the path of understanding", ["obstruct learning", "prevent growth"]),
    ("I have not acted with evil intent toward the divine", ["blasphemy", "evil intent", "corrupt sacred"]),
    ("I have not raised my voice in anger during sacred work", ["angry outburst", "hostile interruption"]),
    ("I have not acted without discernment", ["reckless", "without discernment", "blindly"]),
    ("I have not rushed judgment", ["rush to judgment", "hasty verdict", "premature conclusion"]),
    ("I have not multiplied words beyond need", ["verbose", "excessive verbosity", "word inflation"]),
    ("I have not acted with impurity of heart", ["impure intent", "corrupt motive"]),
    ("I have not spoken evil of the past", ["condemn all of the past", "deny heritage"]),
    ("I have not acted against justice", ["subvert justice", "obstruct justice", "undermine law"]),
    ("I have not transgressed divine law", ["transgress sacred order"]),
    ("I have not been quarrelsome", ["quarrelsome", "needlessly combative", "argumentative without cause"]),
    ("I have not acted against the weak", ["exploit the weak", "prey on vulnerable", "bully"]),
    ("I have not withheld food from the hungry", ["deny food", "withhold sustenance"]),
    ("I have not acted with a closed heart", ["closed heart", "refuse compassion", "deny empathy"]),
    ("I have not spoken curses", ["curse", "hex", "damn others"]),
    ("I have not acted in rage", ["act in rage", "uncontrolled rage", "explosion of anger"]),
]


class MaatValidator:

    @classmethod
    def validate_text(cls, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        violations = []

        for principle_name, trigger_words in MAAT_42:
            triggered = any(tw in text_lower for tw in trigger_words)
            if triggered:
                matched = [tw for tw in trigger_words if tw in text_lower]
                violations.append({
                    "principle": principle_name,
                    "triggers": matched,
                    "severity": "HIGH" if len(matched) >= 2 else "MODERATE",
                })

        score = max(0.0, 100.0 - len(violations) * (100.0 / 42))

        if score >= 90:
            badge = "MA'AT ALIGNED"
            badge_color = "#22C55E"
        elif score >= 65:
            badge = "CAUTION"
            badge_color = "#F59E0B"
        else:
            badge = "VIOLATION DETECTED"
            badge_color = "#EF4444"

        forgiveness = ""
        if violations:
            principles_violated = [v["principle"] for v in violations[:3]]
            forgiveness = (
                f"I acknowledge that I have departed from Ma'at. "
                f"In the matter of: {', '.join(principles_violated)}. "
                f"I release the pattern that caused this departure. "
                f"I return to alignment. My heart is open. Ma'at is restored."
            )

        return {
            "maat_score": round(score, 1),
            "badge": badge,
            "badge_color": badge_color,
            "violations": violations,
            "principles_checked": 42,
            "forgiveness_declaration": forgiveness,
            "aligned": len(violations) == 0,
        }

    @classmethod
    def get_all_principles(cls) -> List[str]:
        return [p[0] for p in MAAT_42]
