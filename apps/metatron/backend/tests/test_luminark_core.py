import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app.luminark_core import LuminarkAI


@pytest.fixture
def ai():
    return LuminarkAI()


MOCK_USER_DATA = {
    "holdings": {
        "AAPL": {
            "price_history": [150, 152, 151, 153, 155],
            "volatility": 18,
            "rsi": 65,
            "sentiment_score": 0.6,
            "put_call_ratio": 0.9,
        },
        "GME": {
            "price_history": [20, 22, 19, 25, 30],
            "volatility": 80,
            "rsi": 85,
            "sentiment_score": 0.9,
            "put_call_ratio": 0.4,
        },
    },
    "transactions": [
        {"type": "buy", "ticker": "AAPL", "days_held": 60},
        {"type": "buy", "ticker": "GME", "days_held": 5},
    ],
    "notes": [
        "AAPL is a sure thing, can't go wrong",
        "GME to the moon!",
        "Maybe I should diversify",
    ],
}


class TestAnalyzePortfolio:
    def test_returns_all_keys(self, ai):
        result = ai.analyze_portfolio(MOCK_USER_DATA)
        for key in ("overall_stage", "overall_description", "holdings", "user", "threats", "recommendations"):
            assert key in result

    def test_holdings_length(self, ai):
        result = ai.analyze_portfolio(MOCK_USER_DATA)
        assert len(result["holdings"]) == 2

    def test_overall_stage_in_bounds(self, ai):
        result = ai.analyze_portfolio(MOCK_USER_DATA)
        assert 0 <= result["overall_stage"] <= 9

    def test_threats_not_empty(self, ai):
        """Mock data contains threat-triggering tickers."""
        result = ai.analyze_portfolio(MOCK_USER_DATA)
        assert len(result["threats"]) > 0

    def test_recommendations_list(self, ai):
        result = ai.analyze_portfolio(MOCK_USER_DATA)
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0

    def test_threat_downgrade(self, ai):
        """Critical threats should push overall_stage down."""
        result = ai.analyze_portfolio(MOCK_USER_DATA)
        # With AAPL ransomware (critical), stage should be ≤ 3
        critical = any(t["severity"] == "critical" for t in result["threats"])
        if critical:
            assert result["overall_stage"] <= 3

    def test_empty_portfolio(self, ai):
        result = ai.analyze_portfolio({"holdings": {}, "transactions": [], "notes": []})
        assert result["overall_stage"] == 0
        assert result["holdings"] == []
