from .base import normalize_telemetry

def from_grid(freq_dev: float, load_stress: float, reserve_margin: float):
    return normalize_telemetry({"severity": freq_dev, "turbulence": load_stress, "adaptability": reserve_margin})
