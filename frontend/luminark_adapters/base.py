from __future__ import annotations

from typing import Dict


def normalize_telemetry(raw: Dict[str, float]) -> Dict[str, float]:
    return {
        "severity": float(max(0, min(10, raw.get("severity", 0)))),
        "turbulence": float(max(0, min(10, raw.get("turbulence", 0)))),
        "adaptability": float(max(0, min(10, raw.get("adaptability", 0)))),
    }
