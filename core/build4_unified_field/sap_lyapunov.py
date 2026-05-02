"""
sap_lyapunov.py – Lyapunov stability for defense actions.
Provides a Lyapunov function V(entropy, energy, velocity) and recommends
actions that decrease V, ensuring asymptotic stability.

Also contains LyapunovVulnerabilityScanner: detects unstable code paths
(potential zero-day candidates) by finding time windows where dV/dt > 0
across recorded NSDT trace data.
"""

import numpy as np
from typing import List, Dict

class LyapunovController:
    def __init__(self, w_H: float = 1.0, w_E: float = 2.0, w_v: float = 0.5):
        """
        Weights for Lyapunov function: V = w_H * H + w_E * E + w_v * v^2
        H = entropy (nats), E = total energy (0-1), v = stage velocity
        """
        self.w_H = w_H
        self.w_E = w_E
        self.w_v = w_v

    def V(self, entropy: float, energy: float, velocity: float) -> float:
        """Compute Lyapunov function value. V >= 0, V=0 only at equilibrium."""
        return self.w_H * entropy + self.w_E * energy + self.w_v * (velocity ** 2)

    def recommend_action(self, entropy: float, energy: float, velocity: float,
                         cynical_loop_detected: bool = False) -> str:
        """
        Recommend defense action based on Lyapunov value and thresholds.
        Returns one of: "HOLD", "DAMPEN", "INTERVENE", "BREAK_PATTERN".
        """
        if cynical_loop_detected:
            return "BREAK_PATTERN"

        v_val = self.V(entropy, energy, velocity)

        if v_val > 5.0:          # high risk
            return "INTERVENE"
        elif v_val > 2.0:        # moderate risk
            return "DAMPEN"
        else:
            return "HOLD"

    def lyapunov_decrease(self, entropy_before, energy_before, velocity_before,
                          entropy_after, energy_after, velocity_after) -> float:
        """Compute actual decrease in V after an action (positive = decrease)."""
        return self.V(entropy_before, energy_before, velocity_before) - \
               self.V(entropy_after, energy_after, velocity_after)


class LyapunovVulnerabilityScanner:
    """
    Scans NSDT time-series traces for windows where the Lyapunov function V
    is increasing (dV/dt > 0), indicating instability – potential zero-day
    candidates in system behaviour.

    trace shape: (N, 5) – each row is [complexity, stability, tension,
                                        adaptability, coherence], all in [0,10].
    timestamps shape: (N,) – Unix timestamps for each sample.
    """

    def __init__(self, w_H: float = 1.0, w_E: float = 2.0, w_v: float = 0.5,
                 instability_threshold: float = 0.2):
        self.controller = LyapunovController(w_H=w_H, w_E=w_E, w_v=w_v)
        self.instability_threshold = instability_threshold

    def _nsdt_to_lyapunov_inputs(self, row: np.ndarray, velocity: float):
        """
        Map a 5D NSDT row to (entropy_proxy, energy_proxy, velocity).
        - entropy_proxy: spread of NSDT values (std as information disorder proxy)
        - energy_proxy:  mean of tension + (1 - adaptability/10) as trap energy proxy
        """
        row_norm = row / 10.0  # normalise to [0,1]
        entropy_proxy = float(np.std(row_norm))
        energy_proxy = float((row_norm[2] + (1.0 - row_norm[3])) / 2.0)
        return entropy_proxy, energy_proxy, velocity

    def scan_code_path(self, trace: np.ndarray, timestamps: np.ndarray) -> Dict:
        """
        Scan a trace for instability windows (dV/dt > 0).

        Parameters
        ----------
        trace      : np.ndarray of shape (N, 5) – NSDT vectors over time
        timestamps : np.ndarray of shape (N,)   – Unix timestamps

        Returns
        -------
        dict with keys:
            "vulnerabilities"   : list of vulnerability descriptors
            "v_series"          : list of V values at each step
            "instability_count" : number of windows with dV/dt > threshold
        """
        if trace.ndim != 2 or trace.shape[1] < 5:
            return {"vulnerabilities": [], "v_series": [], "instability_count": 0,
                    "error": "trace must have shape (N, 5)"}

        n = len(trace)
        v_series = []
        vulnerabilities = []

        # Compute V at each step
        prev_v = None
        for i in range(n):
            row = trace[i, :5]
            if i == 0:
                velocity = 0.0
            else:
                dt = max(1e-3, float(timestamps[i] - timestamps[i - 1]))
                # Stage-proxy velocity: change in mean NSDT / dt
                velocity = float(np.mean(np.abs(trace[i, :5] - trace[i - 1, :5]))) / dt

            entropy_p, energy_p, vel = self._nsdt_to_lyapunov_inputs(row, velocity)
            v_val = self.controller.V(entropy_p, energy_p, vel)
            v_series.append(round(v_val, 5))

            if prev_v is not None:
                dv = v_val - prev_v
                if dv > self.instability_threshold:
                    vulnerabilities.append({
                        "index": i,
                        "timestamp": float(timestamps[i]),
                        "dV_dt": round(dv, 5),
                        "V": round(v_val, 5),
                        "state_vector": row[:5].tolist(),
                        "severity": "HIGH" if dv > self.instability_threshold * 2 else "MODERATE",
                    })
            prev_v = v_val

        return {
            "vulnerabilities": vulnerabilities,
            "v_series": v_series,
            "instability_count": len(vulnerabilities),
        }
