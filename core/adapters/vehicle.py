"""
LUMINARK OVERWATCH PRIME — Domain Adapter
adapters/vehicle.py — Vehicle / Fleet Telemetry → NSDT Vector

Maps J1939 / CAN bus / OBD-II vehicle telemetry to the five NSDT dimensions.
Designed for fleet health monitoring — early detection of mechanical failure.
"""
from luminark.core.schemas import NSDTVector


def vehicle_to_nsdt(
    engine_load_pct:     float,        # 0–100%
    coolant_temp_c:      float,        # degrees Celsius
    oil_pressure_psi:    float,        # PSI
    battery_voltage:     float,        # Volts (nominal 12.6V)
    fault_code_count:    int   = 0,    # Active DTC count
    brake_wear_pct:      float = 0.0,  # 0–100% worn
    transmission_temp_c: float = 80.0, # degrees Celsius
) -> NSDTVector:
    """
    Map vehicle telemetry to NSDT vector.

    NSDT mapping rationale:
      Complexity   — fault code density + multi-system interaction
      Stability    — structural integrity (oil pressure, brake wear)
      Tension      — thermal/electrical load stress
      Adaptability — operational flexibility remaining before breakdown
      Coherence    — sensor/communication integrity (voltage stability)
    """
    # Complexity: fault codes + multi-system deviation
    complexity = min(1.0, fault_code_count / 10.0 + (engine_load_pct - 50) / 200.0)
    complexity = max(0.0, complexity)

    # Stability: oil pressure health + brake wear
    oil_pressure_norm = min(1.0, max(0.0, (oil_pressure_psi - 10) / 60.0))
    brake_health      = 1.0 - brake_wear_pct / 100.0
    stability         = (oil_pressure_norm * 0.6 + brake_health * 0.4)

    # Tension: thermal stress (coolant + transmission temp)
    coolant_stress = min(1.0, max(0.0, (coolant_temp_c - 80) / 40.0))
    trans_stress   = min(1.0, max(0.0, (transmission_temp_c - 90) / 50.0))
    tension        = (coolant_stress * 0.6 + trans_stress * 0.4)

    # Adaptability: how much remaining operational capacity exists
    load_flexibility = 1.0 - engine_load_pct / 100.0
    fault_penalty    = min(1.0, fault_code_count / 5.0)
    adaptability     = max(0.0, load_flexibility * (1.0 - fault_penalty))

    # Coherence: electrical / sensor integrity
    voltage_nominal  = 12.6
    voltage_dev      = abs(battery_voltage - voltage_nominal) / voltage_nominal
    coherence        = max(0.0, 1.0 - voltage_dev * 3.0 - fault_code_count * 0.03)

    return NSDTVector(
        complexity=round(min(1.0, complexity), 4),
        stability=round(min(1.0, stability), 4),
        tension=round(min(1.0, tension), 4),
        adaptability=round(min(1.0, adaptability), 4),
        coherence=round(min(1.0, coherence), 4),
    )
