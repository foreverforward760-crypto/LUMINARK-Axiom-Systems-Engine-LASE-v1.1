"""
kairos_redteam.py – Kairos-based adversarial red-teaming module.
Part of LUMINARK Overwatch v7 / Mycelial Defense System.

Uses the fluid, regression-aware logic of the Kairos engine to simulate
adversarial exploit chains targeting SAP stage traps (primarily Stage 8).
This replaces the placeholder KairosGhostExploit reference in octo_spore_v1.py.
"""

import numpy as np
from typing import Dict, List, Optional
from sap_energy_layer import SAPEnergy


class KairosRedTeam:
    """
    Adversarial red-team simulator built on Kairos fluid logic.
    Chains exploit attempts across SAP stages, targeting Stage 8 (critical trap).
    Uses energy field gradients to find the highest-risk attack vectors.

    This class is the production implementation of the conceptual
    KairosGhostExploit described in the v7 design documents.
    """

    def __init__(self, target_system_id: str, max_depth: int = 5):
        self.target_system_id = target_system_id
        self.max_depth = max_depth
        self.exploit_log: List[Dict] = []

    def _compute_attack_gradient(self, nsdt: List[float]) -> List[float]:
        """
        Compute energy gradient to find which NSDT dimensions are most
        exploitable (highest partial derivative of trap energy w.r.t. input).
        Uses finite differences over a uniform posterior (worst-case assumption).
        """
        posterior = np.ones(10) / 10.0  # uniform: assume attacker has no prior
        return SAPEnergy.compute_gradient(nsdt, posterior)

    def _stage_from_nsdt(self, nsdt: List[float]) -> int:
        """
        Approximate dominant SAP stage from raw NSDT without full Bayesian inference.
        Uses centroid proximity (L2 in normalised space) as a lightweight estimate.
        """
        centroids = {
            0: [0.0, 0.0, 0.0, 0.0, 0.0],
            1: [1.0, 8.0, 1.0, 1.0, 1.0],
            2: [2.0, 7.0, 2.0, 2.0, 2.0],
            3: [4.0, 7.0, 2.5, 3.0, 4.0],
            4: [3.5, 6.5, 3.0, 3.5, 5.0],
            5: [5.0, 4.0, 5.0, 5.0, 4.5],
            6: [6.0, 5.5, 4.0, 6.0, 6.5],
            7: [6.5, 3.0, 7.0, 7.0, 3.5],
            8: [7.5, 7.0, 8.0, 2.0, 2.0],
            9: [8.0, 2.0, 8.5, 1.5, 1.5],
        }
        x = np.array(nsdt) / 10.0
        best_stage, best_dist = 0, float("inf")
        for stage, centroid in centroids.items():
            dist = float(np.linalg.norm(x - np.array(centroid) / 10.0))
            if dist < best_dist:
                best_dist = dist
                best_stage = stage
        return best_stage

    def _perturb_toward_trap(self, nsdt: List[float], gradient: List[float],
                              step: float = 0.5) -> List[float]:
        """
        Move the NSDT vector in the direction of increasing energy (ascending gradient),
        simulating an attacker pushing the system toward a higher-energy trap state.
        Clamps to [0, 10] range.
        """
        perturbed = [
            max(0.0, min(10.0, nsdt[i] + step * gradient[i]))
            for i in range(5)
        ]
        return perturbed

    def attempt_exploit(self, vulnerability: Dict) -> Dict:
        """
        Simulate a Kairos-based adversarial exploit chain starting from
        the given vulnerability descriptor.

        Iterates up to max_depth steps, each time pushing the NSDT vector
        further toward Stage 8 (Illusion of Permanence trap) using the
        energy gradient as an attack guide.

        Parameters
        ----------
        vulnerability : dict with keys:
            "target"       : str  – system identifier
            "nsdt_vector"  : List[float] of length 5
            "stage"        : int  – starting SAP stage

        Returns
        -------
        dict with exploit chain, final stage, trap energy reached, and verdict.
        """
        nsdt = list(vulnerability.get("nsdt_vector", [5.0, 5.0, 5.0, 5.0, 5.0]))
        current_stage = vulnerability.get("stage", 5)
        chain = []

        for depth in range(self.max_depth):
            gradient = self._compute_attack_gradient(nsdt)
            trap_energy = SAPEnergy.trap_energy(current_stage, nsdt)
            total_energy = SAPEnergy.compute_total_energy(nsdt, np.ones(10) / 10.0)

            chain.append({
                "depth": depth,
                "stage": current_stage,
                "nsdt": [round(v, 3) for v in nsdt],
                "trap_energy": round(trap_energy, 4),
                "total_energy": round(total_energy, 4),
            })

            # Success condition: reached Stage 8 critical trap
            if current_stage == 8 and trap_energy > 0.6:
                self.exploit_log.append({
                    "target": self.target_system_id,
                    "chain": chain,
                    "result": "EXPLOIT_SUCCEEDED",
                })
                return {
                    "target": self.target_system_id,
                    "exploit_chain": chain,
                    "final_stage": current_stage,
                    "final_trap_energy": trap_energy,
                    "result": "EXPLOIT_SUCCEEDED",
                    "depth_reached": depth + 1,
                    "recommendation": "PATCH: reduce coherence sensitivity at Stage 8; increase adaptability floor.",
                }

            # Advance: perturb toward higher energy
            nsdt = self._perturb_toward_trap(nsdt, gradient, step=0.5)
            current_stage = self._stage_from_nsdt(nsdt)

        # Exploit did not reach critical trap within max_depth steps
        self.exploit_log.append({
            "target": self.target_system_id,
            "chain": chain,
            "result": "EXPLOIT_CONTAINED",
        })
        return {
            "target": self.target_system_id,
            "exploit_chain": chain,
            "final_stage": current_stage,
            "final_trap_energy": SAPEnergy.trap_energy(current_stage, nsdt),
            "result": "EXPLOIT_CONTAINED",
            "depth_reached": self.max_depth,
            "recommendation": "System resisted exploit chain. Monitor for combined-vector attacks.",
        }

    def get_exploit_log(self) -> List[Dict]:
        return self.exploit_log


# Alias for backward compatibility with any code referencing the original name
KairosGhostExploit = KairosRedTeam
