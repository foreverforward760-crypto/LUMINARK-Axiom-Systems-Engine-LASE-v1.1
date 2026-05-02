"""
Validation Suite v8.1.0 — LuminarkHybridEngine
Synthetic data generator and end-to-end validation for all SAP stages.
Author: Richard Stanfield, MAAT
"""

import random
from luminark.sap_types import NSDTVector, SAPStage, SystemState
from luminark.inversion_analyzer import InversionAnalyzer
from luminark.dissolution import DissolutionEngine
from luminark.frequency_calculator import FrequencyAdapter
from luminark.nsdt_calculator import NSDTBuilder

# ─────────────────────────────────────────────
# Synthetic Data Generators
# ─────────────────────────────────────────────

def gen_stage9_ready() -> NSDTVector:
    """Generate NSDT vector that should trigger Stage 9 + dissolution."""
    return NSDTVector(
        complexity=random.uniform(0, 20),
        stability=random.uniform(50, 70),
        tension=random.uniform(0, 20),
        adaptability=random.uniform(80, 100),
        coherence=random.uniform(95, 100)
    )

def gen_trap_state() -> NSDTVector:
    """Generate NSDT vector that should trigger a trap (Unity + low adaptability)."""
    return NSDTVector(
        complexity=random.uniform(40, 60),
        stability=random.uniform(65, 80),
        tension=random.uniform(30, 50),
        adaptability=random.uniform(0, 29),
        coherence=random.uniform(60, 80)
    )

def gen_threshold_crisis() -> NSDTVector:
    """Generate NSDT vector at threshold with high tension."""
    return NSDTVector(
        complexity=random.uniform(60, 90),
        stability=random.uniform(20, 45),
        tension=random.uniform(82, 100),
        adaptability=random.uniform(40, 60),
        coherence=random.uniform(65, 80)
    )

def gen_random_vector() -> NSDTVector:
    """Generate a completely random NSDT vector."""
    return NSDTVector(
        complexity=random.uniform(0, 100),
        stability=random.uniform(0, 100),
        tension=random.uniform(0, 100),
        adaptability=random.uniform(0, 100),
        coherence=random.uniform(0, 100)
    )

def gen_fmcsa_sample(risk_level: str = "medium") -> NSDTVector:
    """Generate NSDT from synthetic FMCSA carrier data."""
    if risk_level == "low":
        fmcsa = {"violation_count": 0, "oos_rate": 0.02, "crash_rate": 0.01,
                 "basic_percentiles": {"HOS": 20, "Vehicle": 15, "Driver": 10}}
        eld = {"drive_remaining": 10.0, "shift_remaining": 12.0, "violations": 0, "is_evasive": False}
    elif risk_level == "high":
        fmcsa = {"violation_count": 8, "oos_rate": 0.45, "crash_rate": 0.15,
                 "basic_percentiles": {"HOS": 85, "Vehicle": 90, "Driver": 75}}
        eld = {"drive_remaining": 1.5, "shift_remaining": 2.0, "violations": 3, "is_evasive": True}
    else:  # medium
        fmcsa = {"violation_count": 3, "oos_rate": 0.12, "crash_rate": 0.05,
                 "basic_percentiles": {"HOS": 55, "Vehicle": 48, "Driver": 42}}
        eld = {"drive_remaining": 6.0, "shift_remaining": 8.0, "violations": 1, "is_evasive": False}
    return NSDTBuilder.from_fmcsa_and_eld(fmcsa, eld_data=eld)

def gen_frequency_sample(profile: str = "balanced") -> NSDTVector:
    """Generate NSDT from synthetic frequency/resonance data."""
    profiles = {
        "harmonized": {"dominant_freq_hz": 432.0, "harmonic_alignment": 0.92,
                       "amplitude_variance": 0.15, "signal_to_noise_db": 42.0},
        "distressed":  {"dominant_freq_hz": 680.0, "harmonic_alignment": 0.22,
                        "amplitude_variance": 0.85, "signal_to_noise_db": 8.0},
        "balanced":    {"dominant_freq_hz": 528.0, "harmonic_alignment": 0.65,
                        "amplitude_variance": 0.35, "signal_to_noise_db": 28.0},
    }
    return FrequencyAdapter.from_frequency_metrics(profiles.get(profile, profiles["balanced"]))


# ─────────────────────────────────────────────
# Validation Tests
# ─────────────────────────────────────────────

def run_validation():
    passed = 0
    failed = 0
    results = []

    def check(name, condition, detail=""):
        nonlocal passed, failed
        status = "PASS" if condition else "FAIL"
        if condition:
            passed += 1
        else:
            failed += 1
        results.append(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))

    print("\n" + "="*60)
    print("  LuminarkHybridEngine v8.1.0 — Validation Suite")
    print("="*60)

    # ── Test Group 1: Dissolution ──
    print("\n[1] Dissolution Engine")
    for i in range(5):
        nsdt = gen_stage9_ready()
        state = InversionAnalyzer.compute_stage(nsdt)
        check(
            f"Stage9→VOID dissolution run {i+1}",
            state.stage == SAPStage.VOID,
            f"stage={state.stage}"
        )

    # ── Test Group 2: Trap Detection ──
    print("\n[2] Trap Detection")
    for i in range(5):
        nsdt = gen_trap_state()
        state = InversionAnalyzer.compute_stage(nsdt)
        check(
            f"Trap detection run {i+1}",
            state.is_trap,
            f"stage={state.stage} adaptability={nsdt.adaptability:.1f}"
        )

    # ── Test Group 3: Threshold / Crisis ──
    print("\n[3] Threshold Crisis")
    for i in range(3):
        nsdt = gen_threshold_crisis()
        state = InversionAnalyzer.compute_stage(nsdt)
        check(
            f"Threshold crisis run {i+1}",
            "PIVOT" in state.recommended_action or state.stage == SAPStage.THRESHOLD,
            f"action={state.recommended_action}"
        )

    # ── Test Group 4: FMCSA Domain ──
    print("\n[4] FMCSA Carrier Risk")
    for level in ["low", "medium", "high"]:
        nsdt = gen_fmcsa_sample(level)
        state = InversionAnalyzer.compute_stage(nsdt)
        check(
            f"FMCSA {level} risk",
            0 <= state.unified_field_value <= 1,
            f"U={state.unified_field_value:.3f} stage={state.stage}"
        )

    # ── Test Group 5: Frequency Domain ──
    print("\n[5] Frequency / Bio-Resonance")
    for profile in ["harmonized", "balanced", "distressed"]:
        nsdt = gen_frequency_sample(profile)
        state = InversionAnalyzer.compute_stage(nsdt)
        check(
            f"Frequency {profile}",
            0 <= state.unified_field_value <= 1,
            f"U={state.unified_field_value:.3f} stage={state.stage}"
        )

    # ── Test Group 6: Random Stress ──
    print("\n[6] Random Stress (50 vectors)")
    crash_count = 0
    for i in range(50):
        try:
            nsdt = gen_random_vector()
            state = InversionAnalyzer.compute_stage(nsdt)
            assert 0 <= state.unified_field_value <= 1
        except Exception as e:
            crash_count += 1
    check("No crashes on 50 random vectors", crash_count == 0, f"crashes={crash_count}")

    # ── Print Results ──
    print()
    for r in results:
        print(r)

    total = passed + failed
    print(f"\n{'='*60}")
    print(f"  TOTAL: {passed}/{total} passed  |  {failed} failed")
    print(f"{'='*60}\n")

    return failed == 0


if __name__ == "__main__":
    success = run_validation()
    exit(0 if success else 1)
