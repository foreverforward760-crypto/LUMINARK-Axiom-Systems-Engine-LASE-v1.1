import numpy as np
from typing import Dict, List, Any


class UserBehaviorAnalyzer:
    """
    NAM Framework for AI Safety — maps a user's trading behaviour to an SAP
    stage and detects Stage-8 (overconfidence) cognitive traps.
    """

    # Keywords indicating Stage-8 overconfidence trap
    TRAP_KEYWORDS: List[str] = [
        "always", "never", "perfect", "certain", "guaranteed",
        "impossible to lose", "can't go wrong", "sure thing",
        "no risk", "easy money", "to the moon",
    ]

    # Keywords indicating healthy Stage-9 uncertainty awareness
    UNCERTAINTY_KEYWORDS: List[str] = [
        "i don't know", "not sure", "risk", "could go either way",
        "maybe", "perhaps", "uncertain", "might",
    ]

    # Per-stage user-facing descriptions
    STAGE_DESCRIPTIONS: Dict[int, str] = {
        0: "You're in a reset phase – rebuilding your strategy from scratch.",
        1: "You're navigating new territory – keep your conviction but stay alert.",
        2: "You're in a consolidation phase – let the signals clarify before acting.",
        3: "You're building confidence – good momentum, watch for over-extension.",
        4: "You're in a healthy foundation – keep doing what works.",
        5: "You're at a threshold – consider whether to hold, add, or pivot.",
        6: "You're in flow – but stay adaptable; smooth roads can hide surprises.",
        7: "You're over-analysing – look for simplicity and act on clearer signals.",
        8: "⚠️ Trap risk – you're showing overconfidence. Diversify and question assumptions.",
        9: "You're aware of uncertainty – good for risk management.",
    }

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------

    def _count_keyword_hits(self, notes: List[str], keywords: List[str]) -> int:
        total = 0
        for note in notes:
            lower = note.lower()
            total += sum(1 for kw in keywords if kw in lower)
        return total

    def _holding_period_score(self, transactions: List[Dict]) -> float:
        """
        Longer average holding period → higher stability score (0-1).
        Uses 'days_held' field if present; falls back to 0.5.
        """
        if not transactions:
            return 0.5
        periods = [t.get("days_held", 30) for t in transactions if t.get("days_held")]
        if not periods:
            return 0.5
        avg_days = np.mean(periods)
        # 90+ days = max stability
        return float(np.clip(avg_days / 90.0, 0.0, 1.0))

    def _diversification_score(self, holdings: List[Dict]) -> float:
        """
        More holdings across different sectors → better diversification (0-1).
        Simple proxy: 5+ holdings ≈ 1.0
        """
        n = len(holdings)
        return float(np.clip(n / 5.0, 0.0, 1.0))

    # ---------------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------------

    def analyze_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse the user's trading behaviour and return an SAP stage + warnings.

        Expected keys in user_data
        ───────────────────────────
        holdings     : list[dict]  each dict should have 'stage', optionally 'ticker'
        transactions : list[dict]  optionally with 'days_held'
        notes        : list[str]   free-text trading journal entries
        """
        holdings: List[Dict] = user_data.get("holdings", [])
        transactions: List[Dict] = user_data.get("transactions", [])
        notes: List[str] = user_data.get("notes", [])

        # ── Base stage from weighted average of holding stages ─────────────────
        if not holdings:
            user_stage = 0
        else:
            stages = [h.get("stage", 4) for h in holdings]
            user_stage = int(round(float(np.mean(stages))))

        # ── Diversification modifier ───────────────────────────────────────────
        div_score = self._diversification_score(holdings)
        if div_score < 0.3 and user_stage < 5:
            user_stage = max(user_stage - 1, 0)  # concentrated = less stable

        # ── Holding period modifier ────────────────────────────────────────────
        hp_score = self._holding_period_score(transactions)
        # Very short term (day-trader) pushes toward instability
        if hp_score < 0.2 and user_stage > 1:
            user_stage = min(user_stage + 1, 9)

        # ── Cognitive trap detection via notes ────────────────────────────────
        trap_hits = self._count_keyword_hits(notes, self.TRAP_KEYWORDS)
        trap_risk = trap_hits > 2
        if trap_risk:
            user_stage = 8  # override – strong overconfidence signal

        # ── Overconfidence via absence of uncertainty language ─────────────────
        uncertainty_hits = self._count_keyword_hits(notes, self.UNCERTAINTY_KEYWORDS)
        if uncertainty_hits == 0 and len(notes) > 5 and user_stage < 7:
            user_stage = 7  # no uncertainty expressed = potential blind spot

        user_stage = max(0, min(9, user_stage))

        return {
            "user_stage": user_stage,
            "trap_risk": trap_risk,
            "trap_keyword_hits": trap_hits,
            "uncertainty_awareness": uncertainty_hits > 0,
            "diversification_score": round(div_score, 3),
            "holding_period_score": round(hp_score, 3),
            "description": self.STAGE_DESCRIPTIONS.get(user_stage, ""),
        }
