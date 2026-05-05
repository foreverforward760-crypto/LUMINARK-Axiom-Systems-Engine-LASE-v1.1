"""
kairos_integration.py – Bridge between LUMINARK Hybrid Engine and LUMINARK Kairos.

Allows the active adversarial spore to target Kairos (therapeutic engine) as well
as the strict industrial engine.

FLAW CORRECTIONS (vs submitted document):
  [9]  KairosRedTeamAdapter.attempt_exploit() passed numpy arrays to
       client.analyze() — requests.post() cannot JSON-serialize np.ndarray.
       Fixed: .tolist() applied before all API calls.
  [10] The finite-difference loop made up to 50 HTTP calls with no timeout or
       error handling — a DoS risk against the target.
       Fixed: timeout parameter added to all requests; try/except around each
       call; per-step error logged and loop aborted on repeated failure.
"""

import requests
import numpy as np
from typing import Dict, List, Optional


class KairosClient:
    """
    HTTP client for LUMINARK Kairos API (build2_kairos / separate Kairos repo).

    Parameters
    ----------
    base_url : str — base URL of the Kairos API (default http://localhost:8002)
    timeout  : float — request timeout in seconds (default 5.0)
    """

    def __init__(self, base_url: str = "http://localhost:8002",
                 timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def analyze(self, system_id: str, nsdt: List[float],
                allow_regression: bool = True,
                journal_entry: Optional[str] = None) -> Dict:
        """Send NSDT vector to Kairos /analyze endpoint."""
        # FIX [9]: ensure nsdt is a plain Python list, not a numpy array
        nsdt_list = [float(v) for v in nsdt]
        payload = {
            "system_id": system_id,
            "nsdt": nsdt_list,
            "allow_regression": allow_regression,
            "journal_entry": journal_entry or "",
        }
        response = requests.post(
            f"{self.base_url}/analyze",
            json=payload,
            timeout=self.timeout,  # FIX [10]
        )
        response.raise_for_status()
        return response.json()

    def get_history(self, system_id: str, limit: int = 20) -> List[Dict]:
        response = requests.get(
            f"{self.base_url}/history/{system_id}",
            params={"limit": limit},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json().get("history", [])

    def reset_session(self, system_id: str) -> Dict:
        response = requests.post(
            f"{self.base_url}/reset/{system_id}",
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def health(self) -> bool:
        """Return True if Kairos is reachable and healthy."""
        try:
            r = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            return r.status_code == 200
        except requests.RequestException:
            return False


class KairosRedTeamAdapter:
    """
    Adversarial red-team adapter that targets a live Kairos instance.
    Uses gradient ascent over trap energy to push the system toward Stage 8.

    This complements kairos_redteam.py (which works offline on the strict engine).
    Use this when you need to probe a running Kairos deployment.

    Parameters
    ----------
    kairos_url : str — base URL of the target Kairos API
    timeout    : float — per-request timeout in seconds (default 5.0)

    Rate note: each exploit step makes at most 2×5+1 = 11 HTTP calls.
    With max_steps=5 that is up to 55 calls. Use responsibly — set appropriate
    timeout and ensure you have authorisation to test the target.
    """

    def __init__(self, kairos_url: str = "http://localhost:8002",
                 timeout: float = 5.0):
        self.client = KairosClient(kairos_url, timeout=timeout)

    def _finite_diff_gradient(self, system_id: str, nsdt: List[float],
                               epsilon: float = 0.5) -> Optional[np.ndarray]:
        """
        Estimate gradient of trap_energy w.r.t. nsdt via finite differences.
        Returns None if any HTTP call fails.

        FIX [9]: all lists converted to plain float lists before API calls.
        FIX [10]: errors caught and None returned to abort step gracefully.
        """
        grad = []
        for i in range(5):
            try:
                x_plus = [float(v) for v in nsdt]
                x_plus[i] = min(10.0, x_plus[i] + epsilon)
                r_plus = self.client.analyze(system_id, x_plus)

                x_minus = [float(v) for v in nsdt]
                x_minus[i] = max(0.0, x_minus[i] - epsilon)
                r_minus = self.client.analyze(system_id, x_minus)

                dE = (r_plus.get("trap_energy", 0.0) -
                      r_minus.get("trap_energy", 0.0))
                grad.append(dE / (2.0 * epsilon))
            except requests.RequestException as e:
                print(f"[KairosRedTeamAdapter] HTTP error at dim {i}: {e}")
                return None
        return np.array(grad)

    def attempt_exploit(self, system_id: str, initial_nsdt: List[float],
                        max_steps: int = 5,
                        step_size: float = 0.5,
                        trap_threshold: float = 0.6) -> Dict:
        """
        Probe a live Kairos instance with gradient ascent on trap energy,
        targeting Stage 8 (Illusion of Permanence).

        Parameters
        ----------
        system_id     : str — Kairos session identifier
        initial_nsdt  : List[float] — starting NSDT vector (5 values, [0,10])
        max_steps     : int — maximum gradient steps (default 5)
        step_size     : float — gradient ascent step size (default 0.5)
        trap_threshold: float — trap_energy level considered successful (default 0.6)

        Returns
        -------
        dict with exploit chain, final stage, final trap energy, and success flag.
        """
        # FIX [9]: ensure list of plain floats
        current_nsdt = [float(v) for v in initial_nsdt]
        chain = []
        consecutive_errors = 0
        max_consecutive_errors = 3

        for step in range(max_steps):
            # FIX [10]: error handling around each step
            try:
                result = self.client.analyze(system_id, current_nsdt,
                                             allow_regression=True)
            except requests.RequestException as e:
                print(f"[KairosRedTeamAdapter] Step {step} analyze failed: {e}")
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    break
                continue

            consecutive_errors = 0
            trap_energy = float(result.get("trap_energy", 0.0))
            chain.append({
                "step": step,
                "nsdt": [round(v, 3) for v in current_nsdt],
                "dominant_stage": result.get("dominant_stage"),
                "trap_energy": round(trap_energy, 4),
                "therapeutic_note": result.get("therapeutic_note", ""),
            })

            # Success: reached high-trap state
            if trap_energy > trap_threshold:
                break

            # Gradient ascent toward higher trap energy
            grad = self._finite_diff_gradient(system_id, current_nsdt)
            if grad is None:
                print(f"[KairosRedTeamAdapter] Gradient failed at step {step}, aborting.")
                break

            # FIX [9]: clip returns ndarray; convert to plain list
            current_nsdt = np.clip(
                np.array(current_nsdt) + step_size * grad,
                0.0, 10.0
            ).tolist()  # ← .tolist() ensures JSON-serializable

        final = chain[-1] if chain else {
            "dominant_stage": None, "trap_energy": 0.0
        }
        return {
            "target": system_id,
            "engine": "kairos",
            "exploit_chain": chain,
            "final_stage": final.get("dominant_stage"),
            "final_trap_energy": final.get("trap_energy", 0.0),
            "success": final.get("trap_energy", 0.0) > trap_threshold,
            "steps_taken": len(chain),
        }
