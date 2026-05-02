from .base import normalize_telemetry

def from_network(loss: float, latency_jitter: float, reroute_capacity: float):
    return normalize_telemetry({"severity": loss, "turbulence": latency_jitter, "adaptability": reroute_capacity})
