"""
luminark/industrial_overlay.py — Industrial Translation Layer (v8.2.1)

Backward-compatible industrial wrappers for Stage 6-8 classifiers.
Translates SAP phenomenological language into industrial/infrastructure terms.
Arc-aware: Descending Arc outputs differ from Ascending Arc outputs.

Stage 6 → Operating Margin (Optimal vs Exhausted)
Stage 7 → Failure Isolation (Contained vs Cascading)
Stage 8 → Resource Recirculation (Dissolution vs Shattering)

Author: Richard L. Stanfield — Meridian Axiom Alignment Technologies (MAAT)
"""

from typing import Dict, Any


def classify_operating_margin(state) -> Dict[str, Any]:
    """
    Industrial wrapper for Stage 6 flow quality.
    Sustainable Flow → Optimal Operating Margin
    Brittle Flow     → Exhausted Safety Margin
    Descending Arc   → Initial Crystallization (hidden brittleness)
    """
    arc_dir = getattr(state, "arc_direction", "indeterminate")
    current_arc = "Descending" if arc_dir in ["descending", "indeterminate"] else "Ascending"

    if current_arc == "Descending":
        return {
            "margin_type": "initial_crystallization",
            "label": "INITIAL CRYSTALLIZATION",
            "directive": (
                "Descending Arc active — high output, hidden brittleness. "
                "System has not yet completed a full cycle. "
                "Monitor divergence between projected stability and actual tension. "
                "Do not mistake initial peak for sustainable operating envelope."
            ),
            "arc": "Descending",
        }

    flow = getattr(state, "flow_analysis", None)
    if flow and isinstance(flow, dict):
        flow_type = flow.get("flow_type", "brittle")
    else:
        flow_type = "brittle"

    if flow_type == "sustainable":
        return {
            "margin_type": "optimal",
            "label": "OPTIMAL OPERATING MARGIN",
            "directive": (
                "System within rated envelope. Conductor Score confirms predictive "
                "monitoring active. Safety margins robust. "
                "Schedule maintenance proactively before harmonic drift emerges."
            ),
            "arc": "Ascending",
            "conductor_score": flow.get("conductor_score", 0) if flow else 0,
        }
    else:
        return {
            "margin_type": "exhausted",
            "label": "EXHAUSTED SAFETY MARGIN",
            "directive": (
                "Safety margin depleted. System has merged with its own performance — "
                "no meta-awareness of load limits. Reduce operational load immediately. "
                "Stage 7 transition (failure isolation) imminent."
            ),
            "arc": current_arc,
            "conductor_score": flow.get("conductor_score", 0) if flow else 0,
        }


def classify_failure_isolation(state) -> Dict[str, Any]:
    """
    Industrial wrapper for Stage 7 crucible mode.
    Conscious Distillation → Contained Failure Isolation
    Chaotic Collapse       → Cascading Failure Risk
    Descending Arc         → Uncontrolled fragmentation (no distillation framework)
    """
    arc_dir = getattr(state, "arc_direction", "indeterminate")
    current_arc = "Descending" if arc_dir in ["descending", "indeterminate"] else "Ascending"

    if current_arc == "Descending":
        return {
            "isolation_mode": "uncontrolled",
            "label": "UNCONTROLLED FRAGMENTATION",
            "directive": (
                "Descending Arc — breakdown is not yet being conducted by consciousness. "
                "No distillation framework established. "
                "Cascade risk elevated. Execute emergency isolation protocol."
            ),
            "arc": "Descending",
            "shadow_surfacing": False,
        }

    crucible = getattr(state, "crucible_analysis", None)
    if crucible and isinstance(crucible, dict):
        mode = crucible.get("crucible_mode", "collapse")
        shadow = crucible.get("shadow_surfacing", False)
    else:
        mode = "collapse"
        shadow = False

    if mode == "distillation":
        return {
            "isolation_mode": "contained",
            "label": "CONTAINED FAILURE ISOLATION",
            "directive": (
                "Failure mode contained to designated subsystem. "
                "Root cause extraction active — the crucible is burning what cannot "
                "survive, not what is essential. Reroute load. Controlled decomposition."
            ),
            "arc": "Ascending",
            "shadow_surfacing": shadow,
            "shadow_note": crucible.get("shadow_note") if crucible else None,
        }
    else:
        return {
            "isolation_mode": "cascading",
            "label": "CASCADING FAILURE RISK",
            "directive": (
                "ALERT: Failure propagating beyond isolated subsystem. "
                "System resistance amplifying fragmentation. "
                "Execute emergency shutdown. Reduce to minimum viable load."
            ),
            "arc": current_arc,
            "shadow_surfacing": shadow,
        }


def classify_resource_recirculation(state) -> Dict[str, Any]:
    """
    Industrial wrapper for Stage 8 crystallization.
    Dissolution  → Graceful Decommission / Energy Recapture
    Shattering   → Emergency Stop / Total Loss Risk
    Descending Arc → Crystallization building; Gratitude Mechanism not yet available
    """
    arc_dir = getattr(state, "arc_direction", "indeterminate")
    current_arc = "Descending" if arc_dir in ["descending", "indeterminate"] else "Ascending"

    if current_arc == "Descending":
        return {
            "recirculation_status": "crystallizing",
            "label": "CRYSTALLIZATION IN PROGRESS",
            "directive": (
                "Descending Arc — maximum density building toward Stage 8 peak. "
                "Ascending Arc required before Gratitude Mechanism becomes available. "
                "Complete Stage 5 Middle Path Gateway to enable dissolution pathway. "
                "Without it, shattering is the probable outcome."
            ),
            "arc": "Descending",
            "trajectory": "shattering_risk",
        }

    crystal = getattr(state, "crystallization_analysis", None)
    if crystal and isinstance(crystal, dict):
        trajectory = crystal.get("trajectory", "shattering")
        divergence = crystal.get("divergence", 5.0)
    else:
        trajectory = "shattering"
        divergence = 5.0

    if trajectory == "dissolution":
        return {
            "recirculation_status": "engaged",
            "label": "GRACEFUL DECOMMISSION",
            "directive": (
                "Gratitude Mechanism engaged. Revealed/Concealed divergence converging. "
                "Controlled decommissioning viable. Energy can be recaptured and "
                "recirculated into next cycle. Proceed with structured wind-down."
            ),
            "arc": "Ascending",
            "trajectory": "dissolution",
            "divergence": divergence,
            "gratitude_engaged": crystal.get("gratitude_engaged", True) if crystal else True,
        }
    else:
        return {
            "recirculation_status": "failed",
            "label": "EMERGENCY STOP — SHATTERING RISK",
            "directive": (
                "CRITICAL: Crystallization Paradox active. Maximum density + maximum brittleness. "
                "Gratitude Mechanism not engaged. Revealed/Concealed divergence critical. "
                f"Divergence score: {divergence:.1f}. Emergency stop required. "
                "Catastrophic structural failure imminent without immediate intervention."
            ),
            "arc": current_arc,
            "trajectory": "shattering",
            "divergence": divergence,
        }
