"""
Offline + online hybrid training loop
"""

from sap_calibration_engine import SAPCalibrationEngine
import random

engine = SAPCalibrationEngine(lr=0.02)

def synthetic_sample():
    # placeholder generative structure
    x = [random.uniform(0, 10) for _ in range(5)]
    y = random.randint(0, 9)
    return x, y


for step in range(5000):
    x, y = synthetic_sample()

    out = engine.forward(x)
    engine.update(x, y)

    if step % 500 == 0:
        print(step, out["expected_stage"], out["entropy"])
