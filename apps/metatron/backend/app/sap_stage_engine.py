"""
apps/metatron/backend/app/sap_stage_engine.py
──────────────────────────────────────────────
Metatron SAP Stage Engine — Canonical Bridge v2.0
Stanfield's Axiom of Perpetuity (SAP) Framework

WIRING (LASE Task 3):
    This module now delegates canonical stage classification to
    core/luminark/engine_factory.py (EngineFactory) rather than running
    its own standalone heuristic classifier.

    The financial domain mapper (ticker_data → NSDTVector) is preserved
    and extended here.  The NSDT vector is passed to the canonical engine
    which returns a SAPAnalysisResult with stage, posterior, trap_energy,
    and risk_level.  The result dict is then translated back into the
    Metatron response format for backward compatibility.

    If core/luminark is not importable (e.g., isolated deployment),
    the module falls back to the legacy heuristic classifier.

Author : Richard L. Stanfield / MAAT (Meridian Axiom Alignment Technologies)
Contact: LuminarkMeridian@gmail.com
"""

from __future__ import annotations

import os
import sys
import logging
import numpy as np
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# ── Locate core/luminark on sys.path ─────────────────────────────────────────
_HERE      = os.path.dirname(os.path.abspath(__file__))                 # app/
_BACKEND   = os.path.dirname(_HERE)                                     # backend/
_METATRON  = os.path.dirname(_BACKEND)                                  # metatron/
_APPS      = os.path.dirname(_METATRON)                                 # apps/
_LASE_ROOT = os.path.dirname(_APPS)                                     # LASE/
_CORE_DIR  = os.path.join(_LASE_ROOT, "core")

if _CORE_DIR not in sys.path:
    sys.path.insert(0, _CORE_DIR)

# ── Try to import canonical engine ────────────────────────────────────────────
_CANONICAL_AVAILABLE = False
try:
    from luminark.engine_factory import EngineFactory, EngineConfig
    from luminark.sap_types import NSDTVector, SAP_STAGE_NAMES
    _CANONICAL_AVAILABLE = True
    logger.info("SAPStageEngine: canonical core/luminark engine loaded.")
except ImportError as e:
    logger.warning(f"SAPStageEngine: canonical engine not importable ({e}) — using legacy fallback.")


# ─────────────────────────────────────────────────────────────────────────────
# Canonical stage descriptions (constitutional constants — never alter)
# ─────────────────────────────────────────────────────────────────────────────

STAGE_DESCRIPTIONS: Dict[int, str] = {
    0: "PLENARA – Complete reset, post-crash or pre-emergence. Primordial potential.",
    1: "SPARK OF NAVIGATION – First ignition of uptrend, high uncertainty, directional clarity emerging.",
    2: "FORGE OF POLARITY – Consolidation and polarization, forming base, conflicting signals.",
    3: "ENGINE OF EXPRESSION – Breakout attempt, high volume, confident move, first self-reflection.",
    4: "CRUCIBLE OF EQUILIBRIUM – Sustainable trend, healthy pullbacks, maximum complexity threshold.",
    5: "DYNAMO OF WILL – Critical decision point, high tension, volatile. Three-way bifurcation stage.",
    6: "NEXUS OF HARMONY – Peak integration, smooth trend, low volatility, all systems synchronized.",
    7: "LENS OF DISTILLATION – Divergences appear, distribution, deep refinement and analysis.",
    8: "VESSEL OF GROUNDING – Dual-chamber trap: Illusion of Arrival (low adaptability) or "
       "Illusion of Permanence (high tension). 1.45x TrapScore amplifier active.",
    9: "TRANSPARENCY OF THE GUIDE – Climax, dissolution, blow-off or completion. Return to PLENARA.",
}


# ─────────────────────────────────────────────────────────────────────────────
# Financial domain → NSDT mapper
# ─────────────────────────────────────────────────────────────────────────────

def _map_ticker_to_nsdt(ticker_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Convert financial market data to NSDT vector on [0, 100] scale.

    This mapper is the financial domain bridge — it translates market signals
    into the five canonical SAP dimensions.  The mapping is intentionally
    conservative: it produces NSDT values that feed the canonical Bayesian
    classifier rather than directly determining stage.
    """
    price_history: list = ticker_data.get("price_history", [])
    volatility: float   = float(ticker_data.get("volatility", 30))
    rsi: float          = float(ticker_data.get("rsi", 50))
    sentiment: float    = float(ticker_data.get("sentiment_score", 0))
    pc_ratio: float     = float(ticker_data.get("put_call_ratio", 1.0))
    volume_history: list = ticker_data.get("volume_history", [])

    # Complexity — driven by volatility and trend inconsistency
    vol_complexity = min(volatility / 50.0, 1.0)  # 50% vol → max complexity
    complexity = vol_complexity * 100.0

    # Stability — inverse volatility + trend consistency bonus
    vol_stability = 1.0 - min(volatility / 50.0, 1.0)
    if len(price_history) >= 3:
        diffs = [price_history[i] - price_history[i - 1] for i in range(1, len(price_history))]
        consistency = sum(1 for d in diffs if d > 0) / len(diffs)
        vol_stability = vol_stability * 0.9 + consistency * 0.1
    stability = float(np.clip(vol_stability * 100.0, 0.0, 100.0))

    # Tension — elevated put/call ratio + high volatility
    pc_tension = min(max(pc_ratio - 0.7, 0.0) / 1.0, 1.0)  # pc_ratio 0.7→1.7 maps to 0→100
    vol_tension = min(volatility / 80.0, 1.0)
    tension = float(np.clip((pc_tension * 0.6 + vol_tension * 0.4) * 100.0, 0.0, 100.0))

    # Adaptability — sentiment + RSI space (room to move)
    sentiment_norm = (sentiment + 1.0) / 2.0  # -1..1 → 0..1
    rsi_adaptability = 1.0 - abs(rsi - 50.0) / 50.0  # RSI at 50 = max adaptability
    adaptability = float(np.clip((sentiment_norm * 0.5 + rsi_adaptability * 0.5) * 100.0, 0.0, 100.0))

    # Coherence — volume consistency + trend alignment
    if len(volume_history) >= 3:
        vol_mean = float(np.mean(volume_history))
        vol_std  = float(np.std(volume_history))
        vol_cv   = vol_std / (vol_mean + 1e-6)  # coefficient of variation
        coherence = float(np.clip((1.0 - min(vol_cv, 1.0)) * 100.0, 0.0, 100.0))
    else:
        # No volume history: infer from sentiment consistency
        coherence = float(np.clip(abs(sentiment) * 100.0, 20.0, 80.0))

    return {
        "complexity":   round(complexity,   2),
        "stability":    round(stability,    2),
        "tension":      round(tension,      2),
        "adaptability": round(adaptability, 2),
        "coherence":    round(coherence,    2),
    }


# ─────────────────────────────────────────────────────────────────────────────
# SAPStageEngine — canonical-bridged classifier
# ─────────────────────────────────────────────────────────────────────────────

class SAPStageEngine:
    """
    Stanfield's Axiom of Perpetuity — maps market data to SAP stages 0–9.

    v2.0 (LASE wiring): Delegates canonical classification to core/luminark
    EngineFactory (overwatch build).  Falls back to the legacy heuristic
    classifier if the canonical engine is unavailable.

    Inversion Principle (constitutional — never alter):
        Odd  stages → physically unstable, consciously stable
        Even stages → physically stable, consciously unstable
        Stage 0     → both low (void/crash)
        Stage 9     → climax/release (special)
    """

    STAGE_DESCRIPTIONS = STAGE_DESCRIPTIONS

    def __init__(self, build: str = "overwatch"):
        self._build = build
        self._engine = None
        if _CANONICAL_AVAILABLE:
            try:
                self._engine = EngineFactory.create(build)
                logger.info(f"SAPStageEngine: canonical engine ready (build={build})")
            except Exception as e:
                logger.warning(f"SAPStageEngine: EngineFactory.create failed ({e}) — using legacy fallback.")

    # ── Helpers (legacy fallback) ─────────────────────────────────────────────

    def _physical_stability(self, volatility: float, price_history: list) -> float:
        vol_score = 1.0 - min(volatility / 50.0, 1.0)
        if len(price_history) >= 3:
            diffs = [price_history[i] - price_history[i - 1] for i in range(1, len(price_history))]
            positive_days = sum(1 for d in diffs if d > 0)
            consistency = positive_days / len(diffs)
            vol_score = vol_score * 0.9 + consistency * 0.1
        return round(float(np.clip(vol_score, 0.0, 1.0)), 4)

    def _conscious_stability(self, sentiment: float, put_call_ratio: float, rsi: float) -> float:
        base = (sentiment + 1.0) / 2.0
        if put_call_ratio > 1.2:
            base *= 0.5
        elif put_call_ratio < 0.7:
            base = base * 0.9 + 0.1
        if rsi > 70:
            base = min(base + 0.1, 1.0)
        elif rsi < 30:
            base = max(base - 0.1, 0.0)
        return round(float(np.clip(base, 0.0, 1.0)), 4)

    def _legacy_compute_stage(self, ticker_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy heuristic fallback — only used when canonical engine unavailable."""
        price_history = ticker_data.get("price_history", [])
        volatility    = float(ticker_data.get("volatility", 30))
        rsi           = float(ticker_data.get("rsi", 50))
        sentiment     = float(ticker_data.get("sentiment_score", 0))
        pc_ratio      = float(ticker_data.get("put_call_ratio", 1.0))

        ps = self._physical_stability(volatility, price_history)
        cs = self._conscious_stability(sentiment, pc_ratio, rsi)

        composite = (ps * 0.6 + cs * 0.4) * 10
        stage = int(round(composite))
        stage = max(0, min(9, stage))

        if ps < 0.5 and cs < 0.5:
            stage = 0
        elif ps > 0.5 and cs > 0.5:
            if volatility < 15 and sentiment > 0.8:
                stage = 8
            else:
                stage = 4
        elif ps > 0.5 and cs < 0.5:
            if stage % 2 != 0:
                stage = min(stage + 1, 8)
        elif ps < 0.5 and cs > 0.5:
            if stage % 2 == 0:
                stage = min(stage + 1, 9)

        if rsi > 85 and volatility > 60 and sentiment > 0.85:
            stage = 9

        inversion_type = (
            "special" if stage in (0, 9)
            else "odd" if stage % 2 == 1
            else "even"
        )

        return {
            "stage":               stage,
            "description":         STAGE_DESCRIPTIONS.get(stage, ""),
            "physical_stability":  ps,
            "conscious_stability": cs,
            "inversion_type":      inversion_type,
            "engine":              "legacy_heuristic",
        }

    # ── Public API ────────────────────────────────────────────────────────────

    def compute_stage(self, ticker_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute the SAP stage (0–9) for a single asset.

        Delegates to core/luminark EngineFactory (overwatch build) via
        financial domain → NSDT mapping.  Falls back to legacy heuristic
        if canonical engine is unavailable.

        Expected keys in ticker_data
        ─────────────────────────────
        price_history   : list[float]  daily close prices (oldest → newest)
        volatility      : float        30-day annualised volatility (%)
        rsi             : float        latest RSI (default 50)
        sentiment_score : float        -1..1  (default 0)
        put_call_ratio  : float        (default 1.0)
        volume_history  : list[float]  optional
        """
        if self._engine is None:
            return self._legacy_compute_stage(ticker_data)

        try:
            # Map financial data → NSDT vector (canonical [0,100] scale)
            nsdt_dict = _map_ticker_to_nsdt(ticker_data)

            # Build NSDTVector for canonical engine ([0,10] scale internally)
            nsdt_vec = NSDTVector(
                complexity   = nsdt_dict["complexity"]   / 10.0,
                stability    = nsdt_dict["stability"]    / 10.0,
                tension      = nsdt_dict["tension"]      / 10.0,
                adaptability = nsdt_dict["adaptability"] / 10.0,
                coherence    = nsdt_dict["coherence"]    / 10.0,
                domain       = "financial",
            )

            result = self._engine.analyze(nsdt_vec, system_id="metatron")
            stage  = result.stage

            # Inversion type for backward compatibility
            inversion_type = (
                "special" if stage in (0, 9)
                else "odd" if stage % 2 == 1
                else "even"
            )

            return {
                "stage":               stage,
                "description":         STAGE_DESCRIPTIONS.get(stage, ""),
                "physical_stability":  round(nsdt_vec.stability, 4),
                "conscious_stability": round(nsdt_vec.coherence, 4),
                "inversion_type":      inversion_type,
                "trap_energy":         round(result.trap_energy, 4),
                "risk_level":          result.risk_level,
                "alert_color":         result.alert_color,
                "dominant_prob":       round(result.dominant_prob, 4),
                "entropy":             round(result.entropy, 4),
                "nsdt":                nsdt_dict,
                "engine":              f"canonical_{self._build}",
            }

        except Exception as e:
            logger.warning(f"SAPStageEngine canonical compute failed ({e}) — falling back to legacy.")
            return self._legacy_compute_stage(ticker_data)
