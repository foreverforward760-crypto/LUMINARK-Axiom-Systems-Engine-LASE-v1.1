"""
Frequency Adapter - Translates acoustic/resonance metrics into NSDT vector.
Agnostic of audio source; accepts standardized frequency feature dictionary.
"""

from typing import Dict, Any
from .sap_types import NSDTVector

class FrequencyAdapter:
    """
    Translates acoustic/resonance metrics into the 5-D NSDT vector.
    Accepts a standardized JSON payload (agnostic of source: voice, instrument, environment).
    """

    @staticmethod
    def from_frequency_metrics(metrics: Dict[str, Any]) -> NSDTVector:
        """
        Expected metrics keys:
        - dominant_freq_hz: float (e.g., 432.0)
        - harmonic_alignment: float (0-1, where 1 = perfect alignment to target like 432/528 Hz)
        - amplitude_variance: float (0-1, measure of volume instability)
        - signal_to_noise_db: float (SNR in dB, higher = cleaner signal)
        """
        dom_freq = metrics.get("dominant_freq_hz", 440.0)
        harmonic_ratio = metrics.get("harmonic_alignment", 0.5)
        amp_variance = metrics.get("amplitude_variance", 0.5)
        snr = metrics.get("signal_to_noise_db", 20.0)

        # Complexity: maps frequency range to 0-100 (human voice ~85-1100 Hz)
        # Normalize: 100 Hz -> 0, 1000 Hz -> 100
        complexity = min(100, max(0, (dom_freq - 100) / 9.0))

        # Coherence: directly from harmonic alignment
        coherence = harmonic_ratio * 100

        # Adaptability: harmonic alignment + SNR contribution
        adaptability = (harmonic_ratio * 80) + (min(1.0, snr / 40.0) * 20)

        # Tension: amplitude variance and poor SNR create tension
        tension = (amp_variance * 60) + (max(0, 1.0 - (snr / 30.0)) * 40)
        tension = min(100, tension)

        # Stability: inverse of tension plus SNR
        stability = 100 - (tension * 0.7) + (min(1.0, snr / 50.0) * 30)
        stability = min(100, max(0, stability))

        return NSDTVector(
            complexity=round(complexity, 2),
            stability=round(stability, 2),
            tension=round(tension, 2),
            adaptability=round(adaptability, 2),
            coherence=round(coherence, 2)
        )
