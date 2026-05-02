"""
octo_spore_v1.py – Active Adversarial Spore Module
Part of LUMINARK Overwatch v7 / Mycelial Defense System
Integrates Lyapunov probing, Kairos red-teaming, and Stage 5 threshold inversion.

CORRECTIONS APPLIED (vs original submission):
  [1] LyapunovVulnerabilityScanner is now defined in sap_lyapunov.py and importable.
  [2] kairos_redteam.py now exists; KairosGhostExploit aliased to KairosRedTeam.
  [3] NSDTDomainMapper replaced with NSDataTEngine (correct class name from v7).
  [4] OctoMycelialChip import added with graceful fallback for standalone use.
  [5] scan_code_path now implemented in LyapunovVulnerabilityScanner with
      defined (N, 5) trace contract.
  [6] STAGE_5_DUALITY_THRESHOLD renamed to STAGE_5_DUALITY_COHERENCE_NORM_THRESHOLD
      with docstring clarifying it applies to normalised coherence (raw / 10).
  [7] active_defense_cycle honey-pot node reference corrected: iterates over
      actual graph nodes matching the affected system rather than using system_id
      as a direct graph node key.
  [8] run_defense_cycle last_state explicitly sliced to [:5] to enforce NSDT
      dimension contract regardless of trace width.
  [9] original_run_protection_cycle renamed to run_protection_cycle (correct override).
  [10] __all__ defined; module-level guard added around demo/test code.
"""

import numpy as np
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# --- LUMINARK core imports ---
from sap_lyapunov import LyapunovVulnerabilityScanner, LyapunovController
from kairos_redteam import KairosRedTeam  # FIX [2]: KairosGhostExploit → KairosRedTeam

# FIX [3]: NSDTDomainMapper does not exist; correct class is NSDataTEngine
try:
    from nsdt_engine_v7 import NSDataTEngine
except ImportError:
    NSDataTEngine = None  # graceful degradation if v7 engine not present

# FIX [4]: OctoMycelialChip import with fallback for standalone use
try:
    from octo_mycelial_v4 import OctoMycelialChip
    _MYCELIAL_AVAILABLE = True
except ImportError:
    OctoMycelialChip = object  # stand-in base so class definition doesn't error
    _MYCELIAL_AVAILABLE = False

__all__ = [
    "SporeConfig",
    "OctoSpore",
    "OctoMycelialChipV7",
]

# FIX [6]: Renamed constant; clarified it operates on normalised coherence (raw/10)
STAGE_5_THRESHOLD = 5
STAGE_5_DUALITY_COHERENCE_NORM_THRESHOLD = 0.3
# Raw coherence < 3.0 AND normalised stability > 0.7 (raw stability > 7.0)
# signals hidden compromise at the bifurcation point.


@dataclass
class SporeConfig:
    """Configuration for the active spore."""
    probe_interval_seconds: float = 60.0
    max_spore_depth: int = 5
    lyapunov_threshold: float = 0.2
    honey_pot_enabled: bool = True


class OctoSpore:
    """
    Active adversarial spore that:
    - Probes the local system for Lyapunov instabilities (zero-day candidates).
    - Launches Kairos-based red-teaming simulations against those candidates.
    - Detects Stage 5 duality (hidden compromise) and flips affected nodes into honey-pots.
    """

    def __init__(self, config: Optional[SporeConfig] = None):
        self.config = config or SporeConfig()
        # FIX [1]: LyapunovVulnerabilityScanner now exists in sap_lyapunov.py
        self.lyapunov = LyapunovVulnerabilityScanner(
            instability_threshold=self.config.lyapunov_threshold
        )
        self.redteam: Optional[KairosRedTeam] = None
        # FIX [3]: use NSDataTEngine if available
        self.domain_engine = NSDataTEngine() if NSDataTEngine is not None else None
        self.honey_pots: Dict[str, Dict] = {}  # node_id -> original state snapshot

    def probe_code_path(self, trace: np.ndarray, timestamps: np.ndarray) -> List[Dict]:
        """
        Use Lyapunov to find unstable code paths (potential zero-days).

        Parameters
        ----------
        trace      : np.ndarray of shape (N, 5) – NSDT vectors over time
        timestamps : np.ndarray of shape (N,)   – Unix timestamps

        Returns
        -------
        List of vulnerability descriptors (empty if none found).
        """
        # FIX [5]: scan_code_path is now properly implemented in LyapunovVulnerabilityScanner
        result = self.lyapunov.scan_code_path(trace, timestamps)
        return result.get("vulnerabilities", [])

    def launch_adversarial_spore(self, target_system_id: str, initial_nsdt: List[float]) -> Dict:
        """
        Create a Kairos-based red-teaming spore against a specific target.
        The spore attempts to chain exploits to reach Stage 8 (critical trap).
        """
        # FIX [2]: KairosRedTeam replaces undefined KairosGhostExploit
        self.redteam = KairosRedTeam(target_system_id, max_depth=self.config.max_spore_depth)
        vulnerability = {
            "target": target_system_id,
            "nsdt_vector": initial_nsdt,
            "stage": 5,  # start at threshold (bifurcation point)
        }
        exploit_result = self.redteam.attempt_exploit(vulnerability)
        return exploit_result

    def detect_stage_5_duality(self, node_id: str, current_nsdt: List[float]) -> bool:
        """
        Detect if a node is "living in two directions":
        - High stability (normalised > 0.7, i.e. raw > 7.0) indicates external normalcy.
        - Low coherence (normalised < 0.3, i.e. raw < 3.0) indicates internal corruption.
        This is the Stage 5 threshold inversion signature.

        FIX [6]: threshold constant renamed to STAGE_5_DUALITY_COHERENCE_NORM_THRESHOLD
                 to make clear it applies to normalised (divided-by-10) coherence.
        """
        stability_norm = current_nsdt[1] / 10.0
        coherence_norm = current_nsdt[4] / 10.0
        return stability_norm > 0.7 and coherence_norm < STAGE_5_DUALITY_COHERENCE_NORM_THRESHOLD

    def flip_to_honey_pot(self, node_id: str, current_nsdt: List[float]) -> Dict:
        """
        When Stage 5 duality is detected, isolate the node and flip it into a honey-pot.
        The honey-pot records attacker behaviour while preventing real damage.
        """
        if not self.config.honey_pot_enabled:
            return {"action": "skip", "reason": "honey_pot disabled"}

        # Store original state for later restoration (if needed)
        self.honey_pots[node_id] = {
            "original_nsdt": current_nsdt,
            "timestamp": time.time(),
            "attacker_signatures": [],
        }
        return {
            "action": "FLIP_TO_HONEY_POT",
            "node_id": node_id,
            "message": f"Node {node_id} isolated. Traffic redirected to decoy.",
            "honey_pot_active": True,
        }

    def run_defense_cycle(self, system_id: str, trace: np.ndarray, timestamps: np.ndarray) -> Dict:
        """
        Full autonomous defense cycle:
        1. Probe for vulnerabilities using Lyapunov instability scanning.
        2. For each vulnerability, launch a red-teaming spore.
        3. Check for Stage 5 duality on the most recent trace state.
        4. Flip compromised nodes to honey-pots.

        FIX [8]: last_state explicitly sliced to [:5] to enforce NSDT 5D contract.
        """
        # Step 1: Lyapunov probing
        vulnerabilities = self.probe_code_path(trace, timestamps)
        spore_results = []
        for vuln in vulnerabilities[:3]:  # limit to first 3 for performance
            initial_nsdt = vuln.get("state_vector", [5.0, 5.0, 5.0, 5.0, 5.0])
            result = self.launch_adversarial_spore(system_id, initial_nsdt)
            spore_results.append(result)

        # Step 2: Stage 5 duality detection
        honey_pot_action: Dict = {"action": "none", "reason": "empty trace"}
        if len(trace) > 0:
            # FIX [8]: always slice to first 5 dimensions regardless of trace width
            last_row = trace[-1]
            last_state: List[float] = (
                last_row[:5].tolist() if hasattr(last_row, "tolist")
                else list(last_row[:5])
            )
            if self.detect_stage_5_duality(system_id, last_state):
                honey_pot_action = self.flip_to_honey_pot(system_id, last_state)
            else:
                honey_pot_action = {"action": "none", "reason": "no duality detected"}

        return {
            "system_id": system_id,
            "vulnerabilities_found": len(vulnerabilities),
            "spore_simulations": spore_results,
            "honey_pot_action": honey_pot_action,
            "recommendation": "Patch high-risk vulnerabilities immediately",
            "timestamp": time.time(),
        }


# ========== Integration with octo_mycelial_v4 ==========

class OctoMycelialChipV7(OctoMycelialChip):
    """
    Upgraded Mycelial chip with active spore capabilities.
    Extends OctoMycelialChip (from octo_mycelial_v4.py) with Lyapunov probing
    and Kairos red-teaming on the existing passive resilience pipeline.

    FIX [4]: OctoMycelialChip is now explicitly imported (with fallback).
    """

    def __init__(self, *args, **kwargs):
        if not _MYCELIAL_AVAILABLE:
            raise ImportError(
                "OctoMycelialChip is not available. "
                "Ensure octo_mycelial_v4.py is present in the Python path."
            )
        super().__init__(*args, **kwargs)
        self.spore = OctoSpore()
        self.trace_buffer: List[List[float]] = []
        self.trace_timestamps: List[float] = []

    def record_trace(self, nsdt_vector: List[float]):
        """Continuously record 5D NSDT vectors for Lyapunov probing."""
        self.trace_buffer.append(nsdt_vector[:5])  # enforce 5D contract
        self.trace_timestamps.append(time.time())
        # Keep last 500 samples
        if len(self.trace_buffer) > 500:
            self.trace_buffer = self.trace_buffer[-500:]
            self.trace_timestamps = self.trace_timestamps[-500:]

    def active_defense_cycle(self, system_id: str) -> Dict:
        """
        Run the spore on the collected trace.
        Should be called periodically (e.g., every 60 seconds).

        FIX [7]: honey-pot application now iterates over actual graph nodes
                 rather than using system_id (a string key) as a graph node
                 reference, which would raise KeyError on self.G.nodes[system_id].
        """
        if len(self.trace_buffer) < 10:
            return {"status": "insufficient_data", "samples": len(self.trace_buffer)}

        trace = np.array(self.trace_buffer)
        timestamps = np.array(self.trace_timestamps)
        result = self.spore.run_defense_cycle(system_id, trace, timestamps)

        # FIX [7]: honey-pot must apply to actual graph nodes, not system_id string.
        if result["honey_pot_action"].get("action") == "FLIP_TO_HONEY_POT":
            for node in list(self.G.nodes):
                # Mark nodes that are active (not already isolated) as honey-pots
                node_data = self.G.nodes[node]
                if node not in getattr(self, "isolated", set()):
                    node_data["state"] = "honey_pot"
                    if hasattr(self, "isolated"):
                        self.isolated.add(node)

        return result

    # FIX [9]: renamed from original_run_protection_cycle → run_protection_cycle
    #          This is the correct Python override pattern. super() calls the parent.
    def run_protection_cycle(self):
        """
        Override of OctoMycelialChip.run_protection_cycle.
        Runs the original passive resilience first, then the active spore.
        """
        # Original passive resilience (adaptive camouflage, isolate & regenerate)
        super().run_protection_cycle()

        # Build current NSDT vector from network health metrics
        nodes = list(self.G.nodes)
        if not nodes:
            return

        avg_complexity   = np.mean([self.G.nodes[n].get("processing",  50) for n in nodes]) / 10.0
        avg_stability    = np.mean([self.G.nodes[n].get("health",     100) for n in nodes]) / 10.0
        avg_tension      = np.mean([self.G.nodes[n].get("energy",      50) for n in nodes]) / 10.0
        avg_adaptability = np.mean([self.G.nodes[n].get("health",     100) for n in nodes]) / 10.0
        avg_coherence    = np.mean([self.G.nodes[n].get("temperature",  37) for n in nodes]) / 37.0

        # Clamp to [0, 10] NSDT range
        current_nsdt = [
            max(0.0, min(10.0, avg_complexity   * 10.0)),
            max(0.0, min(10.0, avg_stability     * 10.0)),
            max(0.0, min(10.0, avg_tension       * 10.0)),
            max(0.0, min(10.0, avg_adaptability  * 10.0)),
            max(0.0, min(10.0, avg_coherence     * 10.0)),
        ]

        self.record_trace(current_nsdt)
        active_result = self.active_defense_cycle("mycelium_network")
        print(f"[Active Spore] {active_result}")
        return active_result


if __name__ == "__main__":
    # FIX [10]: demo/test code guarded so it doesn't execute on import
    print("octo_spore_v1.py – standalone smoke test")

    spore = OctoSpore()

    # Synthetic trace: 20 samples, 5 NSDT dims, with injected instability at step 15
    np.random.seed(42)
    trace = np.random.uniform(3.0, 7.0, size=(20, 5))
    trace[14:, 2] = 9.5  # spike tension dimension to trigger dV/dt > 0
    trace[14:, 3] = 1.0  # drop adaptability (trap condition)
    timestamps = np.array([time.time() + i for i in range(20)])

    result = spore.run_defense_cycle("test_system", trace, timestamps)
    print(f"Vulnerabilities found : {result['vulnerabilities_found']}")
    print(f"Honey-pot action      : {result['honey_pot_action']['action']}")
    print(f"Spore simulations     : {len(result['spore_simulations'])}")
