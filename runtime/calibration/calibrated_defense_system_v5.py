"""
v5 Probabilistic Defense System
"""

class DefenseSystemV5:
    def analyze(self, probs, entropy, trap_score):

        p7, p8, p9 = probs[7], probs[8], probs[9]

        uncertainty = entropy

        # learned thresholds replaced with probabilistic logic

        if p8 > 0.55 and trap_score > 70:
            return {
                "state": "CRITICAL",
                "action": "INTERVENE",
                "confidence": p8
            }

        if uncertainty > 2.2:
            return {
                "state": "UNCERTAIN",
                "action": "HOLD",
                "confidence": 1.0 - uncertainty / 3.0
            }

        if p9 > 0.6:
            return {
                "state": "STABLE_HIGH_FLOW",
                "action": "ALLOW",
                "confidence": p9
            }

        if p7 > 0.6:
            return {
                "state": "INSTABILITY",
                "action": "DAMPEN",
                "confidence": p7
            }

        return {
            "state": "NORMAL",
            "action": "NONE",
            "confidence": max(probs)
        }
