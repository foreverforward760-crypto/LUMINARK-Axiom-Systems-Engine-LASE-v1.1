from __future__ import annotations

from luminark_adapters import from_org
from luminark_core import LuminarkEngine


def run_market_analyzer(conflict: float, volatility: float, resilience: float):
    engine = LuminarkEngine()
    telemetry = from_org(conflict, volatility, resilience)
    return engine.analyze(telemetry)
