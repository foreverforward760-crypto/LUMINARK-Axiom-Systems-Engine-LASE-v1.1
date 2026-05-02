from .base import normalize_telemetry

def from_hvac(thermal_stress: float, pressure_noise: float, control_headroom: float):
    return normalize_telemetry({"severity": thermal_stress, "turbulence": pressure_noise, "adaptability": control_headroom})
