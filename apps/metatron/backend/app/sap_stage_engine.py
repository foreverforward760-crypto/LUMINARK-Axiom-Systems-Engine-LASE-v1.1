import numpy as np
from typing import Dict, Any


class SAPStageEngine:
    """
    Stanfields Axiom of Perpetuity — maps market data to stages 0-9.

    Inversion Principle:
        Odd  stages → physically unstable, consciously stable
        Even stages → physically stable, consciously unstable
        Stage 0     → both low (void/crash)
        Stage 9     → climax/release (special)
    """

    STAGE_DESCRIPTIONS: Dict[int, str] = {
        0: "PLENARA – Complete reset, post-crash or pre-emergence. Primordial potential.",
        1: "SPARK OF NAVIGATION – First ignition of uptrend, high uncertainty, directional clarity emerging.",
        2: "FORGE OF POLARITY – Consolidation and polarization, forming base, conflicting signals.",
        3: "ENGINE OF EXPRESSION – Breakout attempt, high volume, confident move, first self-reflection.",
        4: "CRUCIBLE OF EQUILIBRIUM – Sustainable trend, healthy pullbacks, maximum complexity threshold.",
        5: "DYNAMO OF WILL – Critical decision point, high tension, volatile. Three-way bifurcation stage.",
        6: "NEXUS OF HARMONY – Peak integration, smooth trend, low volatility, all systems synchronized.",
        7: "LENS OF DISTILLATION – Divergences appear, distribution, deep refinement and analysis.",
        8: "VESSEL OF GROUNDING – Dual-chamber trap: Illusion of Arrival (low adaptability) or "
           "Illusion of Permanence (high tension). 1.45x TrapScore amplifier active.",
        9: "TRANSPARENCY OF THE GUIDE – Climax, dissolution, blow-off or completion. Return to PLENARA.",
    }

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------

    def _physical_stability(self, volatility: float, price_history: list) -> float:
        """
        0 = completely unstable, 1 = rock solid.

        Uses annualised volatility as the primary signal.
        A 50%+ annualised vol maps to 0 stability.
        Trend consistency (monotone run) adds a small bonus.
        """
        vol_score = 1.0 - min(volatility / 50.0, 1.0)

        # Trend consistency bonus (±0.1)
        if len(price_history) >= 3:
            diffs = [price_history[i] - price_history[i - 1] for i in range(1, len(price_history))]
            positive_days = sum(1 for d in diffs if d > 0)
            consistency = positive_days / len(diffs)  # 0..1
            vol_score = vol_score * 0.9 + consistency * 0.1

        return round(float(np.clip(vol_score, 0.0, 1.0)), 4)

    def _conscious_stability(self, sentiment: float, put_call_ratio: float, rsi: float) -> float:
        """
        0 = totally fearful/uncertain, 1 = fully confident/greedy.

        Sentiment: -1..1 → mapped to 0..1
        Put/call  > 1.2  → fear, reduces stability
        RSI       > 70   → overbought greed bonus
        RSI       < 30   → oversold fear penalty
        """
        base = (sentiment + 1.0) / 2.0  # -1..1 → 0..1

        if put_call_ratio > 1.2:
            base *= 0.5  # fear discount
        elif put_call_ratio < 0.7:
            base = base * 0.9 + 0.1  # greed nudge

        # RSI modifier
        if rsi > 70:
            base = min(base + 0.1, 1.0)
        elif rsi < 30:
            base = max(base - 0.1, 0.0)

        return round(float(np.clip(base, 0.0, 1.0)), 4)

    # ---------------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------------

    def compute_stage(self, ticker_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute the SAP stage (0-9) for a single asset.

        Expected keys in ticker_data
        ─────────────────────────────
        price_history   : list[float]  daily close prices (oldest → newest)
        volatility      : float        30-day annualised volatility (%)
        rsi             : float        latest RSI (default 50)
        sentiment_score : float        -1..1  (default 0)
        put_call_ratio  : float        (default 1.0)
        volume_history  : list[float]  optional
        """
        price_history: list = ticker_data.get("price_history", [])
        volatility: float = float(ticker_data.get("volatility", 30))
        rsi: float = float(ticker_data.get("rsi", 50))
        sentiment: float = float(ticker_data.get("sentiment_score", 0))
        pc_ratio: float = float(ticker_data.get("put_call_ratio", 1.0))

        ps = self._physical_stability(volatility, price_history)
        cs = self._conscious_stability(sentiment, pc_ratio, rsi)

        # ── Primary composite (0-10 raw, clamped to 0-9) ──────────────────────
        composite = (ps * 0.6 + cs * 0.4) * 10
        stage = int(round(composite))
        stage = max(0, min(9, stage))

        # ── Inversion correction ───────────────────────────────────────────────
        if ps < 0.5 and cs < 0.5:
            # Both dimensions low → void / crash
            stage = 0

        elif ps > 0.5 and cs > 0.5:
            # Both high → healthy (4) or trap (8)
            if volatility < 15 and sentiment > 0.8:
                stage = 8   # low vol + extreme greed = euphoria trap
            else:
                stage = 4

        elif ps > 0.5 and cs < 0.5:
            # Physically stable, consciously unstable → even stages
            if stage % 2 != 0:
                stage = min(stage + 1, 8)

        elif ps < 0.5 and cs > 0.5:
            # Physically unstable, consciously stable → odd stages
            if stage % 2 == 0:
                stage = min(stage + 1, 9)

        # ── Special climax check (Stage 9) ────────────────────────────────────
        if rsi > 85 and volatility > 60 and sentiment > 0.85:
            stage = 9

        inversion_type = (
            "special" if stage in (0, 9)
            else "odd" if stage % 2 == 1
            else "even"
        )

        return {
            "stage": stage,
            "description": self.STAGE_DESCRIPTIONS.get(stage, ""),
            "physical_stability": ps,
            "conscious_stability": cs,
            "inversion_type": inversion_type,
        }
