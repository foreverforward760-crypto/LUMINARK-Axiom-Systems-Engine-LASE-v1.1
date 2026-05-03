"""
backend/luminark/nsdt_calculator.py – LUMINARK NSDT Adapter for Axiom Yield Broker

Translates Axiom Yield Broker domain inputs (FMCSA snapshot, state flags, ELD data)
into the 5-dimensional NSDT vector used by the LUMINARK SAP engine.

NSDT Dimensions (all normalised to [0, 10]):
    Complexity   ← route volatility + number of carriers + lane entropy
    Stability    ← physical HOS capacity (driver hours remaining)
    Tension      ← market pressure + violations + recovery debt
    Adaptability ← reroute capacity + driver experience proxy
    Coherence    ← communication quality + ELD sync quality

CORRECTION [6]: The submitted document imported from luminark.nsdt_calculator and
luminark.inversion_analyzer which do not exist in the LUMINARK engine. These adapter
modules provide the expected interface while internally using the actual SAP math
from the LuminarkHybridEngine build.

CORRECTION [8,9]: The yield_score formula used [0,100] scale but LUMINARK uses [0,10].
All normalisation is handled here so the formula in yield.py receives consistent values.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class NSDTVector:
    """
    5-dimensional NSDT vector for the SAP engine.
    All dimensions in [0.0, 10.0].
    """
    complexity:   float   # Route/network complexity
    stability:    float   # Physical HOS capacity
    tension:      float   # Market pressure + violations
    adaptability: float   # Reroute + flexibility capacity
    coherence:    float   # Communication + ELD sync quality

    def to_list(self):
        return [self.complexity, self.stability, self.tension,
                self.adaptability, self.coherence]


def _clamp(v: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return max(lo, min(hi, v))


def _norm(v: float, v_min: float, v_max: float) -> float:
    """Linear normalise v from [v_min, v_max] to [0, 10]."""
    if v_max == v_min:
        return 5.0
    return _clamp((v - v_min) / (v_max - v_min) * 10.0)


class NSDTBuilder:
    """
    Builds NSDT vectors from Axiom Yield Broker domain data.
    """

    # FMCSA baseline averages (used when ELD feed is unavailable)
    _FMCSA_DEFAULTS = {
        "drive_remaining":  5.5,   # hours — FMCSA industry average mid-shift
        "shift_remaining":  6.0,
        "cycle_remaining":  30.0,
        "violations":       0,
        "duty_status":      "DRIVING",
        "is_evasive":       False,
    }

    @classmethod
    def from_fmcsa_and_eld(
        cls,
        fmcsa_data:  Dict[str, Any],
        state_data:  Dict[str, Any],
        eld_data:    Dict[str, Any],
    ) -> NSDTVector:
        """
        Build NSDTVector from combined data sources.

        Parameters
        ----------
        fmcsa_data  : dict — carrier/route data from FMCSA feeds
                        Keys: route_stops (int), route_volatility (0-100),
                              recovery_debt (0-100), carrier_age_months (int),
                              on_time_pct (0-100)
        state_data  : dict — Florida DOT / state flags
                        Keys: lane_entropy (0-100), reroute_options (0-10),
                              market_pressure (0-100)
        eld_data    : dict — ELD telemetry (may be empty or contain 'error' key)
                        Keys: drive_remaining (hrs), violations (int),
                              is_evasive (bool), duty_status (str)
        """
        # Use ELD data if available, else fall back to FMCSA averages
        eld = dict(cls._FMCSA_DEFAULTS)
        if eld_data and "error" not in eld_data:
            eld.update(eld_data)

        # ── Complexity: route complexity + lane entropy ──────────────────────
        route_stops  = fmcsa_data.get("route_stops", 3)
        lane_entropy = state_data.get("lane_entropy", 30.0)
        complexity   = _clamp(
            _norm(route_stops, 1, 20) * 0.5 +
            _norm(lane_entropy, 0, 100) * 0.5
        )

        # ── Stability: HOS physical capacity ────────────────────────────────
        # Higher drive_remaining = more stable (physically safe)
        drive_hrs = eld.get("drive_remaining", 5.5)
        stability = _norm(drive_hrs, 0.0, 11.0)

        # ── Tension: market pressure + violations + recovery debt ────────────
        route_vol    = fmcsa_data.get("route_volatility", 30.0)
        recovery_dbt = fmcsa_data.get("recovery_debt", 20.0)
        violations   = eld.get("violations", 0)
        mkt_pressure = state_data.get("market_pressure", 40.0)
        is_evasive   = eld.get("is_evasive", False)

        tension = _clamp(
            _norm(route_vol, 0, 100) * 0.3 +
            _norm(recovery_dbt, 0, 100) * 0.25 +
            _norm(mkt_pressure, 0, 100) * 0.3 +
            min(violations * 1.5, 10.0) * 0.15 +
            (3.0 if is_evasive else 0.0)
        )

        # ── Adaptability: reroute capacity + flexibility ─────────────────────
        reroute_opts = state_data.get("reroute_options", 3)
        on_time_pct  = fmcsa_data.get("on_time_pct", 85.0)
        adaptability = _clamp(
            _norm(reroute_opts, 0, 10) * 0.5 +
            _norm(on_time_pct, 0, 100) * 0.5
        )

        # ── Coherence: communication + ELD data quality ─────────────────────
        comm_coh  = fmcsa_data.get("communication_coherence", 70.0)
        eld_degr  = 1.0 if (eld_data and "error" in eld_data) else 0.0
        coherence = _clamp(
            _norm(comm_coh, 0, 100) * 0.8 +
            (10.0 * (1.0 - eld_degr)) * 0.2   # penalty if ELD is degraded
        )

        return NSDTVector(
            complexity=round(complexity, 3),
            stability=round(stability, 3),
            tension=round(tension, 3),
            adaptability=round(adaptability, 3),
            coherence=round(coherence, 3),
        )
