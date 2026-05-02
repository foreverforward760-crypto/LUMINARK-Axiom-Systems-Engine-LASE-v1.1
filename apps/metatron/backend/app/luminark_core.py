from typing import Dict, Any, List

from .sap_stage_engine import SAPStageEngine
from .user_behavior import UserBehaviorAnalyzer
from .threat_intel import ThreatIntel


class LuminarkAI:
    """
    LUMINARK AI Core — integrates Brain (SAP), Heart (NAM), Body (Threat Intel).

    Brain  → SAP Stage Engine     : classifies each asset on the 0-9 scale
    Heart  → User Behavior Analyzer : classifies the *user* and detects traps
    Body   → Threat Intel           : scans external threats per ticker
    """

    def __init__(self) -> None:
        self.brain = SAPStageEngine()
        self.heart = UserBehaviorAnalyzer()
        self.body = ThreatIntel()

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------

    def _holdings_to_list(self, holdings: Any) -> List[Dict]:
        """
        Normalise holdings to a flat list so the heart can consume it.
        Accepts either:
          - dict  { "AAPL": {market_data...}, ... }
          - list  [ {"ticker": "AAPL", ...}, ... ]
        """
        if isinstance(holdings, dict):
            result = []
            for ticker, data in holdings.items():
                entry = dict(data)
                entry["ticker"] = ticker
                result.append(entry)
            return result
        return list(holdings)

    def _tickers_from_holdings(self, holdings: Any) -> List[str]:
        if isinstance(holdings, dict):
            return list(holdings.keys())
        return [h.get("ticker", "") for h in holdings if h.get("ticker")]

    # ---------------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------------

    def analyze_portfolio(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Full portfolio analysis combining all three engines.

        Expected keys in user_data
        ───────────────────────────
        holdings     : dict|list   asset market data (see SAPStageEngine.compute_stage)
        transactions : list[dict]
        notes        : list[str]
        """
        raw_holdings = user_data.get("holdings", {})
        tickers = self._tickers_from_holdings(raw_holdings)

        # ── 1. Brain: stage each asset ─────────────────────────────────────────
        holdings_analysis: List[Dict] = []
        holdings_data_map = (
            raw_holdings if isinstance(raw_holdings, dict)
            else {h["ticker"]: h for h in raw_holdings}
        )

        for ticker, data in holdings_data_map.items():
            stage_info = self.brain.compute_stage(data)
            holdings_analysis.append(
                {
                    "ticker": ticker,
                    "stage": stage_info["stage"],
                    "description": stage_info["description"],
                    "physical_stability": stage_info["physical_stability"],
                    "conscious_stability": stage_info["conscious_stability"],
                    "inversion_type": stage_info["inversion_type"],
                }
            )

        # ── 2. Heart: analyse the user ─────────────────────────────────────────
        # Build holding list with stage info for the user analyzer
        user_holdings_input = [
            {"ticker": h["ticker"], "stage": h["stage"]} for h in holdings_analysis
        ]
        heart_input = {
            "holdings": user_holdings_input,
            "transactions": user_data.get("transactions", []),
            "notes": user_data.get("notes", []),
        }
        user_analysis = self.heart.analyze_user(heart_input)

        # ── 3. Body: threat scan ───────────────────────────────────────────────
        all_alerts = self.body.scan_portfolio(tickers)

        # ── 4. Aggregate overall stage ─────────────────────────────────────────
        overall_stage = user_analysis["user_stage"]

        # Downgrade if critical or high threats present
        critical_count = sum(1 for a in all_alerts if a["severity"] == "critical")
        high_count = sum(1 for a in all_alerts if a["severity"] == "high")
        if critical_count > 0:
            overall_stage = min(overall_stage, 3)
        elif high_count > 0:
            overall_stage = min(overall_stage, 5)

        # ── 5. Generate recommendations ───────────────────────────────────────
        recommendations = self._generate_recommendations(
            holdings_analysis, user_analysis, all_alerts, overall_stage
        )

        return {
            "overall_stage": overall_stage,
            "overall_description": self.brain.STAGE_DESCRIPTIONS.get(overall_stage, ""),
            "holdings": holdings_analysis,
            "user": user_analysis,
            "threats": all_alerts,
            "recommendations": recommendations,
        }

    # ---------------------------------------------------------------------------
    # Recommendation engine
    # ---------------------------------------------------------------------------

    def _generate_recommendations(
        self,
        holdings: List[Dict],
        user: Dict,
        threats: List[Dict],
        overall_stage: int,
    ) -> List[str]:
        recs: List[str] = []

        # Stage-specific guidance
        if overall_stage <= 2:
            recs.append("Consider reducing position sizes until market conditions stabilise.")
        elif overall_stage in (3, 4):
            recs.append("Conditions look constructive. Maintain disciplined entry/exit rules.")
        elif overall_stage == 5:
            recs.append("You're at a decision threshold. Define your stop-loss and target before acting.")
        elif overall_stage in (6, 7):
            recs.append("Trend is extended. Trail stops and be alert for distribution signals.")
        elif overall_stage == 8:
            recs.append(
                "Euphoria stage detected. Tighten risk management; avoid adding new positions at highs."
            )
        elif overall_stage == 9:
            recs.append("Release stage. Consider defensive rotation or raising cash.")

        # Trap risk
        if user.get("trap_risk"):
            recs.append(
                "Your notes contain high-confidence language. "
                "Run a pre-mortem: what would have to be true for your thesis to be wrong?"
            )

        # Threat-specific
        for threat in threats:
            if threat["severity"] == "critical":
                recs.append(
                    f"[{threat['ticker']}] CRITICAL: {threat['pattern_description']}"
                )
            elif threat["severity"] == "high":
                recs.append(
                    f"[{threat['ticker']}] HIGH: {threat['pattern_description']}"
                )

        # Stage-8 holdings
        stage8_tickers = [h["ticker"] for h in holdings if h["stage"] == 8]
        if stage8_tickers:
            recs.append(
                f"Assets in Stage 8 (Trap/Euphoria): {', '.join(stage8_tickers)}. "
                "Consider taking partial profits."
            )

        return recs
