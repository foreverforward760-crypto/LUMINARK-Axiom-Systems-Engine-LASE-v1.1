"""
LUMINARK OVERWATCH PRIME — Core Engine v1.0
temporal.py — Trajectory detection and temporal state analysis

PROTECTED MODULE.

The Temporal State Engine is the feature that separates LUMINARK from a
simple calculator. Without it, the system only knows where a system IS.
With it, the system knows where the system is GOING.

Trajectory States:
  ASCENDING    — Stage values consistently increasing (system deteriorating)
  DESCENDING   — Stage values consistently decreasing (system recovering)
  OSCILLATING  — Stage oscillating — unstable, unpredictable
  STABLE       — Stage roughly constant

Yunus Trajectory Trigger (sustained rigidity detection):
  Fires when: 3+ consecutive readings at stage >= 7
  AND adaptability trend is declining
  This is the Stage 8 trap signature — false confidence + declining flexibility
"""
from typing import List
from .schemas import NSDTVector, TrajectoryResult


# Minimum history length to compute trajectory
MIN_HISTORY = 2
YUNUS_WINDOW = 3        # consecutive high-stage readings required
YUNUS_HIGH_STAGE = 7    # stage threshold for Yunus trigger


def detect_trajectory(history: List[NSDTVector], stage_history: List[int] | None = None) -> TrajectoryResult:
    """
    Analyze NSDT history to determine trajectory direction.

    Args:
        history:       List of NSDTVector (oldest first, newest last)
        stage_history: Optional list of classified stages matching history

    Returns:
        TrajectoryResult with state, confidence, and window size
    """
    window = len(history)

    if window < MIN_HISTORY:
        return TrajectoryResult(state="STABLE", confidence=0.5, window=window)

    # Use last 5 readings for trajectory (or all if fewer)
    recent = history[-5:]

    if len(recent) < 2:
        return TrajectoryResult(state="STABLE", confidence=0.5, window=window)

    prev = recent[-2]
    curr = recent[-1]

    # Dimension-by-dimension delta
    dims = ["complexity", "stability", "tension", "adaptability", "coherence"]
    delta = [getattr(curr, d) - getattr(prev, d) for d in dims]

    # Weight: stability and adaptability matter most for trajectory
    weights = [0.15, 0.30, 0.20, 0.25, 0.10]
    weighted_delta = sum(w * d for w, d in zip(weights, delta))

    inc_count = sum(1 for d in delta if d > 0.02)
    dec_count = sum(1 for d in delta if d < -0.02)

    # For multi-step history, also check monotonic trend
    if len(recent) >= 3:
        complexity_trend  = [v.complexity for v in recent]
        stability_trend   = [v.stability  for v in recent]
        adaptability_trend = [v.adaptability for v in recent]

        # Is stability consistently declining?
        stability_declining = all(
            stability_trend[i] > stability_trend[i+1]
            for i in range(len(stability_trend)-1)
        )
        # Is complexity consistently rising?
        complexity_rising = all(
            complexity_trend[i] < complexity_trend[i+1]
            for i in range(len(complexity_trend)-1)
        )

        if stability_declining and complexity_rising:
            return TrajectoryResult(state="ASCENDING", confidence=0.92, window=window)

        stability_recovering = all(
            stability_trend[i] < stability_trend[i+1]
            for i in range(len(stability_trend)-1)
        )
        if stability_recovering:
            return TrajectoryResult(state="DESCENDING", confidence=0.88, window=window)

    # Fallback to single-step delta
    if inc_count >= 4:
        return TrajectoryResult(state="ASCENDING", confidence=0.80, window=window)
    elif dec_count >= 4:
        return TrajectoryResult(state="DESCENDING", confidence=0.80, window=window)
    elif inc_count >= 2 and dec_count >= 2:
        return TrajectoryResult(state="OSCILLATING", confidence=0.70, window=window)
    else:
        return TrajectoryResult(state="STABLE", confidence=0.75, window=window)


def yunus_trajectory_triggered(stage_history: List[int], nsdt_history: List[NSDTVector]) -> bool:
    """
    Yunus Protocol: Detect sustained high-stage rigidity trap.

    Triggers when:
    - Last YUNUS_WINDOW readings all have stage >= YUNUS_HIGH_STAGE
    - AND adaptability dimension has been declining across the window

    This is the Stage 8 trap signature: a system that has been locked in high
    tension with declining flexibility for 3+ consecutive observations.
    NOT a snapshot — this is a behavioral pattern detection.
    """
    if len(stage_history) < YUNUS_WINDOW or len(nsdt_history) < YUNUS_WINDOW:
        return False

    recent_stages = stage_history[-YUNUS_WINDOW:]
    recent_nsdt   = nsdt_history[-YUNUS_WINDOW:]

    # All recent stages must be >= 7
    if not all(s >= YUNUS_HIGH_STAGE for s in recent_stages):
        return False

    # Adaptability must be declining
    adapt_values = [v.adaptability for v in recent_nsdt]
    adaptability_declining = all(
        adapt_values[i] > adapt_values[i+1]
        for i in range(len(adapt_values)-1)
    )

    return adaptability_declining


def rigidity_index(stage_history: List[int], nsdt_history: List[NSDTVector], window: int = 5) -> float:
    """
    Compute rigidity index: how locked into a high-stage state the system is.
    Range 0.0 (fully flexible) → 1.0 (fully rigid).
    """
    if not stage_history:
        return 0.0

    recent_stages = stage_history[-window:]
    recent_nsdt   = nsdt_history[-window:] if nsdt_history else []

    high_stage_pct = sum(1 for s in recent_stages if s >= 7) / len(recent_stages)

    if recent_nsdt:
        adapt_trend = sum(v.adaptability for v in recent_nsdt) / len(recent_nsdt)
        adaptability_factor = 1.0 - adapt_trend
    else:
        adaptability_factor = 0.5

    return round(min(1.0, high_stage_pct * adaptability_factor * 2), 4)
