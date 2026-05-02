import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app.user_behavior import UserBehaviorAnalyzer


@pytest.fixture
def analyzer():
    return UserBehaviorAnalyzer()


def _base_user():
    return {
        "holdings": [{"ticker": "AAPL", "stage": 4}, {"ticker": "MSFT", "stage": 3}],
        "transactions": [{"type": "buy", "ticker": "AAPL", "days_held": 45}],
        "notes": ["Looks interesting", "Maybe I should diversify a bit"],
    }


class TestTrapDetection:
    def test_trap_risk_flagged(self, analyzer):
        user = _base_user()
        user["notes"] = [
            "This is a sure thing",
            "Can't go wrong with AAPL",
            "Guaranteed returns",
            "I always win",
        ]
        result = analyzer.analyze_user(user)
        assert result["trap_risk"] is True
        assert result["user_stage"] == 8

    def test_no_trap_normal_notes(self, analyzer):
        result = analyzer.analyze_user(_base_user())
        assert result["trap_risk"] is False

    def test_uncertainty_awareness(self, analyzer):
        user = _base_user()
        user["notes"] = ["I'm not sure about GME", "risk seems high"]
        result = analyzer.analyze_user(user)
        assert result["uncertainty_awareness"] is True

    def test_overconfidence_from_silence(self, analyzer):
        """No uncertainty keywords in >5 notes → stage bumped to at least 7."""
        user = _base_user()
        user["notes"] = ["buy more", "hold", "strong", "great", "excellent", "moon"]
        result = analyzer.analyze_user(user)
        assert result["user_stage"] >= 7


class TestOutputKeys:
    def test_all_keys_present(self, analyzer):
        result = analyzer.analyze_user(_base_user())
        for key in (
            "user_stage", "trap_risk", "trap_keyword_hits",
            "uncertainty_awareness", "diversification_score",
            "holding_period_score", "description",
        ):
            assert key in result

    def test_stage_in_bounds(self, analyzer):
        result = analyzer.analyze_user(_base_user())
        assert 0 <= result["user_stage"] <= 9
