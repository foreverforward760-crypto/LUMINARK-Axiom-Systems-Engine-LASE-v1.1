"""
luminark/stage_descriptions.py  –  Industrial stage descriptions and themes.

Provides canonical descriptions for SAP Stages 6-8 with industrial interpretations,
maintaining clean separation from KAIROS consciousness model terminology.

These descriptions are used by the InversionAnalyzer classifiers and UI guidance systems.
"""

from typing import Dict, Any

# Industrial-friendly stage descriptions for Stages 6-8
# These replace anthropomorphic language with deterministic system diagnostics
STAGE_DESCRIPTIONS: Dict[int, Dict[str, str]] = {
    6: {
        "name": "NEXUS OF HARMONY",
        "industrial_theme": "Safety Margin Utilization",
        "description": (
            "Peak operational efficiency. All subsystems synchronized and responsive. "
            "Apparent stability, but hidden destabilization begins. The system appears to have "
            "unlimited capacity, masking the onset of fatigue."
        ),
        "directive": "Maintain the Safety Margin. Do not exceed optimal load.",
        "mechanism": "classify_operating_margin",
    },
    7: {
        "name": "LENS OF DISTILLATION",
        "industrial_theme": "Failure Isolation / Component Stress-Testing",
        "description": (
            "Breakdown is being conducted by the monitoring system, not happening to it. "
            "Faults are isolated and contained. The system is actively stress-testing itself "
            "to identify and compartmentalize defects before cascade."
        ),
        "directive": "Contain the failure. Reroute around the affected component.",
        "mechanism": "classify_failure_isolation",
    },
    8: {
        "name": "VESSEL OF GROUNDING",
        "industrial_theme": "Crystallization & Resource Recirculation",
        "description": (
            "Maximum structural integrity equals maximum brittleness. The system has consolidated "
            "all resources into a rigid configuration. It must now decide: dissolve (controlled "
            "decommissioning with energy recovery) or shatter (catastrophic failure with total loss)."
        ),
        "directive": "Engage Resource Recirculation. Acknowledge wear and return energy to the pool.",
        "mechanism": "classify_resource_recirculation",
    },
}

# Mapping of stage to industrial classifier method names
STAGE_CLASSIFIERS: Dict[int, str] = {
    6: "classify_operating_margin",
    7: "classify_failure_isolation",
    8: "classify_resource_recirculation",
}

# Industrial risk levels based on classifier outputs
RISK_MAPPING: Dict[str, Dict[str, str]] = {
    # Stage 6 Operating Margin
    "operating_margin:sustainable": {"risk": "LOW", "alert_color": "GREEN"},
    "operating_margin:nominal": {"risk": "MEDIUM", "alert_color": "YELLOW"},
    "operating_margin:brittle": {"risk": "HIGH", "alert_color": "RED"},
    
    # Stage 7 Failure Isolation
    "failure_isolation:distillation": {"risk": "MEDIUM", "alert_color": "YELLOW"},
    "failure_isolation:degraded": {"risk": "HIGH", "alert_color": "ORANGE"},
    "failure_isolation:collapse": {"risk": "CRITICAL", "alert_color": "RED"},
    
    # Stage 8 Resource Recirculation
    "resource_recirculation:dissolution": {"risk": "MEDIUM", "alert_color": "YELLOW"},
    "resource_recirculation:uncertain": {"risk": "MEDIUM", "alert_color": "YELLOW"},
    "resource_recirculation:shattering": {"risk": "CRITICAL", "alert_color": "RED"},
}

def get_stage_description(stage: int) -> Dict[str, str]:
    """
    Retrieve the industrial description for a given SAP stage.
    
    Args:
        stage: SAP stage number (0-9)
    
    Returns:
        Dictionary with keys: name, industrial_theme, description, directive, mechanism
        Returns empty dict if stage is not 6-8.
    """
    return STAGE_DESCRIPTIONS.get(stage, {})

def get_classifier_method(stage: int) -> str:
    """
    Get the classifier method name for a given stage.
    
    Args:
        stage: SAP stage number
    
    Returns:
        Method name as string (e.g., "classify_operating_margin")
        Returns empty string if stage has no classifier.
    """
    return STAGE_CLASSIFIERS.get(stage, "")

def get_risk_level(classifier_result: str) -> Dict[str, str]:
    """
    Map a classifier result to risk level and alert color.
    
    Args:
        classifier_result: String in format "classifier_type:result_value"
                          e.g., "operating_margin:brittle"
    
    Returns:
        Dictionary with keys: risk, alert_color
        Returns {"risk": "UNKNOWN", "alert_color": "GRAY"} if not found.
    """
    return RISK_MAPPING.get(classifier_result, {"risk": "UNKNOWN", "alert_color": "GRAY"})
