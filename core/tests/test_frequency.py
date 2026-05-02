import pytest
from luminark.frequency_calculator import FrequencyAdapter
from luminark.sap_types import NSDTVector

def test_frequency_adapter_basic():
    metrics = {
        "dominant_freq_hz": 432.0,
        "harmonic_alignment": 0.9,
        "amplitude_variance": 0.2,
        "signal_to_noise_db": 40.0
    }
    nsdt = FrequencyAdapter.from_frequency_metrics(metrics)
    assert isinstance(nsdt, NSDTVector)
    assert 0 <= nsdt.complexity <= 100
    assert nsdt.coherence > 80  # high harmonic alignment
    assert nsdt.tension < 50    # low variance, high SNR
    assert nsdt.adaptability > 70

def test_frequency_adapter_defaults():
    metrics = {}
    nsdt = FrequencyAdapter.from_frequency_metrics(metrics)
    # Should not crash; defaults produce reasonable values
    assert 0 <= nsdt.complexity <= 100
    assert 0 <= nsdt.stability <= 100

def test_frequency_extremes():
    # Very noisy, low alignment
    metrics = {
        "dominant_freq_hz": 8000.0,
        "harmonic_alignment": 0.1,
        "amplitude_variance": 0.9,
        "signal_to_noise_db": 5.0
    }
    nsdt = FrequencyAdapter.from_frequency_metrics(metrics)
    assert nsdt.complexity == 100.0  # capped
    assert nsdt.coherence < 30
    assert nsdt.tension > 60
    assert nsdt.adaptability < 40
