"""
tests/test_integration_v81.py – Integration Tests for v8.1 Features

Tests all four architectural additions working together:
  1. Edge stub — zero-dependency offline analysis
  2. Oracle — cryptographic signing and verification
  3. UI Guidance — polyvagal UX data contract
  4. Omega Loop — cross-domain NSDT routing

Run with: pytest tests/test_integration_v81.py -v
"""

import os
import sys
import time
import numpy as np

# Allow imports from repo root and build directories
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "build1_overwatch_strict"))
sys.path.insert(0, os.path.join(_ROOT, "build3_active_defense"))


# ── 1. Edge stub ──────────────────────────────────────────────────────────────

def test_edge_no_external_imports():
    """Edge stub must not import numpy, requests, fastapi, or any external lib."""
    import importlib, ast
    path = os.path.join(_ROOT, "luminark", "sap_edge_stub.py")
    with open(path) as f:
        tree = ast.parse(f.read())
    forbidden = {"numpy", "np", "requests", "fastapi", "pydantic"}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [n.name for n in getattr(node, "names", [])]
            mod = getattr(node, "module", "") or ""
            for bad in forbidden:
                assert bad not in mod and all(bad not in n for n in names), \
                    f"Edge stub imports forbidden module: {bad}"


def test_edge_analyzer_all_cases():
    """EdgeAnalyzer produces valid actions for all SAP stage zones."""
    from sap_edge_stub import EdgeAnalyzer
    analyzer = EdgeAnalyzer()
    stage_vectors = [
        (0.5, 0.5, 0.5, 9.0, 0.5, 0.0),   # Stage 0
        (5.0, 4.0, 5.0, 5.0, 4.5, 0.5),   # Stage 5
        (7.5, 7.0, 8.0, 2.0, 2.0, 1.5),   # Stage 8 trap
        (6.5, 3.0, 7.0, 7.0, 3.5, 0.8),   # Stage 7
    ]
    valid_actions = {"HOLD", "DAMPEN", "INTERVENE", "BREAK_PATTERN"}
    for c, s, t, a, coh, vel in stage_vectors:
        result = analyzer.analyze(c, s, t, a, coh, velocity=vel)
        assert result["action"] in valid_actions
        assert 0.0 <= result["trap_energy"] <= 1.0
        assert result["V"] >= 0.0
        assert result["risk_level"] in ("LOW", "MODERATE", "HIGH", "CRITICAL")


def test_edge_cynical_loop_detection():
    """EdgeAnalyzer detects 8→7→8 cynical loop and returns BREAK_PATTERN."""
    from sap_edge_stub import EdgeAnalyzer
    analyzer = EdgeAnalyzer()
    # Feed a 8→7→8 sequence
    for stage in [6, 7, 8, 7, 8, 7, 8]:
        analyzer.analyze(7.5, 7.0, 8.0, 2.0, 2.0, velocity=0.5,
                         current_stage=stage)
    result = analyzer.analyze(7.5, 7.0, 8.0, 2.0, 2.0, velocity=0.5,
                               current_stage=8)
    assert result["action"] == "BREAK_PATTERN"
    assert result["cynical_loop"] is True


def test_edge_determinism():
    """Same inputs produce identical output across 20 calls."""
    from sap_edge_stub import EdgeAnalyzer
    analyzer = EdgeAnalyzer()
    r0 = analyzer.analyze(6.2, 4.1, 7.3, 3.8, 5.9, velocity=0.5)
    for _ in range(19):
        r = analyzer.analyze(6.2, 4.1, 7.3, 3.8, 5.9, velocity=0.5)
        assert r["V"] == r0["V"]
        assert r["action"] == r0["action"]


# ── 2. Oracle ─────────────────────────────────────────────────────────────────

def test_oracle_sign_and_verify():
    """Oracle sign + verify round-trip succeeds."""
    from sap_oracle import SAPOracle
    key = os.urandom(32)
    oracle = SAPOracle(key, "TEST-ORACLE")
    payload = {
        "system_id": "carrier-TX-441", "stage": 4,
        "trap_normalized": 18.5, "risk_level": "LOW",
        "timestamp": "2026-04-14T12:00:00",
    }
    signed = oracle.sign(payload)
    assert oracle.verify(signed)


def test_oracle_tamper_rejected():
    """Tampered payload must fail verification."""
    from sap_oracle import SAPOracle
    key = os.urandom(32)
    oracle = SAPOracle(key, "TEST-ORACLE")
    payload = {
        "system_id": "node-01", "stage": 3,
        "trap_normalized": 10.0, "risk_level": "LOW",
        "timestamp": "2026-04-14T00:00:00",
    }
    signed = oracle.sign(payload)
    tampered = dict(signed)
    tampered["trap_normalized"] = 99.9
    assert not oracle.verify(tampered)


def test_oracle_contract_hints():
    """Contract hints correctly map stage/trap to contract actions."""
    from sap_oracle import SAPOracle
    key = os.urandom(32)
    oracle = SAPOracle(key)
    cases = [
        (4, 18.0,  "RELEASE_ESCROW"),
        (5, 55.0,  "INCREASE_PREMIUM"),
        (7, 72.0,  "HOLD_AND_REALLOCATE"),
        (8, 85.0,  "HOLD_AND_REALLOCATE"),
    ]
    for stage, trap, expected_action in cases:
        signed = oracle.sign({
            "system_id": "x", "stage": stage,
            "trap_normalized": trap, "risk_level": "TEST",
            "timestamp": "",
        })
        assert signed["contract_hint"]["action"] == expected_action, \
            f"stage={stage} trap={trap}: expected {expected_action}, got {signed['contract_hint']['action']}"


def test_oracle_abi_encoding():
    """ABI-encoded bytes32 decodes to correct stage and trap values."""
    import struct
    from sap_oracle import SAPOracle
    key = os.urandom(32)
    oracle = SAPOracle(key)
    signed = oracle.sign({
        "system_id": "x", "stage": 6, "trap_normalized": 47.3,
        "risk_level": "MODERATE", "timestamp": "",
    })
    raw = bytes.fromhex(signed["abi_encoded"])
    stage_decoded = raw[0]
    trap_decoded  = struct.unpack(">H", raw[1:3])[0]
    assert stage_decoded == 6
    assert trap_decoded == int(47.3 * 100)


# ── 3. UI Guidance ────────────────────────────────────────────────────────────

def test_ui_guidance_schema_complete():
    """generate_ui_guidance returns all required keys for every stage."""
    from sap_ui_guidance import generate_ui_guidance
    required_keys = {
        "color_palette", "animation", "layout", "breathing_guide",
        "stage_label", "somatic_cue", "urgency", "polyvagal_state",
    }
    for stage in range(10):
        g = generate_ui_guidance(stage, entropy=1.0, trap_energy=0.2)
        missing = required_keys - set(g.keys())
        assert not missing, f"Stage {stage} missing keys: {missing}"


def test_ui_guidance_urgency_escalation():
    """Urgency escalates correctly with stage and trap energy."""
    from sap_ui_guidance import generate_ui_guidance
    assert generate_ui_guidance(0, 0.3, 0.05)["urgency"] == "none"
    assert generate_ui_guidance(5, 1.5, 0.3)["urgency"] == "watch"
    assert generate_ui_guidance(7, 0.8, 0.55)["urgency"] == "alert"
    assert generate_ui_guidance(8, 0.4, 0.82)["urgency"] == "critical"


def test_ui_guidance_duality_triggers_critical_palette():
    """Stage 5 duality switches to critical palette (deep rose primary color)."""
    from sap_ui_guidance import generate_ui_guidance
    normal  = generate_ui_guidance(5, 1.0, 0.2, duality_detected=False)
    duality = generate_ui_guidance(5, 1.0, 0.2, duality_detected=True)
    # Duality switches to the critical palette — primary becomes deep rose
    assert duality["color_palette"]["primary"] != normal["color_palette"]["primary"], \
        "Duality must change the primary color"
    assert duality["color_palette"]["primary"] == "#BE123C", \
        "Duality must use critical palette primary (#BE123C)"
    # Animation becomes faster/more focused
    assert duality["animation"]["transition_ms"] <= normal["animation"]["transition_ms"], \
        "Duality must reduce transition speed (more focused)"


def test_ui_guidance_high_entropy_slows_animation():
    """High entropy must increase transition_ms to reduce cognitive load."""
    from sap_ui_guidance import generate_ui_guidance
    low_ent  = generate_ui_guidance(4, entropy=0.5, trap_energy=0.1)
    high_ent = generate_ui_guidance(4, entropy=2.5, trap_energy=0.1)
    assert high_ent["animation"]["transition_ms"] >= low_ent["animation"]["transition_ms"]


def test_ui_guidance_polyvagal_override():
    """polyvagal_override is respected in palette selection."""
    from sap_ui_guidance import generate_ui_guidance
    g = generate_ui_guidance(3, 0.5, 0.1, polyvagal_override="ventral")
    assert g["polyvagal_state"] == "ventral"


# ── 4. Omega Loop ─────────────────────────────────────────────────────────────

def test_omega_logistics_to_kairos():
    """AYB Stage 7 event routes to Kairos."""
    from luminark.omega_loop import OmegaLoop, NSDTEvent, install_default_rules
    received = []
    loop = OmegaLoop(log=False)
    loop.register("kairos", lambda e: received.append(e))
    install_default_rules(loop)

    loop.publish(NSDTEvent(
        source_domain="logistics", source_id="TX-441",
        complexity=7.2, stability=3.1, tension=8.5,
        adaptability=2.0, coherence=3.8,
        stage=7, trap_score=72.0,
    ))
    assert len(received) == 1
    assert received[0].source_domain == "logistics"


def test_omega_no_circular_routing():
    """An event from domain X must never route back to domain X."""
    from luminark.omega_loop import OmegaLoop, NSDTEvent, RoutingRule
    loop = OmegaLoop(log=False)
    loop.register("kairos", lambda e: None)
    loop.register("logistics", lambda e: (_ for _ in ()).throw(
        AssertionError("Circular routing detected!")
    ))
    loop.add_rule(RoutingRule(
        name="test-rule", target_domains=["logistics", "kairos"],
        source_domains=["logistics"], min_stage=0,
    ))
    # Should not raise — circular routing is suppressed
    loop.publish(NSDTEvent(
        source_domain="logistics", source_id="x",
        complexity=5.0, stability=5.0, tension=5.0,
        adaptability=5.0, coherence=5.0,
    ))


def test_omega_normal_event_not_routed():
    """Stage 3 event below all thresholds must not trigger any rules."""
    from luminark.omega_loop import OmegaLoop, NSDTEvent, install_default_rules
    received = []
    loop = OmegaLoop(log=False)
    loop.register("kairos",        lambda e: received.append("kairos"))
    loop.register("overwatch",     lambda e: received.append("overwatch"))
    loop.register("active_defense",lambda e: received.append("defense"))
    install_default_rules(loop)

    dispatches = loop.publish(NSDTEvent(
        source_domain="logistics", source_id="OK-220",
        complexity=3.0, stability=7.5, tension=2.0,
        adaptability=7.0, coherence=6.5,
        stage=3, trap_score=10.0,
    ))
    assert len(dispatches) == 0
    assert len(received) == 0


def test_omega_domain_bridge_logistics():
    """LogisticsMetrics → NSDTEvent translation produces valid NSDT coordinates."""
    from luminark.sap_domain_bridge import LogisticsMetrics, logistics_to_nsdt
    m = LogisticsMetrics(
        carrier_id="TX-441", route_stops=12,
        hos_hours_remaining=1.5, on_time_pct=72.0,
        spot_vs_contract=35.0, reroute_options=1,
        eld_sync_score=60.0, weather_severity=7.0,
    )
    event = logistics_to_nsdt(m)
    for val in event.to_vector():
        assert 0.0 <= val <= 10.0, f"NSDT value {val} out of [0,10]"
    assert event.source_domain == "logistics"


def test_omega_domain_bridge_biometric():
    """BiometricMetrics → NSDTEvent produces valid coordinates."""
    from luminark.sap_domain_bridge import BiometricMetrics, biometric_to_nsdt
    m = BiometricMetrics(
        user_id="u-001", hrv_lf_hf_ratio=4.2, resting_hr=88.0,
        movement_intensity=0.8, skin_conductance=0.9,
        hrv_recovery_rate=0.2, polyvagal_tone=0.15,
    )
    event = biometric_to_nsdt(m)
    for val in event.to_vector():
        assert 0.0 <= val <= 10.0


def test_omega_history():
    """Omega Loop records dispatch history correctly."""
    from luminark.omega_loop import OmegaLoop, NSDTEvent, install_default_rules
    loop = OmegaLoop(log=False)
    loop.register("kairos", lambda e: None)
    install_default_rules(loop)

    loop.publish(NSDTEvent(
        source_domain="logistics", source_id="x",
        complexity=7.0, stability=3.0, tension=8.5,
        adaptability=2.0, coherence=4.0,
        stage=7, trap_score=65.0,
    ))
    history = loop.get_history()
    assert len(history) >= 1
    assert history[0]["source"] == "logistics"
    assert history[0]["target"] == "kairos"


# ── Runner ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import pytest
    result = pytest.main([__file__, "-v", "--tb=short"])
    sys.exit(result)
