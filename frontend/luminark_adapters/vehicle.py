from .base import normalize_telemetry

def from_vehicle(brake_risk: float, control_jitter: float, redundancy: float):
    return normalize_telemetry({"severity": brake_risk, "turbulence": control_jitter, "adaptability": redundancy})
