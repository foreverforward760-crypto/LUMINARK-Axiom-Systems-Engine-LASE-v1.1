"""
LUMINARK OVERWATCH PRIME — Core Engine v1.0
recurrence.py — Pattern matching against validated failure signatures

PROTECTED MODULE.

The Pattern Recurrence Engine matches the current NSDT vector against the
library of 10 validated historical failure signatures.

This is evidence-based anomaly classification — not black-box ML.
Every match is traceable to a documented real-world event with a known outcome
and a recorded lead time.

When the current system state resembles a known failure precursor, operators
receive not just an alert but a historical context: "This signature resembles
what we saw 9 hours before Hurricane Ian's peak outage."

Match threshold: 0.25 (Euclidean distance in 5D normalized space)
Conservative: only report a match when the vector is genuinely similar.
"""
import math
import json
from pathlib import Path
from typing import Optional, List
from .schemas import NSDTVector, FailureSignature


def _load_signatures() -> List[dict]:
    """Load validated events from data file."""
    data_path = Path(__file__).parent.parent.parent / "data" / "validated_events.json"
    if not data_path.exists():
        return []
    with open(data_path) as f:
        return json.load(f)


# Load at module import — validated events are static reference data
_VALIDATED_EVENTS = _load_signatures()

# Pre-grouped by failure signature type for pattern library
FAILURE_SIGNATURES: dict[str, List[float]] = {
    "WINTER_FREEZE_OFF":        [0.85, 0.20, 0.90, 0.30, 0.60],
    "HURRICANE_INFRASTRUCTURE": [0.88, 0.17, 0.84, 0.20, 0.48],
    "HEAT_WAVE_DEMAND_SPIKE":   [0.53, 0.33, 0.88, 0.48, 0.85],
    "FUEL_SUPPLY_CONSTRAINT":   [0.45, 0.35, 0.90, 0.30, 0.88],
}

# Map signature types to their example events
SIGNATURE_EXAMPLES: dict[str, List[str]] = {
    "WINTER_FREEZE_OFF":        ["Texas Uri 2021", "SPP Feb 2021", "Elliott Dec 2022"],
    "HURRICANE_INFRASTRUCTURE": ["Hurricane Ian 2022", "Hurricane Laura 2020", "Hurricane Helene 2024", "Hurricane Milton 2024"],
    "HEAT_WAVE_DEMAND_SPIKE":   ["California Heat Wave 2020", "Pacific Northwest Heat Dome 2021"],
    "FUEL_SUPPLY_CONSTRAINT":   ["New England Bomb Cyclone 2018"],
}

MATCH_THRESHOLD = 0.25


def _euclidean(a: List[float], b: List[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def match_pattern(vec: NSDTVector, threshold: float = MATCH_THRESHOLD) -> Optional[FailureSignature]:
    """
    Match the current NSDT vector against the validated failure signature library.

    Args:
        vec:       Current NSDT vector
        threshold: Maximum Euclidean distance to report a match (default 0.25)

    Returns:
        FailureSignature if a match is found within threshold, else None
    """
    v = vec.as_list()
    best_name: Optional[str] = None
    best_distance = float("inf")

    for sig_name, centroid in FAILURE_SIGNATURES.items():
        dist = _euclidean(v, centroid)
        if dist < best_distance:
            best_distance = dist
            best_name = sig_name

    if best_distance <= threshold and best_name:
        return FailureSignature(
            name=best_name,
            pattern=FAILURE_SIGNATURES[best_name],
            example_events=SIGNATURE_EXAMPLES.get(best_name, []),
            distance=round(best_distance, 4),
        )

    return None


def recommended_action_from_signature(signature: Optional[FailureSignature], alert_level: int) -> str:
    """
    Generate a specific recommended action based on matched failure signature
    and alert level.
    """
    if alert_level == 1:
        return "Continue normal operations. Monitor at standard interval."

    if signature is None:
        actions = {
            2: "Inspect system within 30 days. Review recent operational logs.",
            3: "Schedule maintenance within 7 days. Notify on-call operations team.",
            4: "Immediate operator review required. Prepare emergency response protocols.",
            5: "Initiate full containment protocol. Emergency shutdown authorized.",
        }
        return actions.get(alert_level, "Escalate to operations supervisor.")

    sig_actions = {
        "WINTER_FREEZE_OFF": {
            2: "Review generator weatherization status. Pre-position backup fuel.",
            3: "Issue cold-weather advisory. Pre-dispatch maintenance to vulnerable units.",
            4: "Activate winter storm emergency protocol. Pre-position mutual aid crews.",
            5: "Implement emergency load shedding. Contact neighboring BAs for imports now.",
        },
        "HURRICANE_INFRASTRUCTURE": {
            2: "Review hurricane preparedness. Identify coastal generation exposure.",
            3: "Pre-stage mutual aid crews. Notify critical facilities to test backup generation.",
            4: "Pre-dispatch crews to staging areas. Activate standby generation at critical sites.",
            5: "Execute hurricane response protocol. Begin controlled load reduction now.",
        },
        "HEAT_WAVE_DEMAND_SPIKE": {
            2: "Activate voluntary conservation messaging. Review import availability.",
            3: "Issue demand response notifications. Pre-negotiate emergency imports.",
            4: "Activate mandatory conservation. Emergency import purchases now.",
            5: "Execute rolling blackout protocol. Prioritize critical load immediately.",
        },
        "FUEL_SUPPLY_CONSTRAINT": {
            2: "Verify fuel inventory levels. Review backup fuel contracts.",
            3: "Pre-purchase backup fuel. Notify oil-capable generators to prepare.",
            4: "Activate fuel emergency protocol. Switch generation fleet to backup fuels now.",
            5: "Implement emergency load shedding. Contact grid operator for emergency dispatch.",
        },
    }

    return sig_actions.get(signature.name, {}).get(
        alert_level,
        "Escalate to operations supervisor immediately."
    )
