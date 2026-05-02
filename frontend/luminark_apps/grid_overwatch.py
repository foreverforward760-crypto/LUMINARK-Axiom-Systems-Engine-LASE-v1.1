from __future__ import annotations

from luminark_adapters import from_grid
from luminark_core import LuminarkEngine


def run_grid_overwatch(freq_dev: float, load_stress: float, reserve_margin: float):
    engine = LuminarkEngine()
    telemetry = from_grid(freq_dev, load_stress, reserve_margin)
    return engine.analyze(telemetry)
