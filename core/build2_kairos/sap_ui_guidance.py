"""
sap_ui_guidance.py – LUMINARK Polyvagal UI/UX Guidance Layer

Maps SAP stage + entropy + polyvagal state → structured UX recommendations.
This is a pure data contract. The engine emits guidance; the React/web frontend
consumes it. No CSS is written here — any UI framework can consume this dict.

DESIGN PHILOSOPHY:
  The interface itself becomes an active participant in the feedback loop.
  If the engine detects Stage 5 Duality (sympathetic spike), the UI should
  automatically alter transition speeds, layout density, and color palettes
  to match Kairos somatic invitations — grounding visual rhythm that begins
  stabilizing the user BEFORE they read the protocol text.

POLYVAGAL ALIGNMENT:
  ventral  → connected, safe, social     → warm colors, fluid motion, expanded layout
  sympathetic → mobilized, aroused, alert → cooler tones, reduced motion, focused density
  dorsal   → shutdown, frozen, withdrawn → muted palette, minimal elements, gentle emergence

OUTPUT FORMAT (consumed by React dashboard):
  {
    "color_palette":    { "background": "#...", "primary": "#...", "accent": "#...",
                          "text": "#...", "warning": "#..." },
    "animation":        { "transition_ms": int, "easing": str, "pulse_hz": float },
    "layout":           { "density": str, "sidebar_visible": bool, "font_scale": float },
    "breathing_guide":  { "inhale_ms": int, "hold_ms": int, "exhale_ms": int },
    "stage_label":      str,
    "somatic_cue":      str,
    "urgency":          str   # "none" | "watch" | "alert" | "critical"
  }
"""

from typing import Dict, Any, Optional


# ── Polyvagal color palettes ──────────────────────────────────────────────────

_PALETTES = {
    "ventral": {
        "background": "#F0F4F8",   # warm off-white
        "primary":    "#2D6A4F",   # forest green — safety, growth
        "accent":     "#74C69D",   # mint — connection
        "text":       "#1B2A35",   # deep slate
        "warning":    "#E9C46A",   # soft amber
    },
    "sympathetic": {
        "background": "#EFF6FF",   # cool blue-white — clarity, focus
        "primary":    "#1D4ED8",   # blue — alert, focused
        "accent":     "#60A5FA",   # sky — attention
        "text":       "#1E293B",   # dark slate
        "warning":    "#F97316",   # orange — activation signal
    },
    "dorsal": {
        "background": "#F8F7F4",   # warm grey — grounding
        "primary":    "#6B7280",   # grey — neutral, present
        "accent":     "#9CA3AF",   # light grey — gentle
        "text":       "#374151",   # medium dark
        "warning":    "#D1D5DB",   # very light — not alarming
    },
    "critical": {
        "background": "#FFF1F2",   # very light red — alert without panic
        "primary":    "#BE123C",   # deep rose — urgent
        "accent":     "#F43F5E",   # rose — action required
        "text":       "#1C1917",   # near-black — sharp
        "warning":    "#EF4444",   # red
    },
}

# ── Animation profiles ────────────────────────────────────────────────────────

_ANIMATIONS = {
    "grounded":     {"transition_ms": 800,  "easing": "ease-in-out", "pulse_hz": 0.1},
    "fluid":        {"transition_ms": 500,  "easing": "ease-out",    "pulse_hz": 0.2},
    "focused":      {"transition_ms": 250,  "easing": "ease",        "pulse_hz": 0.0},
    "minimal":      {"transition_ms": 150,  "easing": "linear",      "pulse_hz": 0.0},
    "still":        {"transition_ms": 1200, "easing": "ease-in-out", "pulse_hz": 0.05},
}

# ── Layout density profiles ───────────────────────────────────────────────────

_LAYOUTS = {
    "expanded":  {"density": "expanded",  "sidebar_visible": True,  "font_scale": 1.1},
    "standard":  {"density": "standard",  "sidebar_visible": True,  "font_scale": 1.0},
    "focused":   {"density": "focused",   "sidebar_visible": False, "font_scale": 1.0},
    "minimal":   {"density": "minimal",   "sidebar_visible": False, "font_scale": 0.9},
}

# ── Breathing guide (4-7-8 variants tuned to polyvagal state) ────────────────

_BREATHING = {
    "ventral":     {"inhale_ms": 4000, "hold_ms": 4000, "exhale_ms": 6000},  # box
    "sympathetic": {"inhale_ms": 4000, "hold_ms": 7000, "exhale_ms": 8000},  # 4-7-8
    "dorsal":      {"inhale_ms": 3000, "hold_ms": 1000, "exhale_ms": 5000},  # gentle
    "critical":    {"inhale_ms": 2000, "hold_ms": 0,    "exhale_ms": 4000},  # 1:2 ratio
}


# ── Stage-to-UX mapping ───────────────────────────────────────────────────────

def _stage_urgency(stage: int, entropy: float, trap_energy: float) -> str:
    if stage >= 8 or trap_energy > 0.75:
        return "critical"
    if stage == 7 or trap_energy > 0.5:
        return "alert"
    if stage >= 5 or entropy > 2.0:
        return "watch"
    return "none"


def _polyvagal_from_stage(stage: int, polyvagal_override: Optional[str] = None) -> str:
    if polyvagal_override:
        return polyvagal_override
    mapping = {
        0: "ventral",
        1: "sympathetic",
        2: "dorsal",
        3: "sympathetic",
        4: "dorsal",
        5: "ventral",     # bifurcation — agency available
        6: "ventral",
        7: "sympathetic",
        8: "dorsal",
        9: "ventral",
    }
    return mapping.get(stage, "ventral")


_SOMATIC_CUES = {
    0: "Rest your hand on your heart. Breathe slowly.",
    1: "Notice the first spark in your body. Where do you feel it?",
    2: "One hand belly, one hand chest. Feel the boundary.",
    3: "Three deep breaths, exhale longer than inhale.",
    4: "Stand up. Stretch wide. Feel the ground.",
    5: "Feet flat. Ask: 'What is mine to do?'",
    6: "Hum one note. Feel vibration in your chest.",
    7: "Hand to throat. Say softly: 'I am here. I am not alone.'",
    8: "Breathe into your back body. Soft space behind your heart.",
    9: "Lie down. Surrender your weight to the floor.",
}

_STAGE_LABELS = {
    0: "Open Field", 1: "Awakening", 2: "Forming Identity",
    3: "Discipline", 4: "Testing Ground", 5: "Choice Point",
    6: "Integration", 7: "Insight & Isolation", 8: "Illusion of Permanence",
    9: "Dissolution & Renewal",
}


# ── Main guidance function ────────────────────────────────────────────────────

def generate_ui_guidance(
    stage: int,
    entropy: float,
    trap_energy: float,
    polyvagal_override: Optional[str] = None,
    duality_detected: bool = False,
) -> Dict[str, Any]:
    """
    Generate structured UI/UX guidance from engine output.

    Parameters
    ----------
    stage              : int   — SAP stage (0–9)
    entropy            : float — posterior entropy (nats)
    trap_energy        : float — total trap energy (0–1)
    polyvagal_override : str or None — override polyvagal state if known
    duality_detected   : bool — Stage 5 duality (high stability + low coherence)

    Returns
    -------
    dict — UI guidance contract (see module docstring for schema)
    """
    urgency = _stage_urgency(stage, entropy, trap_energy)
    polyvagal = _polyvagal_from_stage(stage, polyvagal_override)

    # Override to critical palette if Stage 8 trap or duality
    if urgency == "critical" or (duality_detected and stage == 5):
        palette = _PALETTES["critical"]
        anim = _ANIMATIONS["focused"]
        layout = _LAYOUTS["focused"]
    elif polyvagal == "ventral" and urgency == "none":
        palette = _PALETTES["ventral"]
        anim = _ANIMATIONS["fluid"]
        layout = _LAYOUTS["expanded"]
    elif polyvagal == "sympathetic":
        palette = _PALETTES["sympathetic"]
        anim = _ANIMATIONS["focused"]
        layout = _LAYOUTS["focused"]
    elif polyvagal == "dorsal":
        palette = _PALETTES["dorsal"]
        anim = _ANIMATIONS["still"]
        layout = _LAYOUTS["minimal"]
    else:
        palette = _PALETTES["ventral"]
        anim = _ANIMATIONS["standard"] if hasattr(_ANIMATIONS, "standard") else _ANIMATIONS["fluid"]
        layout = _LAYOUTS["standard"]

    # High entropy → reduce animation speed (don't add to cognitive load)
    if entropy > 2.0:
        anim = dict(anim)
        anim["transition_ms"] = min(anim["transition_ms"] * 2, 1500)
        anim["pulse_hz"] = 0.0

    breathing = _BREATHING.get(polyvagal, _BREATHING["ventral"])
    if urgency == "critical":
        breathing = _BREATHING["critical"]

    return {
        "color_palette":   palette,
        "animation":       anim,
        "layout":          layout,
        "breathing_guide": breathing,
        "stage_label":     _STAGE_LABELS.get(stage, f"Stage {stage}"),
        "somatic_cue":     _SOMATIC_CUES.get(stage, "Take three conscious breaths."),
        "urgency":         urgency,
        "polyvagal_state": polyvagal,
        "duality_detected": duality_detected,
        "entropy":         round(entropy, 4),
        "trap_energy":     round(trap_energy, 4),
    }


# ── Self-test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    cases = [
        (0,  0.3, 0.0,  False, "Stage 0 – Open Field"),
        (5,  1.8, 0.3,  False, "Stage 5 – Choice Point"),
        (5,  0.4, 0.6,  True,  "Stage 5 – Duality Detected"),
        (7,  0.8, 0.5,  False, "Stage 7 – Crisis"),
        (8,  0.4, 0.82, False, "Stage 8 – Trap Active"),
    ]
    for stage, ent, trap, duality, label in cases:
        g = generate_ui_guidance(stage, ent, trap, duality_detected=duality)
        print(f"\n{label}")
        print(f"  Urgency    : {g['urgency']}")
        print(f"  Polyvagal  : {g['polyvagal_state']}")
        print(f"  Primary    : {g['color_palette']['primary']}")
        print(f"  Transition : {g['animation']['transition_ms']}ms")
        print(f"  Breathing  : {g['breathing_guide']['inhale_ms']}ms inhale")
        print(f"  Somatic    : {g['somatic_cue'][:60]}...")
