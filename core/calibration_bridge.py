"""
calibration_bridge.py
─────────────────────
LUMINARK Axiom Systems Engine — Calibration Bridge v1.0
Stanfield's Axiom of Perpetuity (SAP) Framework

Wires the UpdateAndRestoredOverwatch v5 adaptive calibration layer
(SAPCalibrationEngine) into the core luminark engine factory.

The calibration layer provides:
  - Online Bayesian centroid learning from confirmed stage labels
  - Temperature self-tuning (reduces overconfidence over time)
  - Stability penalty enforcement (prevents manifold collapse)
  - Expected-stage soft output for hybrid classification

USAGE (from engine_factory.py or any calling code):
    from calibration_bridge import CalibrationBridge, get_calibration_bridge

    bridge = get_calibration_bridge()

    # Inference — get calibrated stage probabilities
    result = bridge.forward([complexity, stability, tension, adaptability, coherence])
    # { "probs": [...x10], "expected_stage": float, "entropy": float }

    # After confirmed classification — online update
    bridge.update([...nsdt...], confirmed_stage=8)

    # Save learned parameters
    bridge.save("runtime/calibration/learned.json")

INTEGRATION with EngineFactory:
    The factory passes calibrated expected_stage as a Bayesian prior.
    See engine_factory.py — create_engine(build, calibrate=True).

Author : Richard L. Stanfield / MAAT (Meridian Axiom Alignment Technologies)
Contact: LuminarkMeridian@gmail.com
"""

from __future__ import annotations

import os
import sys
import json
import logging
from typing import List, Optional, Dict, Any

import numpy as np

logger = logging.getLogger(__name__)

# ── Locate runtime/calibration/ relative to LASE repo root ───────────────────
_HERE      = os.path.dirname(os.path.abspath(__file__))
_CORE_ROOT = _HERE                                          # core/ = here
_LASE_ROOT = os.path.dirname(_CORE_ROOT)                   # LASE/ parent
_CALIB_DIR = os.path.join(_LASE_ROOT, "runtime", "calibration")
if _CALIB_DIR not in sys.path:
    sys.path.insert(0, _CALIB_DIR)

# ── Canonical stage centroids — [complexity, stability, tension, adaptability, coherence]
# Values on [0, 10] (luminark native scale). These are the initial centroids;
# the calibration engine updates them online from confirmed stage observations.
_DEFAULT_CENTROIDS = np.array([
    [0.0, 0.0, 0.0, 0.0, 0.0],   # 0  PLENARA
    [1.0, 8.0, 1.0, 1.0, 1.0],   # 1  SPARK OF NAVIGATION
    [2.0, 7.0, 2.0, 2.0, 2.0],   # 2  FORGE OF POLARITY
    [4.0, 7.0, 2.5, 3.0, 4.0],   # 3  ENGINE OF EXPRESSION
    [3.5, 6.5, 3.0, 3.5, 5.0],   # 4  CRUCIBLE OF EQUILIBRIUM
    [5.0, 4.0, 5.0, 5.0, 4.5],   # 5  DYNAMO OF WILL
    [6.0, 5.5, 4.0, 6.0, 6.5],   # 6  NEXUS OF HARMONY
    [6.5, 3.0, 7.0, 7.0, 3.5],   # 7  LENS OF DISTILLATION
    [7.5, 7.0, 8.0, 2.0, 2.0],   # 8  VESSEL OF GROUNDING
    [8.0, 2.0, 8.5, 1.5, 1.5],   # 9  TRANSPARENCY OF THE GUIDE
], dtype=float)

_DEFAULT_WEIGHTS     = np.array([1.0, 1.5, 1.5, 1.0, 0.8], dtype=float)
_DEFAULT_TEMPERATURE = 1.0


class CalibrationBridge:
    """
    Adapter between the LUMINARK engine factory and the v5 calibration engine.

    Falls back to a clean numpy implementation if runtime/calibration/ is not
    importable (test environments, clean installs).
    """

    def __init__(
        self,
        lr: float = 0.01,
        stability_lambda: float = 0.1,
        learned_path: Optional[str] = None,
    ):
        self._use_native = False
        self._engine     = None

        try:
            from sap_calibration_engine import SAPCalibrationEngine
            self._engine     = SAPCalibrationEngine(lr=lr, stability_lambda=stability_lambda)
            self._use_native = True
            logger.info("CalibrationBridge: native SAPCalibrationEngine loaded.")
        except ImportError:
            logger.info(
                "CalibrationBridge: runtime/calibration not importable — "
                "using embedded fallback calibrator."
            )
            self._centroids   = _DEFAULT_CENTROIDS.copy()
            self._weights     = _DEFAULT_WEIGHTS.copy()
            self._temperature = _DEFAULT_TEMPERATURE
            self._lr          = lr

        if learned_path and os.path.exists(learned_path):
            self.load(learned_path)

    # ── Inference ─────────────────────────────────────────────────────────────

    def forward(self, nsdt_list: List[float]) -> Dict[str, Any]:
        """
        Run calibrated forward pass.

        Parameters
        ----------
        nsdt_list : [complexity, stability, tension, adaptability, coherence]
                    All values on luminark native scale [0, 10].

        Returns
        -------
        dict with keys:
            probs          : List[float] — posterior over 10 stages (sums to 1.0)
            expected_stage : float       — soft weighted expected stage
            entropy        : float       — distribution entropy (higher = less certain)
        """
        x = np.array(nsdt_list, dtype=float)
        if self._use_native:
            return self._engine.forward(x)
        return self._fallback_forward(x)

    def update(self, nsdt_list: List[float], confirmed_stage: int) -> None:
        """
        Online learning step — update centroids toward a confirmed stage.

        Call after forensic audit confirmation, retrospective batch validation,
        or domain-expert review.

        Parameters
        ----------
        nsdt_list       : NSDT vector on [0, 10]
        confirmed_stage : int [0-9] — the verified true SAP stage
        """
        x = np.array(nsdt_list, dtype=float)
        if self._use_native:
            self._engine.update(x, confirmed_stage)
            return
        self._fallback_update(x, confirmed_stage)

    def predict_stage(self, nsdt_list: List[float]) -> int:
        """Return the MAP (maximum a posteriori) stage integer."""
        p = np.array(self.forward(nsdt_list)["probs"])
        return int(np.argmax(p))

    def stage_confidence(self, nsdt_list: List[float]) -> float:
        """Return the probability mass of the MAP stage (0.0–1.0)."""
        p = np.array(self.forward(nsdt_list)["probs"])
        return float(p.max())

    # ── Persistence ───────────────────────────────────────────────────────────

    def save(self, path: str) -> None:
        """Serialize learned parameters to JSON."""
        if self._use_native:
            params = self._engine.params
            data = {
                "centroids":   params.centroids.tolist(),
                "temperature": float(params.temperature),
                "source":      "native_SAPCalibrationEngine_v5",
            }
        else:
            data = {
                "centroids":   self._centroids.tolist(),
                "temperature": float(self._temperature),
                "source":      "LASE_fallback_calibrator",
            }

        dirpath = os.path.dirname(path)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"CalibrationBridge: parameters saved → {path}")

    def load(self, path: str) -> None:
        """Load serialized parameters from JSON."""
        with open(path, "r") as f:
            data = json.load(f)

        centroids   = np.array(data["centroids"], dtype=float)
        temperature = float(data.get("temperature", _DEFAULT_TEMPERATURE))

        if self._use_native:
            self._engine.params.centroids   = centroids
            self._engine.params.temperature = temperature
            self._engine.model = type(self._engine.model)(self._engine.params)
        else:
            self._centroids   = centroids
            self._temperature = temperature

        logger.info(f"CalibrationBridge: parameters loaded ← {path}")

    # ── Fallback implementation ────────────────────────────────────────────────

    def _softmin_probs(self, x: np.ndarray) -> np.ndarray:
        diffs     = self._centroids - x
        weighted  = (diffs ** 2) * self._weights
        distances = np.sqrt(weighted.sum(axis=1))
        d         = distances - distances.min()
        exp       = np.exp(-d / max(self._temperature, 1e-6))
        return exp / exp.sum()

    def _fallback_forward(self, x: np.ndarray) -> Dict[str, Any]:
        p        = self._softmin_probs(x)
        expected = float(np.sum(np.arange(10) * p))
        entropy  = float(-np.sum(p * np.log(p + 1e-12)))
        return {"probs": p.tolist(), "expected_stage": expected, "entropy": entropy}

    def _fallback_update(self, x: np.ndarray, true_stage: int) -> None:
        p = self._softmin_probs(x)
        for i in range(10):
            error = p[i] - (1.0 if i == true_stage else 0.0)
            self._centroids[i] -= self._lr * error * (x - self._centroids[i])
        # Stability penalty — prevent centroid manifold collapse
        for i in range(9):
            diff = self._centroids[i + 1] - self._centroids[i]
            if np.linalg.norm(diff) < 0.3:
                self._centroids[i + 1] += 0.05 * diff


# ── Singleton accessor ────────────────────────────────────────────────────────

_bridge_instance: Optional[CalibrationBridge] = None


def get_calibration_bridge(learned_path: Optional[str] = None) -> CalibrationBridge:
    """
    Return the shared CalibrationBridge singleton.
    Thread-safe for read-heavy workloads; single writer assumed.
    """
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = CalibrationBridge(learned_path=learned_path)
    return _bridge_instance


def run_batch_update(
    bridge: CalibrationBridge,
    records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Batch calibration update from retrospective validation data.

    Parameters
    ----------
    bridge  : CalibrationBridge
    records : List of dicts, each:
                "nsdt"  : [complexity, stability, tension, adaptability, coherence]
                "stage" : int — confirmed true stage

    Returns
    -------
    dict: { "records_updated": int, "final_entropy": float }
    """
    updated = 0
    final_entropy = 0.0

    for rec in records:
        nsdt  = rec.get("nsdt", [])
        stage = rec.get("stage")
        if len(nsdt) == 5 and stage is not None:
            bridge.update(nsdt, int(stage))
            r = bridge.forward(nsdt)
            final_entropy = r["entropy"]
            updated += 1

    logger.info(f"CalibrationBridge batch update: {updated} records processed.")
    return {"records_updated": updated, "final_entropy": round(final_entropy, 4)}
