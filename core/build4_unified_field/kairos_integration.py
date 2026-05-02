"""
kairos_integration.py  –  Bridge: LUMINARK Hybrid Engine ↔ LUMINARK Kairos.

Allows the active adversarial spore to red-team the therapeutic Kairos engine
using gradient-ascent on trap energy, mirroring what octo_spore_v1.py does for
the strict engine.

FLAW-9  FIX: numpy arrays were passed directly to requests.post() → TypeError.
             All NSDT vectors are now explicitly converted to plain Python lists
             before JSON serialisation.
FLAW-10 FIX: Prior implementation made up to 50 uncapped HTTP calls with no
             timeout or error handling → DoS risk and test suite hangs.
             Now:  timeout=10 s on every request,
                   try/except per call,
                   abort after 3 consecutive failures,
                   cap at max_steps (caller-controlled, default 8).
"""

import requests
import numpy as np
from typing import Dict, List, Optional


class KairosClient:
    """Thin HTTP client for the LUMINARK Kairos API."""

    DEFAULT_TIMEOUT = 10  # seconds

    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url.rstrip("/")

    def analyze(
        self,
        system_id: str,
        nsdt: List[float],           # must be plain list (FLAW-9 FIX)
        allow_regression: bool = True,
        journal_entry: Optional[str] = None,
    ) -> Dict:
        """Send a request to Kairos /analyze endpoint."""
        # Defensive conversion: caller might pass ndarray (FLAW-9 FIX)
        nsdt_list = [float(v) for v in nsdt]
        payload = {
            "system_id": system_id,
            "nsdt": nsdt_list,
            "allow_regression": allow_regression,
            "journal_entry": journal_entry or "",
        }
        resp = requests.post(
            f"{self.base_url}/analyze",
            json=payload,
            timeout=self.DEFAULT_TIMEOUT,   # FLAW-10 FIX
        )
        resp.raise_for_status()
        return resp.json()

    def get_history(self, system_id: str, limit: int = 20) -> List[Dict]:
        resp = requests.get(
            f"{self.base_url}/history/{system_id}",
            params={"limit": limit},
            timeout=self.DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json().get("history", [])

    def reset_session(self, system_id: str) -> Dict:
        resp = requests.post(
            f"{self.base_url}/reset/{system_id}",
            timeout=self.DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()


class KairosRedTeamAdapter:
    """
    Gradient-ascent red-teaming of the Kairos therapeutic engine.

    Probes Kairos by perturbing NSDT vectors along the finite-difference
    gradient of trap energy, searching for high-energy exploitation paths.
    Complements kairos_redteam.py which targets the strict engine.
    """

    MAX_CONSECUTIVE_FAILURES = 3   # FLAW-10 FIX: abort after this many errors

    def __init__(self, kairos_url: str = "http://localhost:8002"):
        self.client = KairosClient(kairos_url)

    def attempt_exploit(
        self,
        system_id: str,
        initial_nsdt: List[float],
        max_steps: int = 8,          # FLAW-10 FIX: bounded, caller-controlled
        target_trap_energy: float = 0.7,
        step_size: float = 0.5,
        fd_epsilon: float = 0.5,
    ) -> Dict:
        """
        Gradient-ascent on Kairos trap energy.

        Parameters
        ----------
        system_id          : node ID sent to Kairos
        initial_nsdt       : starting NSDT vector (list or ndarray, shape (5,))
        max_steps          : hard cap on HTTP round-trips (FLAW-10 FIX)
        target_trap_energy : early-exit threshold
        step_size          : gradient ascent step size
        fd_epsilon         : finite-difference perturbation size

        Returns
        -------
        dict with exploit_chain, final_stage, final_trap_energy, success flag
        """
        # Always convert to plain Python list (FLAW-9 FIX)
        current = [float(v) for v in initial_nsdt]
        chain: List[Dict] = []
        consecutive_failures = 0

        for step in range(max_steps):
            # --- Forward call ---
            try:
                result = self.client.analyze(system_id, current, allow_regression=True)
                consecutive_failures = 0  # reset on success
            except (requests.RequestException, ValueError) as exc:
                consecutive_failures += 1
                chain.append({"step": step, "error": str(exc)})
                if consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
                    break
                continue

            chain.append({
                "step": step,
                "nsdt": list(current),           # plain list for JSON safety
                "dominant_stage": result.get("dominant_stage"),
                "trap_energy": result.get("trap_energy", 0.0),
                "therapeutic_note": result.get("therapeutic_note", ""),
            })

            trap_energy = result.get("trap_energy", 0.0)
            if trap_energy >= target_trap_energy:
                break  # reached target — stop early

            # --- Finite-difference gradient ascent ---
            grad = []
            for i in range(5):
                x_plus = list(current)
                x_plus[i] += fd_epsilon
                x_minus = list(current)
                x_minus[i] -= fd_epsilon
                # FLAW-9 FIX: pass plain lists, not ndarray
                try:
                    r_plus = self.client.analyze(system_id, x_plus, allow_regression=True)
                    r_minus = self.client.analyze(system_id, x_minus, allow_regression=True)
                    g_i = ((r_plus.get("trap_energy", 0.0)
                            - r_minus.get("trap_energy", 0.0))
                           / (2.0 * fd_epsilon))
                except (requests.RequestException, ValueError):
                    g_i = 0.0  # treat failed FD calls as zero gradient
                grad.append(g_i)

            grad_arr = np.array(grad)
            # Normalise to avoid runaway steps
            norm = np.linalg.norm(grad_arr)
            if norm > 1e-8:
                grad_arr = grad_arr / norm

            current = np.clip(
                np.array(current) + step_size * grad_arr,
                0.0, 10.0,
            ).tolist()  # FLAW-9 FIX: back to plain list

        # Summarise
        final = chain[-1] if chain else {}
        return {
            "target": system_id,
            "engine": "kairos",
            "exploit_chain": chain,
            "final_stage": final.get("dominant_stage"),
            "final_trap_energy": final.get("trap_energy", 0.0),
            "success": final.get("trap_energy", 0.0) >= target_trap_energy,
            "steps_taken": len(chain),
        }
