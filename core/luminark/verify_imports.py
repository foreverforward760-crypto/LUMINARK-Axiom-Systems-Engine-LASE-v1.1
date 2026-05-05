"""
verify_imports.py — LuminarkHybridEngine v8.1.0
Verifies all modules import cleanly before committing.
"""

import sys

modules = [
    ("luminark.sap_types",          ["SAPStage", "NSDTVector", "SystemState"]),
    ("luminark.inversion_analyzer", ["InversionAnalyzer"]),
    ("luminark.nsdt_calculator",    ["NSDTBuilder"]),
    ("luminark.dissolution",        ["DissolutionEngine"]),
    ("luminark.frequency_calculator", ["FrequencyAdapter"]),
    ("luminark.engine_factory",     ["EngineFactory", "EngineConfig"]),
]

# Optional modules (may not exist in all builds)
optional_modules = [
    ("luminark.recalibration",      ["RecalibrationEngine"]),
    ("luminark.unified_field",      ["UnifiedField"]),
]

passed = 0
failed = 0

print("\n" + "="*55)
print("  LuminarkHybridEngine v8.1.0 — Import Verification")
print("="*55)

def check_module(mod_name, symbols, required=True):
    global passed, failed
    try:
        mod = __import__(mod_name, fromlist=symbols)
        for sym in symbols:
            assert hasattr(mod, sym), f"Missing symbol: {sym}"
        print(f"  [PASS] {mod_name}")
        passed += 1
    except Exception as e:
        tag = "FAIL" if required else "WARN"
        print(f"  [{tag}] {mod_name} — {e}")
        if required:
            failed += 1

print("\nRequired Modules:")
for mod, syms in modules:
    check_module(mod, syms, required=True)

print("\nOptional Modules:")
for mod, syms in optional_modules:
    check_module(mod, syms, required=False)

print(f"\n{'='*55}")
print(f"  Result: {passed}/{passed+failed} required modules OK")
print(f"{'='*55}\n")

sys.exit(0 if failed == 0 else 1)
