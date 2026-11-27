"""
sap_signal_translator.py
────────────────────────
Axiom Yield Broker — Signal Translation Layer v1.0
Stanfield's Axiom of Perpetuity (SAP) Framework

Converts raw engine output (stage integer, trap_energy float, chamber/path
identifiers) into logistics-domain decision signals suitable for:
    - Broker dashboards
    - API responses (external-facing)
    - Alert systems
    - Demo scenarios / buyer presentations

DESIGN PRINCIPLE (IP Protection):
    This layer is the ONLY thing exposed externally.
    Chamber logic, thresholds, amplifier values, and stage mechanics
    are NEVER included in translated output.  The mapping from
    system state → actionable signal is the commercial product.

Author : Richard L. Stanfield / MAAT (Meridian Axiom Alignment Technologies)
Contact: LuminarkMeridian@gmail.com
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Risk level constants (external-safe labels)
# ─────────────────────────────────────────────────────────────────────────────

RISK_CRITICAL = "CRITICAL"
RISK_HIGH     = "HIGH"
RISK_MODERATE = "MODERATE"
RISK_LOW      = "LOW"
RISK_STABLE   = "STABLE"


# ─────────────────────────────────────────────────────────────────────────────
# Signal dataclass — the external-facing output object
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AxiomSignal:
    """
    The complete translated output for a single carrier or lane evaluation.

    All fields are safe for external API exposure.
    No internal mechanics (thresholds, amplifiers, chamber labels) are present.
    """
    # Core identifiers
    carrier_id:        Optional[str]
    stage:             int
    stage_name:        str
    yield_score:       float          # 0–100, inverted from trap_energy
    risk_level:        str            # Rule severity label; not a measured probability or verified carrier risk

    # Decision signals
    signal_code:       str            # machine-readable signal identifier
    signal_label:      str            # human-readable signal name
    recommended_action: str           # specific broker action

    # Alert flags
    load_assignment_blocked: bool     # Prototype review-hold flag only; not an enforced dispatch restriction
    immediate_intervention:  bool     # Prompt human-review flag; not a verified emergency alert
    predictive_window_hours: Optional[int]  # Reserved for validated prediction; always None in this prototype

    # Supplementary context (buyer-facing, no mechanics exposed)
    pattern_description: str         # what the system is observing
    broker_note:         str         # plain-English summary

    # Stage 5 specific
    bifurcation_path:  Optional[str] = None  # "ADVANCE", "REGRESSION", "LOCK"
    bifurcation_label: Optional[str] = None

    # Metadata
    build:    str = "overwatch"
    version:  str = "1.0"
    assessment_basis: str = "Rule-based SAP/NSDT prototype output; not independently validated for carrier-risk prediction. Human verification required."


# ─────────────────────────────────────────────────────────────────────────────
# Stage name registry (canonical — never alter)
# ─────────────────────────────────────────────────────────────────────────────

STAGE_NAMES = {
    0: "PLENARA",
    1: "SPARK OF NAVIGATION",
    2: "FORGE OF POLARITY",
    3: "ENGINE OF EXPRESSION",
    4: "CRUCIBLE OF EQUILIBRIUM",
    5: "DYNAMO OF WILL",
    6: "NEXUS OF HARMONY",
    7: "LENS OF DISTILLATION",
    8: "VESSEL OF GROUNDING",
    9: "TRANSPARENCY OF THE GUIDE",
}


# ─────────────────────────────────────────────────────────────────────────────
# Yield score conversion
# ─────────────────────────────────────────────────────────────────────────────

def _trap_energy_to_yield_score(trap_energy: float) -> float:
    """
    Convert trap_energy [0.0, 1.0] to Axiom Yield Score [0, 100].
    Higher yield score = healthier system.
    trap_energy = 0.0 → yield_score = 100
    trap_energy = 1.0 → yield_score = 0
    """
    return round((1.0 - max(0.0, min(1.0, trap_energy))) * 100, 1)


# ─────────────────────────────────────────────────────────────────────────────
# Core translation function
# ─────────────────────────────────────────────────────────────────────────────

def translate_result(
    stage:        int,
    trap_energy:  float,
    carrier_id:   Optional[str] = None,
    build:        str = "overwatch",
    # Optional: pass Stage 5 path ('A', 'B', 'C') if already computed
    stage5_path:  Optional[str] = None,
    # Optional: pass Stage 8 chamber ('A', 'B', None) if already computed
    stage8_chamber: Optional[str] = None,
) -> AxiomSignal:
    """
    Primary external entry point.  Takes raw engine output and returns
    a fully translated AxiomSignal ready for API response or dashboard render.

    Parameters
    ----------
    stage        : SAP stage integer (0–9)
    trap_energy  : float [0.0, 1.0] from sap_energy_layer.trap_energy()
    carrier_id   : optional carrier identifier for response tagging
    build        : engine build context
    stage5_path  : 'A', 'B', or 'C' from Stage 5 bifurcation (if stage == 5)
    stage8_chamber: 'A', 'B', or None from Stage 8 evaluation (if stage == 8)
    """
    yield_score = _trap_energy_to_yield_score(trap_energy)
    stage_name  = STAGE_NAMES.get(stage, f"STAGE_{stage}")

    # ── Route to stage-specific translator ───────────────────────────────────
    if stage == 8:
        return _translate_stage_8(
            stage_name, yield_score, trap_energy,
            carrier_id, build, stage8_chamber
        )

    if stage == 5:
        return _translate_stage_5(
            stage_name, yield_score, trap_energy,
            carrier_id, build, stage5_path
        )

    if stage == 9:
        return _translate_stage_9(
            stage_name, yield_score, trap_energy, carrier_id, build
        )

    # ── General stage translation ─────────────────────────────────────────────
    return _translate_general(
        stage, stage_name, yield_score, trap_energy, carrier_id, build
    )


# ─────────────────────────────────────────────────────────────────────────────
# Stage-specific translators
# ─────────────────────────────────────────────────────────────────────────────

def _translate_stage_8(
    stage_name, yield_score, trap_energy,
    carrier_id, build, chamber
) -> AxiomSignal:
    """
    Stage 8 — VESSEL OF GROUNDING
    The most commercially significant stage for Axiom Yield.
    Two framework-defined Stage 8 patterns; their relationship to actual carrier outcomes has not been validated.
    """

    if chamber == "A":
        # Illusion of Arrival — carrier appears rock-solid, zero safety margin
        risk_level = RISK_HIGH if trap_energy < 0.8 else RISK_CRITICAL
        return AxiomSignal(
            carrier_id               = carrier_id,
            stage                    = 8,
            stage_name               = stage_name,
            yield_score              = yield_score,
            risk_level               = risk_level,
            signal_code              = "S8_CRYSTALLIZATION",
            signal_label             = "Crystallized Stability",
            recommended_action       = (
                "Treat this as a prototype review flag only. Verify current HOS, ELD telemetry, equipment condition, driver availability, route, and weather independently before making any dispatch decision."
            ),
            load_assignment_blocked  = True,
            immediate_intervention   = False,
            predictive_window_hours  = None,
            pattern_description      = (
                "The supplied values triggered the prototype's Stage 8 Chamber A rules. This pattern has not been validated as a real-world carrier-failure indicator."
            ),
            broker_note              = (
                f"Yield Score {yield_score:.0f} — Stage 8 Chamber A rule flag. "
                "No failure probability or timing has been established. Verify independently.""
            ),
            build                    = build,
        )

    elif chamber == "B":
        # Illusion of Permanence — carrier in high-tension lock, cannot self-recover
        return AxiomSignal(
            carrier_id               = carrier_id,
            stage                    = 8,
            stage_name               = stage_name,
            yield_score              = yield_score,
            risk_level               = RISK_CRITICAL,
            signal_code              = "S8_TENSION_LOCK",
            signal_label             = "Tension Lock",
            recommended_action       = (
                "The rules flagged a Stage 8 Chamber B pattern. Verify the source data and obtain an independent operational assessment before considering any load-protection action."
            ),
            load_assignment_blocked  = True,
            immediate_intervention   = True,
            predictive_window_hours  = None,
            pattern_description      = (
                "Carrier is under extreme accumulated tension with no coherent "
                "response signal under the prototype's rule definitions. This classification is not a verified carrier condition or failure prediction."
            ),
            broker_note              = (
                f"Yield Score {yield_score:.0f} — Stage 8 Chamber B rule flag. "
                "No failure probability or timing has been established. Verify independently.""
            ),
            build                    = build,
        )

    else:
        # Healthy Stage 8 traversal — carrier is working through duality phase
        return AxiomSignal(
            carrier_id               = carrier_id,
            stage                    = 8,
            stage_name               = stage_name,
            yield_score              = yield_score,
            risk_level               = RISK_LOW,
            signal_code              = "S8_TRAVERSAL",
            signal_label             = "Stage 8 Traversal",
            recommended_action       = (
                "Monitor closely. Carrier is in a high-complexity phase but "
                "is not in a trap state. Assign standard loads only. "
                "Re-evaluate in 6 hours."
            ),
            load_assignment_blocked  = False,
            immediate_intervention   = False,
            predictive_window_hours  = None,
            pattern_description      = (
                "Carrier is navigating peak operational complexity without "
                "crystallizing into a failure state. Continue monitoring."
            ),
            broker_note              = (
                f"Yield Score {yield_score:.0f} — Stage 8 active, no trap detected. "
                "Monitor and reassign to standard loads only."
            ),
            build                    = build,
        )


def _translate_stage_5(
    stage_name, yield_score, trap_energy,
    carrier_id, build, path
) -> AxiomSignal:
    """
    Stage 5 — DYNAMO OF WILL
    The only stage with a backward pathway.  Three distinct outcomes.
    """

    if path == "A":
        return AxiomSignal(
            carrier_id               = carrier_id,
            stage                    = 5,
            stage_name               = stage_name,
            yield_score              = yield_score,
            risk_level               = RISK_STABLE,
            signal_code              = "S5_ADVANCE",
            signal_label             = "Recovery Trajectory",
            recommended_action       = (
                "The rules classified the supplied values as the Stage 5 advance path. This is not confirmation of recovery or a forecast of future performance. Verify operational data independently."
            ),
            load_assignment_blocked  = False,
            immediate_intervention   = False,
            predictive_window_hours  = None,
            pattern_description      = (
                "System has passed the critical choice point and is moving "
                "toward integration and stability."
            ),
            broker_note              = (
                f"Yield Score {yield_score:.0f} — Stage 5 advance-path rule flag. "
                "No recovery or performance forecast has been validated."
            ),
            bifurcation_path         = "ADVANCE",
            bifurcation_label        = "Recovery Arc — Advancing",
            build                    = build,
        )

    elif path == "B":
        alert_note = (
            "Prototype rule flag — Stage 5 pullback classification. "
            if build == "overwatch"
            else "Carrier has entered a strategic reset phase. "
        )
        return AxiomSignal(
            carrier_id               = carrier_id,
            stage                    = 5,
            stage_name               = stage_name,
            yield_score              = yield_score,
            risk_level               = RISK_MODERATE,
            signal_code              = "S5_REGRESSION",
            signal_label             = "Capacity Pullback",
            recommended_action       = (
                "The rules classified the supplied values as the Stage 5 regression path. Review verified operating data and consult the responsible operations team; do not change assignments solely on this prototype output."
            ),
            load_assignment_blocked  = False,
            immediate_intervention   = False,
            predictive_window_hours  = None,
            pattern_description      = (
                "The supplied values triggered the Stage 5 regression rule. The system does not establish why the carrier values occurred or whether recovery capacity is present."
            ),
            broker_note              = (
                f"Yield Score {yield_score:.0f} — {alert_note}"
                "Stage 5 regression rule flag; no recovery timing has been established. Verify independently."
            ),
            bifurcation_path         = "REGRESSION",
            bifurcation_label        = "Capacity Pullback — Recalibrating",
            build                    = build,
        )

    else:
        # Path C — Bifurcation Lock
        return AxiomSignal(
            carrier_id               = carrier_id,
            stage                    = 5,
            stage_name               = stage_name,
            yield_score              = yield_score,
            risk_level               = RISK_CRITICAL,
            signal_code              = "S5_LOCK",
            signal_label             = "Bifurcation Lock",
            recommended_action       = (
                "The rules classified the supplied values as the Stage 5 lock path. Escalate for human review and verify the source data; do not remove or reassign loads solely on this prototype output."
            ),
            load_assignment_blocked  = True,
            immediate_intervention   = True,
            predictive_window_hours  = None,
            pattern_description      = (
                "Carrier has entered a bifurcation lock: maximum tension "
                "with no adaptive capacity remaining. Neither forward "
                "progress nor safe pullback is possible. "
                "This is the highest-risk state in the system."
            ),
            broker_note              = (
                f"Yield Score {yield_score:.0f} — BIFURCATION LOCK. "
                "Highest rule-severity category in this prototype. No failure timing or probability has been established."
            ),
            bifurcation_path         = "LOCK",
            bifurcation_label        = "Bifurcation Lock — Crisis",
            build                    = build,
        )


def _translate_stage_9(
    stage_name, yield_score, trap_energy, carrier_id, build
) -> AxiomSignal:
    """Stage 9 rule classification; not a prediction of imminent carrier failure."""
    return AxiomSignal(
        carrier_id               = carrier_id,
        stage                    = 9,
        stage_name               = stage_name,
        yield_score              = yield_score,
        risk_level               = RISK_CRITICAL,
        signal_code              = "S9_CATASTROPHIC_RELEASE",
        signal_label             = "Catastrophic Release",
        recommended_action       = (
            "Verify live operating conditions through established carrier-monitoring procedures and qualified personnel. Do not take dispatch or insurance action solely on this prototype classification."
        ),
        load_assignment_blocked  = True,
        immediate_intervention   = True,
        predictive_window_hours  = None,
        pattern_description      = (
            "The supplied values triggered the prototype's Stage 9 rule. This does not establish a breakdown, driver departure, accident, or other service failure.""
        ),
        broker_note              = (
            f"Yield Score {yield_score:.0f} — CATASTROPHIC RELEASE DETECTED. "
            "No failure timing or probability has been established. Verify current conditions independently."
        ),
        build                    = build,
    )


def _translate_general(
    stage, stage_name, yield_score, trap_energy, carrier_id, build
) -> AxiomSignal:
    """General translation for Stages 0–4, 6–7."""

    # Determine risk level from trap_energy
    if trap_energy >= 0.8:
        risk_level = RISK_CRITICAL
        signal_code  = "HIGH_TENSION"
        signal_label = "High System Tension"
        action = (
            "Treat this rule-severity flag as a prompt for independent review. Verify current carrier data and established operational indicators before changing assignments."
        )
        blocked  = True
        intervene = False
        window   = None
        pattern  = "The framework's rules assigned a high-tension classification to the supplied inputs; real-world meaning has not been validated."
        note     = f"Yield Score {yield_score:.0f} — High rule-severity flag. Verify independently before any dispatch decision."

    elif trap_energy >= 0.6:
        risk_level = RISK_HIGH
        signal_code  = "EMERGING_INSTABILITY"
        signal_label = "Emerging Instability"
        action = (
            "Review the input data and current operating conditions with the responsible operations team. Do not rely on this prototype score alone."
        )
        blocked  = False
        intervene = False
        window   = None
        pattern  = "The framework's rules assigned an emerging-instability classification to the supplied inputs; real-world meaning has not been validated."
        note     = f"Yield Score {yield_score:.0f} — Emerging-instability rule flag; human verification required."

    elif trap_energy >= 0.4:
        risk_level = RISK_MODERATE
        signal_code  = "MONITOR"
        signal_label = "Monitor"
        action = (
            "Continue using established carrier-monitoring procedures; this prototype does not estimate a validated review interval."
        )
        blocked  = False
        intervene = False
        window   = None
        pattern  = "The framework's rules assigned a transitional classification. This does not establish that the carrier is safe or risk-free."
        note     = f"Yield Score {yield_score:.0f} — Transitional rule classification; not a safety clearance."

    else:
        risk_level = RISK_STABLE
        signal_code  = "STABLE"
        signal_label = "Stable"
        action       = "No high-severity rule was triggered. Continue established carrier checks; this is not a safety clearance."
        blocked      = False
        intervene    = False
        window       = None
        pattern      = "The framework's rules assigned a low-severity classification. This does not establish that the carrier is safe or risk-free."
        note         = f"Yield Score {yield_score:.0f} — Low-severity rule classification; not a safety clearance."

    return AxiomSignal(
        carrier_id               = carrier_id,
        stage                    = stage,
        stage_name               = stage_name,
        yield_score              = yield_score,
        risk_level               = risk_level,
        signal_code              = signal_code,
        signal_label             = signal_label,
        recommended_action       = action,
        load_assignment_blocked  = blocked,
        immediate_intervention   = intervene,
        predictive_window_hours  = window,
        pattern_description      = pattern,
        broker_note              = note,
        build                    = build,
    )


# ─────────────────────────────────────────────────────────────────────────────
# API response builder
# ─────────────────────────────────────────────────────────────────────────────

def build_api_response(
    engine_output: dict,
    carrier_id: Optional[str] = None,
    build: str = "overwatch"
) -> dict:
    """
    Takes raw engine_output dict and returns a complete, external-safe
    API response dict.

    Expected engine_output keys:
        stage          : int
        trap_energy    : float
        stage5_path    : Optional[str] — 'A', 'B', or 'C'
        stage8_chamber : Optional[str] — 'A', 'B', or None

    Returns merged dict: engine_output fields + translated signal fields.
    Internal mechanics (chamber logic, amplifier values) are stripped.
    """
    signal = translate_result(
        stage          = engine_output["stage"],
        trap_energy    = engine_output["trap_energy"],
        carrier_id     = carrier_id,
        build          = build,
        stage5_path    = engine_output.get("stage5_path"),
        stage8_chamber = engine_output.get("stage8_chamber"),
    )

    # Build clean external response — no internal mechanics exposed
    response = {
        "carrier_id":               signal.carrier_id,
        "stage":                    signal.stage,
        "stage_name":               signal.stage_name,
        "yield_score":              signal.yield_score,
        "risk_level":               signal.risk_level,
        "signal_code":              signal.signal_code,
        "signal_label":             signal.signal_label,
        "recommended_action":       signal.recommended_action,
        "load_assignment_blocked":  signal.load_assignment_blocked,
        "immediate_intervention":   signal.immediate_intervention,
        "predictive_window_hours":  signal.predictive_window_hours,
        "assessment_basis":          signal.assessment_basis,
        "pattern_description":      signal.pattern_description,
        "broker_note":              signal.broker_note,
    }

    # Stage 5 bifurcation path — safe to expose (no mechanics)
    if signal.bifurcation_path:
        response["bifurcation_path"]  = signal.bifurcation_path
        response["bifurcation_label"] = signal.bifurcation_label

    return response
