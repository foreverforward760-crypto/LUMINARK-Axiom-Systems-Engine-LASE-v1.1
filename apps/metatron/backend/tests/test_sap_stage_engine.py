import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app.sap_stage_engine import SAPStageEngine


@pytest.fixture
def engine():
    return SAPStageEngine()


def _base():
    return {
        "price_history": [100, 101, 102, 103, 104],
        "volatility": 20,
        "rsi": 50,
        "sentiment_score": 0.0,
        "put_call_ratio": 1.0,
    }


class TestStageRange:
    def test_stage_is_int(self, engine):
        result = engine.compute_stage(_base())
        assert isinstance(result["stage"], int)

    def test_stage_in_bounds(self, engine):
        result = engine.compute_stage(_base())
        assert 0 <= result["stage"] <= 9

    def test_description_present(self, engine):
        result = engine.compute_stage(_base())
        assert result["description"] != ""


class TestInversionPrinciple:
    def test_crash_stage_zero(self, engine):
        """High volatility + very negative sentiment → Stage 0."""
        data = _base()
        data.update({"volatility": 90, "sentiment_score": -0.9, "rsi": 20, "put_call_ratio": 2.0})
        result = engine.compute_stage(data)
        assert result["stage"] == 0

    def test_euphoria_trap_stage_eight(self, engine):
        """Low volatility + extreme greed → Stage 8 (trap)."""
        data = _base()
        data.update({"volatility": 10, "sentiment_score": 0.9, "rsi": 72, "put_call_ratio": 0.6})
        result = engine.compute_stage(data)
        assert result["stage"] == 8

    def test_climax_stage_nine(self, engine):
        """Extreme RSI + high vol + extreme sentiment → Stage 9."""
        data = _base()
        data.update({"volatility": 65, "sentiment_score": 0.9, "rsi": 90, "put_call_ratio": 0.3})
        result = engine.compute_stage(data)
        assert result["stage"] == 9

    def test_inversion_type_odd(self, engine):
        """Physically unstable + consciously stable → odd stage."""
        data = _base()
        data.update({"volatility": 60, "sentiment_score": 0.8, "rsi": 55, "put_call_ratio": 0.8})
        result = engine.compute_stage(data)
        if result["stage"] not in (0, 9):
            assert result["stage"] % 2 == 1

    def test_inversion_type_even(self, engine):
        """Physically stable + consciously unstable → even stage."""
        data = _base()
        data.update({"volatility": 12, "sentiment_score": -0.5, "rsi": 40, "put_call_ratio": 1.5})
        result = engine.compute_stage(data)
        if result["stage"] not in (0, 9):
            assert result["stage"] % 2 == 0


class TestOutputKeys:
    def test_all_keys_present(self, engine):
        result = engine.compute_stage(_base())
        for key in ("stage", "description", "physical_stability", "conscious_stability", "inversion_type"):
            assert key in result
