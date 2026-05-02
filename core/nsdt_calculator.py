"""
NSDT Builder - Constructs 5-D vector from various domain data.
Core method from_generic() accepts agnostic metrics dict.
Domain adapters normalize to generic format before calling from_generic.
"""

from typing import Dict, Any, Optional
from .sap_types import NSDTVector

class NSDTBuilder:
    @staticmethod
    def from_generic(metrics: Dict[str, float]) -> NSDTVector:
        """
        Accepts a standardized dictionary with keys:
        complexity, stability, tension, adaptability, coherence (values 0-100).
        Missing keys default to neutral 50.
        """
        defaults = {
            "complexity": 50.0,
            "stability": 50.0,
            "tension": 50.0,
            "adaptability": 50.0,
            "coherence": 50.0
        }
        values = {k: metrics.get(k, defaults[k]) for k in defaults}
        return NSDTVector(**values)

    @staticmethod
    def from_fmcsa_and_eld(
        fmcsa_data: Dict[str, Any],
        state_data: Optional[Dict[str, Any]] = None,
        eld_data: Optional[Dict[str, Any]] = None
    ) -> NSDTVector:
        """
        Domain adapter for logistics/FMCSA + ELD data.
        Normalizes into generic metrics and delegates to from_generic.
        """
        # Complexity from violation counts
        complexity = min(100, fmcsa_data.get('violation_count', 0) * 10)

        # Stability from BASIC percentiles and ELD clock remaining
        stability = 50.0
        if 'basic_percentiles' in fmcsa_data:
            avg = sum(fmcsa_data['basic_percentiles'].values()) / len(fmcsa_data['basic_percentiles'])
            stability = max(0, 100 - avg)
        if eld_data:
            drive_rem = eld_data.get('drive_remaining', 0)
            shift_rem = eld_data.get('shift_remaining', 0)
            clock_factor = min(drive_rem, shift_rem) / 11.0 * 100
            stability = (stability * 0.5) + (clock_factor * 0.5)

        # Tension from OOS rate and ELD violations
        tension = fmcsa_data.get('oos_rate', 0) * 100
        if eld_data:
            tension += eld_data.get('violations', 0) * 15
        tension = min(100, tension)

        # Adaptability from crash preventability and ELD evasive flag
        adaptability = 100 - (fmcsa_data.get('crash_rate', 0) * 100)
        if eld_data and eld_data.get('is_evasive', False):
            adaptability *= 0.5

        # Coherence from data quality / state flags
        coherence = 80.0
        if state_data:
            coherence = state_data.get('data_quality', 80)

        generic = {
            "complexity": complexity,
            "stability": stability,
            "tension": tension,
            "adaptability": adaptability,
            "coherence": coherence
        }
        return NSDTBuilder.from_generic(generic)
