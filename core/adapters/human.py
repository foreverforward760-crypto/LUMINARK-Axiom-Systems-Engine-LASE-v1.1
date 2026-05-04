"""
LUMINARK OVERWATCH PRIME — Domain Adapter
adapters/human.py — Text / Journal → NSDT Vector

This adapter maps text input (journal entries, self-assessment responses,
organizational narratives) to the NSDT vector using keyword-based heuristics.

IMPORTANT: This adapter is for CONSUMER / RESEARCH PRODUCTS ONLY.
It is NOT used in infrastructure monitoring applications.
It lives here as a domain adapter (Layer B), completely separate from core logic.
The output of this adapter can be fed into the core engine like any other adapter.

This preserves the SAP framework's value for personal/organizational assessment
without allowing that use case to influence the predictive infrastructure engine.
"""
import re
from luminark.core.schemas import NSDTVector


# Keyword sets mapped to dimension signals
_COMPLEXITY_HIGH = [
    "chaos", "unpredictable", "complex", "multiple", "layers", "fractal",
    "network", "system", "overwhelmed", "spinning", "scattered", "fragmented",
    "competing", "conflict", "contradictory", "everything at once",
]
_COMPLEXITY_LOW = [
    "simple", "clear", "one thing", "focused", "linear", "straightforward",
    "easy", "obvious", "direct",
]

_STABILITY_HIGH = [
    "stable", "grounded", "certain", "solid", "secure", "foundation",
    "routine", "consistent", "reliable", "structure", "anchored",
]
_STABILITY_LOW = [
    "unstable", "shaky", "uncertain", "falling", "collapse", "crisis",
    "emergency", "desperate", "losing", "breaking", "failing",
]

_TENSION_HIGH = [
    "stress", "pressure", "urgent", "critical", "crisis", "threshold",
    "tension", "conflict", "anxious", "overwhelmed", "breaking point",
    "maximum", "peak", "desperate",
]
_TENSION_LOW = [
    "relaxed", "calm", "peaceful", "easy", "low pressure", "comfortable",
    "no urgency", "spacious", "flowing",
]

_ADAPTABILITY_HIGH = [
    "flexible", "adapt", "change", "navigate", "learn", "both", "pivot",
    "simultaneously", "multiple perspectives", "shifting", "open",
    "resourceful", "creative", "find a way",
]
_ADAPTABILITY_LOW = [
    "stuck", "rigid", "cannot change", "no options", "trapped", "locked",
    "fixed", "immovable", "no way out", "same", "repeating",
]

_COHERENCE_HIGH = [
    "clear", "aligned", "unified", "coherent", "purpose", "mission",
    "harmony", "integrated", "whole", "together", "connected",
]
_COHERENCE_LOW = [
    "confused", "lost", "disconnected", "fragmented", "scattered",
    "no direction", "incoherent", "mixed signals", "unclear",
]


def _keyword_score(text: str, high_words: list, low_words: list, base: float = 0.4) -> float:
    """Score a dimension from 0–1 based on keyword presence."""
    text_lower = text.lower()
    high_hits = sum(1 for w in high_words if w in text_lower)
    low_hits  = sum(1 for w in low_words  if w in text_lower)

    score = base + (high_hits * 0.08) - (low_hits * 0.08)

    # Structural complexity: longer sentences / more words = higher complexity signal
    word_count  = len(text.split())
    avg_wl = sum(len(w) for w in text.split()) / max(word_count, 1)
    struct_signal = min(0.2, (avg_wl - 4) * 0.03 + word_count / 500.0)

    return round(min(1.0, max(0.0, score + struct_signal * 0.3)), 4)


def text_to_nsdt(text: str) -> NSDTVector:
    """
    Convert free text to an NSDT vector using keyword heuristics.

    This is an approximation — appropriate for consumer/research tools,
    NOT for infrastructure monitoring which requires actual sensor telemetry.
    """
    if not text or len(text.strip()) < 5:
        # Return baseline undifferentiated vector
        return NSDTVector(complexity=0.4, stability=0.5, tension=0.4,
                          adaptability=0.5, coherence=0.5)

    return NSDTVector(
        complexity=   _keyword_score(text, _COMPLEXITY_HIGH,   _COMPLEXITY_LOW,   base=0.30),
        stability=    _keyword_score(text, _STABILITY_HIGH,    _STABILITY_LOW,    base=0.50),
        tension=      _keyword_score(text, _TENSION_HIGH,      _TENSION_LOW,      base=0.35),
        adaptability= _keyword_score(text, _ADAPTABILITY_HIGH, _ADAPTABILITY_LOW, base=0.45),
        coherence=    _keyword_score(text, _COHERENCE_HIGH,    _COHERENCE_LOW,    base=0.50),
    )
