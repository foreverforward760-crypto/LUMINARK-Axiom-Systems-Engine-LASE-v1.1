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
    risk_level:        str            # STABLE / LOW / MODERATE / HIGH / CRITICAL

    # Decision signals
    signal_code:       str            # machine-readable signal identifier
    signal_label:      str            # human-readable signal name
    recommended_action: str           # specific broker action

    # Alert flags
    load_assignment_blocked: bool     # True = do not assign new loads
    immediate_intervention:  bool     # True = active loads at risk now
    predictive_window_hours: Optional[int]  # estimated hours to failure event

    # Supplementary context (buyer-facing, no mechanics exposed)
    pattern_description: str         # what the system is observing
    broker_note:         str         # plain-English summary

    # Stage 5 specific
    bifurcation_path:  Optional[str] = None  # "ADVANCE", "REGRESSION", "LOCK"
    bifurcation_label: Optional[str] = None

    # Metadata
    build:    str = "overwatch"
    version:  str = "1.0"


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
    Two distinct carrier failure patterns, both requiring load protection.
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
                "Do not assign new high-value or time-sensitive loads. "
                "Carrier appears fully stable but has lost all adaptive capacity. "
                "Any disruption — weather, traffic, equipment — will produce "
                "immediate failure with no recovery buffer."
            ),
            load_assignment_blocked  = True,
            immediate_intervention   = False,
            predictive_window_hours  = 24,
            pattern_description      = (
                "Carrier is showing maximum stability with near-zero flexibility. "
                "This pattern precedes sudden brittle failure — the system looks "
                "healthy on every standard metric, which is the warning sign."
            ),
            broker_note              = (
                f"Yield Score {yield_score:.0f} — CARRIER LOOKS STABLE BUT IS NOT. "
                "Stage 8 Crystallization detected. 24-hour failure window active. "
                "Protect your loads now."
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
                "Remove carrier from active load assignments immediately. "
                "Initiate load recovery protocol for all in-transit freight. "
                "Contact backup carriers now — do not wait for confirmation of failure."
            ),
            load_assignment_blocked  = True,
            immediate_intervention   = True,
            predictive_window_hours  = 12,
            pattern_description      = (
                "Carrier is under extreme accumulated tension with no coherent "
                "response signal. System is locked — cannot advance to recovery "
                "and cannot retreat to a safe state. Failure is imminent."
            ),
            broker_note              = (
                f"Yield Score {yield_score:.0f} — CRITICAL TENSION LOCK. "
                "Stage 8 maximum-risk condition. 12-hour failure window. "
                "Load recovery protocol required NOW."
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
                "Carrier is on a confirmed recovery arc. "
                "Safe to assign standard and moderate-priority loads. "
                "Performance improvement expected over next 24-48 hours."
            ),
            load_assignment_blocked  = False,
            immediate_intervention   = False,
            predictive_window_hours  = None,
            pattern_description      = (
                "System has passed the critical choice point and is moving "
                "toward integration and stability."
            ),
            broker_note              = (
                f"Yield Score {yield_score:.0f} — Recovery arc confirmed. "
                "Assign standard loads."
            ),
            bifurcation_path         = "ADVANCE",
            bifurcation_label        = "Recovery Arc — Advancing",
            build                    = build,
        )

    elif path == "B":
        alert_note = (
            "HIGH-PRIORITY ALERT — Carrier has entered voluntary pullback. "
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
                "Reduce load assignment by 50%. Do not assign high-value or "
                "time-sensitive freight. Carrier is recalibrating — monitor "
                "for recovery signal in next 12-24 hours before resuming "
                "normal assignment."
            ),
            load_assignment_blocked  = False,
            immediate_intervention   = False,
            predictive_window_hours  = 24,
            pattern_description      = (
                "Carrier is pulling back from operational overextension. "
                "This is a self-protective response, not a collapse. "
                "System retains recovery capacity."
            ),
            broker_note              = (
                f"Yield Score {yield_score:.0f} — {alert_note}"
                "Reduce assignments. Watch for recovery in 12-24 hours."
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
                "Remove from all active assignments immediately. "
                "Carrier is locked — cannot advance or safely retreat. "
                "Initiate emergency load recovery. "
                "Do not reassign until full system reset is confirmed."
            ),
            load_assignment_blocked  = True,
            immediate_intervention   = True,
            predictive_window_hours  = 6,
            pattern_description      = (
                "Carrier has entered a bifurcation lock: maximum tension "
                "with no adaptive capacity remaining. Neither forward "
                "progress nor safe pullback is possible. "
                "This is the highest-risk state in the system."
            ),
            broker_note              = (
                f"Yield Score {yield_score:.0f} — BIFURCATION LOCK. "
                "Highest-risk state. Emergency load recovery required. "
                "6-hour failure window."
            ),
            bifurcation_path         = "LOCK",
            bifurcation_label        = "Bifurcation Lock — Crisis",
            build                    = build,
        )


def _translate_stage_9(
    stage_name, yield_score, trap_energy, carrier_id, build
) -> AxiomSignal:
    """Stage 9 — TRANSPARENCY OF THE GUIDE: Catastrophic release imminent."""
    return AxiomSignal(
        carrier_id               = carrier_id,
        stage                    = 9,
        stage_name               = stage_name,
        yield_score              = yield_score,
        risk_level               = RISK_CRITICAL,
        signal_code              = "S9_CATASTROPHIC_RELEASE",
        signal_label             = "Catastrophic Release",
        recommended_action       = (
            "Execute immediate load recovery protocol. "
            "All active loads with this carrier are at risk. "
            "Contact backup carriers now. "
            "Do not assign any new freight. "
            "Document all active shipments for insurance and claims processing."
        ),
        load_assignment_blocked  = True,
        immediate_intervention   = True,
        predictive_window_hours  = 2,
        pattern_description      = (
            "Carrier system has reached dissolution threshold. "
            "Catastrophic service failure — breakdown, driver quit, accident, "
            "or total operational collapse — is imminent or already underway."
        ),
        broker_note              = (
            f"Yield Score {yield_score:.0f} — CATASTROPHIC RELEASE DETECTED. "
            "2-hour window. Execute load recovery NOW."
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
            "Hold all new load assignments pending re-evaluation. "
            "Carrier is approaching a critical threshold."
        )
        blocked  = True
        intervene = False
        window   = 18
        pattern  = "System is accumulating tension toward a critical transition point."
        note     = f"Yield Score {yield_score:.0f} — High tension detected. Hold assignments."

    elif trap_energy >= 0.6:
        risk_level = RISK_HIGH
        signal_code  = "EMERGING_INSTABILITY"
        signal_label = "Emerging Instability"
        action = (
            "Reduce load assignment. Assign standard freight only. "
            "Re-evaluate in 8 hours."
        )
        blocked  = False
        intervene = False
        window   = 24
        pattern  = "System is showing early instability indicators. Monitoring required."
        note     = f"Yield Score {yield_score:.0f} — Instability emerging. Reduce assignments."

    elif trap_energy >= 0.4:
        risk_level = RISK_MODERATE
        signal_code  = "MONITOR"
        signal_label = "Monitor"
        action = (
            "Assign standard loads. "
            "Monitor for changes in the next 12–24 hours."
        )
        blocked  = False
        intervene = False
        window   = None
        pattern  = "System is in a transitional phase. No immediate action required."
        note     = f"Yield Score {yield_score:.0f} — Transitional. Monitor and assign standard loads."

    else:
        risk_level = RISK_STABLE
        signal_code  = "STABLE"
        signal_label = "Stable"
        action       = "Normal load assignment. No restrictions."
        blocked      = False
        intervene    = False
        window       = None
        pattern      = "System is operating within healthy parameters."
        note         = f"Yield Score {yield_score:.0f} — Stable. Normal operations."

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
        "pattern_description":      signal.pattern_description,
        "broker_note":              signal.broker_note,
    }

    # Stage 5 bifurcation path — safe to expose (no mechanics)
    if signal.bifurcation_path:
        response["bifurcation_path"]  = signal.bifurcation_path
        response["bifurcation_label"] = signal.bifurcation_label

    return response
