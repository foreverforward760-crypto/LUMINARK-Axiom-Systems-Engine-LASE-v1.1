"""
LUMINARK OVERWATCH PRIME — Core Engine v1.0
alerts.py — Alert level generation

PROTECTED MODULE.

The Alert Engine is the final output stage of LUMINARK's core pipeline.
It maps TrapScore, Stage, Trajectory, and Yunus trigger to one of five
OVERWATCH alert levels with human-readable messages.

Alert Levels:
  5 QUARANTINE          — TrapScore > 0.80 OR Stage <= 0  — Full containment
  4 HARROWING           — TrapScore > 0.60 OR Stage <= 1  — Immediate action
  3 MYCELIAL CONTAINMENT— TrapScore > 0.40 OR Stage <= 2  — 7-day maintenance
  2 OCTO-CAMOUFLAGE     — TrapScore > 0.20 OR Stage <= 3  — 30-day inspection
  1 NOMINAL             — All else                        — Normal operations

The OVERWATCH names are the branded output layer.
The numeric levels are the technical layer.
Both are valid outputs. The numeric levels should be used in API responses
and technical systems. The names appear in dashboards and operator interfaces.
"""
from .schemas import NSDTVector, AlertResult


ALERT_DEFINITIONS = {
    5: {
        "name":    "QUARANTINE",
        "color":   "RED",
        "message": "MAXIMUM SEVERITY — Full containment protocol. Immediate shutdown authorized.",
    },
    4: {
        "name":    "HARROWING",
        "color":   "RED",
        "message": "CRITICAL — Immediate operator action required. System in severe distress.",
    },
    3: {
        "name":    "MYCELIAL CONTAINMENT",
        "color":   "ORANGE",
        "message": "WARNING — Contained fault spreading. Maintenance required within 7 days.",
    },
    2: {
        "name":    "OCTO-CAMOUFLAGE",
        "color":   "YELLOW",
        "message": "ADVISORY — System masking emerging issue. Inspect within 30 days.",
    },
    1: {
        "name":    "NOMINAL",
        "color":   "GREEN",
        "message": "All systems within expected parameters. Continue normal monitoring.",
    },
}


def generate_alert(
    stage:         int,
    trapscore:     float,
    trajectory:    str,
    yunus_trigger: bool = False,
) -> AlertResult:
    """
    Generate OVERWATCH alert level from stage, trapscore, and trajectory.

    Primary driver: TrapScore thresholds
    Secondary modifiers: Stage, Trajectory, Yunus trigger

    Args:
        stage:         Classified health stage (0–9)
        trapscore:     Failure trajectory risk score (0.0–1.0)
        trajectory:    Trajectory state string
        yunus_trigger: Whether Yunus sustained-rigidity pattern is active

    Returns:
        AlertResult with level, name, color, message, and fired flag
    """
    # Primary classification by TrapScore
    if trapscore > 0.80 or stage == 0:
        level = 5
    elif trapscore > 0.60 or stage <= 1:
        level = 4
    elif trapscore > 0.40 or stage <= 2:
        level = 3
    elif trapscore > 0.20 or stage <= 3:
        level = 2
    else:
        level = 1

    # Modifier: ASCENDING trajectory upgrades alert by 1 if already elevated
    if trajectory == "ASCENDING" and level >= 2:
        level = min(5, level + 1)

    # Modifier: Yunus sustained-rigidity trigger — escalate to minimum HARROWING
    if yunus_trigger:
        level = max(level, 4)

    defn = ALERT_DEFINITIONS[level]

    # Augment message for trajectory
    message = defn["message"]
    if trajectory == "ASCENDING" and level >= 3:
        message += " ASCENDING TRAJECTORY — deterioration accelerating."
    elif trajectory == "OSCILLATING":
        message += " OSCILLATING — system unstable, outcome uncertain."
    if yunus_trigger:
        message += " YUNUS PROTOCOL ACTIVE — sustained rigidity trap detected."

    return AlertResult(
        level=level,
        name=defn["name"],
        color=defn["color"],
        message=message,
        fired=(level >= 2),
    )
