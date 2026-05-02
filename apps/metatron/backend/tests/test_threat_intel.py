import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app.threat_intel import ThreatIntel


@pytest.fixture
def intel():
    return ThreatIntel()


class TestScanAsset:
    def test_gme_pump_dump(self, intel):
        alerts = intel.scan_asset("GME")
        types = [a["threat_type"] for a in alerts]
        assert "pump_dump" in types

    def test_aapl_threats(self, intel):
        alerts = intel.scan_asset("AAPL")
        types = [a["threat_type"] for a in alerts]
        assert "deepfake" in types or "ransomware" in types

    def test_ticker_in_alert(self, intel):
        alerts = intel.scan_asset("GME")
        for a in alerts:
            assert a["ticker"] == "GME"

    def test_severity_values(self, intel):
        alerts = intel.scan_asset("AAPL")
        valid = {"critical", "high", "medium", "low"}
        for a in alerts:
            assert a["severity"] in valid

    def test_no_duplicate_threat_types(self, intel):
        alerts = intel.scan_asset("GME")
        types = [a["threat_type"] for a in alerts]
        assert len(types) == len(set(types))


class TestScanPortfolio:
    def test_multiple_tickers(self, intel):
        alerts = intel.scan_portfolio(["AAPL", "GME"])
        tickers = {a["ticker"] for a in alerts}
        assert len(tickers) > 0

    def test_empty_portfolio(self, intel):
        assert intel.scan_portfolio([]) == []
