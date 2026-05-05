"""
luminark/sap_domain_bridge.py – Cross-Domain NSDT Translator

Translates domain-specific metrics into the 5D NSDT coordinate space
so the Omega Loop can route events across build boundaries.

DOMAIN MAPPINGS:

  Logistics (Axiom Yield Broker):
    complexity    ← route_complexity (stops, HOS pressure, weather)
    stability     ← carrier_reliability (on-time %, insurance history)
    tension       ← market_pressure (spot rate vs contract, lane volatility)
    adaptability  ← reroute_capacity (available alternatives)
    coherence     ← system_integration (ELD sync, visibility score)

  Biometric (Meridian-Bio):
    complexity    ← HRV_complexity (LF/HF ratio, sample entropy)
    stability     ← resting_heart_rate_norm (normalised inverse)
    tension       ← cortisol_proxy (movement intensity, skin conductance)
    adaptability  ← recovery_rate (post-stress HRV recovery speed)
    coherence     ← polyvagal_tone (ventral vagal activation score)

  Grid/Infrastructure (Overwatch):
    complexity    ← load_complexity (renewable intermittency, demand spikes)
    stability     ← grid_frequency_stability (deviation from 60Hz)
    tension       ← generation_deficit (supply-demand gap)
    adaptability  ← reserve_margin (available backup capacity)
    coherence     ← network_synchronization (phase coherence across nodes)

  Cognitive/Kairos:
    complexity    ← decision_load (open tabs, context switches)
    stability     ← affect_stability (mood variance over session)
    tension       ← arousal_level (sympathetic activation)
    adaptability  ← response_flexibility (choice diversity)
    coherence     ← narrative_coherence (session self-report consistency)
"""

from dataclasses import dataclass
from typing import Dict, Optional
from luminark.omega_loop import NSDTEvent


def _clamp(v: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return max(lo, min(hi, v))


def _norm(v: float, v_min: float, v_max: float) -> float:
    """Linear normalise v from [v_min, v_max] to [0, 10]."""
    if v_max == v_min:
        return 5.0
    return _clamp((v - v_min) / (v_max - v_min) * 10.0)


# ── Logistics (Axiom Yield Broker) ────────────────────────────────────────────

@dataclass
class LogisticsMetrics:
    """Raw logistics metrics from AYB."""
    carrier_id:          str
    route_stops:         int    = 1       # 1–20
    hos_hours_remaining: float  = 11.0   # 0–11 (HOS limit)
    on_time_pct:         float  = 95.0   # 0–100
    spot_vs_contract:    float  = 0.0    # % above/below contract rate
    reroute_options:     int    = 3       # 0–10 alternatives
    eld_sync_score:      float  = 100.0  # 0–100 (ELD data completeness)
    weather_severity:    float  = 0.0    # 0–10


def logistics_to_nsdt(m: LogisticsMetrics, system_id: Optional[str] = None) -> NSDTEvent:
    """Translate AYB logistics metrics to an NSDTEvent."""
    # complexity: route complexity + HOS pressure + weather
    hos_pressure = _norm(11.0 - m.hos_hours_remaining, 0.0, 11.0)  # high hours left = low pressure
    complexity   = _clamp((_norm(m.route_stops, 1, 20) + hos_pressure + m.weather_severity) / 3.0)

    # stability: carrier reliability (on-time %)
    stability = _norm(m.on_time_pct, 0.0, 100.0)

    # tension: market pressure (spot vs contract, positive = above contract)
    tension = _norm(m.spot_vs_contract + 50.0, 0.0, 100.0)  # centre at 0% = 5.0

    # adaptability: reroute capacity
    adaptability = _norm(m.reroute_options, 0.0, 10.0)

    # coherence: ELD sync quality
    coherence = _norm(m.eld_sync_score, 0.0, 100.0)

    return NSDTEvent(
        source_domain="logistics",
        source_id=system_id or m.carrier_id,
        complexity=round(complexity, 2),
        stability=round(stability, 2),
        tension=round(tension, 2),
        adaptability=round(adaptability, 2),
        coherence=round(coherence, 2),
        metadata={
            "carrier_id":          m.carrier_id,
            "hos_hours_remaining": m.hos_hours_remaining,
            "on_time_pct":         m.on_time_pct,
            "route_stops":         m.route_stops,
        }
    )


# ── Biometric (Meridian-Bio) ──────────────────────────────────────────────────

@dataclass
class BiometricMetrics:
    """Raw biometric metrics from Meridian-Bio wearables."""
    user_id:            str
    hrv_lf_hf_ratio:    float  = 1.5    # 0.5–5.0 (high = sympathetic dominance)
    resting_hr:         float  = 65.0   # 40–100 bpm
    movement_intensity: float  = 0.3    # 0.0–1.0 (g-force proxy)
    skin_conductance:   float  = 0.5    # 0.0–1.0 (EDA proxy)
    hrv_recovery_rate:  float  = 0.6    # 0.0–1.0 (post-stress recovery speed)
    polyvagal_tone:     float  = 0.7    # 0.0–1.0 (1.0 = full ventral)


def biometric_to_nsdt(m: BiometricMetrics, system_id: Optional[str] = None) -> NSDTEvent:
    """Translate Meridian-Bio biometric data to an NSDTEvent."""
    complexity   = _norm(m.hrv_lf_hf_ratio, 0.5, 5.0)
    stability    = _norm(100.0 - m.resting_hr, 0.0, 60.0)  # lower HR = more stable
    tension      = _clamp((m.movement_intensity + m.skin_conductance) * 5.0)
    adaptability = _norm(m.hrv_recovery_rate, 0.0, 1.0)
    coherence    = _norm(m.polyvagal_tone, 0.0, 1.0)

    return NSDTEvent(
        source_domain="biometric",
        source_id=system_id or m.user_id,
        complexity=round(complexity, 2),
        stability=round(stability, 2),
        tension=round(tension, 2),
        adaptability=round(adaptability, 2),
        coherence=round(coherence, 2),
        metadata={
            "user_id":         m.user_id,
            "hrv_lf_hf":       m.hrv_lf_hf_ratio,
            "polyvagal_tone":  m.polyvagal_tone,
            "resting_hr":      m.resting_hr,
        }
    )


# ── Grid/Infrastructure (Overwatch) ──────────────────────────────────────────

@dataclass
class GridMetrics:
    """Raw grid metrics from LUMINARK Overwatch."""
    node_id:              str
    renewable_pct:        float  = 40.0   # 0–100 % renewable generation
    frequency_hz:         float  = 60.0   # 59.5–60.5 Hz
    demand_mw:            float  = 5000.0
    supply_mw:            float  = 5200.0
    reserve_margin_pct:   float  = 15.0   # 0–30 %
    phase_coherence:      float  = 0.98   # 0–1.0


def grid_to_nsdt(m: GridMetrics, system_id: Optional[str] = None) -> NSDTEvent:
    """Translate grid infrastructure metrics to an NSDTEvent."""
    complexity   = _norm(m.renewable_pct, 0.0, 100.0)           # high renewable = complex
    freq_dev     = abs(m.frequency_hz - 60.0) / 0.5             # normalise ±0.5 Hz
    stability    = _clamp(10.0 - freq_dev * 10.0)               # deviation → instability
    deficit      = max(0.0, m.demand_mw - m.supply_mw)
    tension      = _clamp(deficit / max(m.supply_mw, 1.0) * 100.0)
    adaptability = _norm(m.reserve_margin_pct, 0.0, 30.0)
    coherence    = _norm(m.phase_coherence, 0.0, 1.0)

    return NSDTEvent(
        source_domain="grid",
        source_id=system_id or m.node_id,
        complexity=round(complexity, 2),
        stability=round(stability, 2),
        tension=round(tension, 2),
        adaptability=round(adaptability, 2),
        coherence=round(coherence, 2),
        metadata={
            "node_id":           m.node_id,
            "frequency_hz":      m.frequency_hz,
            "reserve_margin_pct": m.reserve_margin_pct,
        }
    )


# ── Self-test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Domain Bridge self-test\n")

    # Logistics: stressed carrier
    log = logistics_to_nsdt(LogisticsMetrics(
        carrier_id="TX-441",
        route_stops=12,
        hos_hours_remaining=1.5,
        on_time_pct=72.0,
        spot_vs_contract=35.0,
        reroute_options=1,
        eld_sync_score=60.0,
        weather_severity=7.0,
    ))
    print(f"Logistics stressed: C={log.complexity} S={log.stability} T={log.tension} A={log.adaptability} Coh={log.coherence}")

    # Biometric: sympathetic spike
    bio = biometric_to_nsdt(BiometricMetrics(
        user_id="user-001",
        hrv_lf_hf_ratio=4.2,
        resting_hr=88.0,
        movement_intensity=0.8,
        skin_conductance=0.9,
        hrv_recovery_rate=0.2,
        polyvagal_tone=0.15,
    ))
    print(f"Biometric stressed: C={bio.complexity} S={bio.stability} T={bio.tension} A={bio.adaptability} Coh={bio.coherence}")

    # Grid: stable
    grid = grid_to_nsdt(GridMetrics(
        node_id="ercot-h",
        renewable_pct=35.0,
        frequency_hz=60.02,
        demand_mw=4800.0,
        supply_mw=5400.0,
        reserve_margin_pct=20.0,
        phase_coherence=0.99,
    ))
    print(f"Grid stable:        C={grid.complexity} S={grid.stability} T={grid.tension} A={grid.adaptability} Coh={grid.coherence}")

    print("\n✅ All domain bridge translations succeeded")
