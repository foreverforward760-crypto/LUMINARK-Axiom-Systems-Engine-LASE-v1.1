from .base import normalize_telemetry

def from_org(conflict: float, volatility: float, resilience: float):
    return normalize_telemetry({"severity": conflict, "turbulence": volatility, "adaptability": resilience})
