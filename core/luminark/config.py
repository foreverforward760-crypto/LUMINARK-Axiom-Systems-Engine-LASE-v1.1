"""
luminark/config.py  –  Unified engine configuration.

EngineConfig selects which build to use and provides all hyperparameters.
Supports dict, JSON, and (optionally) YAML round-trips.

Usage:
    cfg = EngineConfig(build="unified", temperature=0.4)
    engine = create_engine(cfg)

    # Save to JSON
    cfg.to_json("config.json")

    # Load from JSON
    cfg = EngineConfig.from_json("config.json")
"""

import json
from dataclasses import dataclass, asdict, field
from typing import Literal, Dict, Any, Optional

BUILD_CHOICES = Literal["overwatch", "kairos", "defense", "unified"]


@dataclass
class EngineConfig:
    """
    Full configuration for any LUMINARK build.

    build           – which engine to instantiate:
                        "overwatch"  →  Build 1 (strict, v6.5)
                        "kairos"     →  Build 2 (therapeutic, v1.0)
                        "defense"    →  Build 3 (active defense, v7)
                        "unified"    →  Build 4 (unified field, v8)

    Shared hyperparameters (all builds except kairos):
      temperature   – softmax temperature for Bayesian posterior (default 0.5)
      beta          – energy modulation coefficient (default 0.8)

    Kairos-only:
      allow_regression  – permit stage regression in therapeutic mode
      kairos_temperature, kairos_beta  – separate tuning for therapeutic engine

    Build 3 Lyapunov weights:
      w_H, w_E, w_v

    Build 4 Unified Field coefficients:
      uf_alpha (G weight), uf_beta (P weight), uf_gamma (E weight), uf_delta (L weight)
    """
    build:              str   = "overwatch"
    temperature:        float = 0.5
    beta:               float = 0.8

    # Kairos-specific
    allow_regression:   bool  = True
    kairos_temperature: float = 0.7
    kairos_beta:        float = 0.6

    # Lyapunov weights (Build 3 & 4)
    w_H:                float = 1.0
    w_E:                float = 2.0
    w_v:                float = 0.5

    # Unified Field coefficients (Build 4)
    uf_alpha:           float = 1.0
    uf_beta:            float = 1.0
    uf_gamma:           float = 1.0
    uf_delta:           float = 1.0

    # Optional metadata
    label:              str   = ""
    description:        str   = ""

    def validate(self) -> "EngineConfig":
        valid = ("overwatch", "kairos", "defense", "unified")
        if self.build not in valid:
            raise ValueError(f"build must be one of {valid}, got '{self.build}'")
        for attr in ("temperature", "beta", "kairos_temperature", "kairos_beta"):
            v = getattr(self, attr)
            if not (0.0 < v <= 10.0):
                raise ValueError(f"{attr}={v} must be in (0, 10]")
        return self

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EngineConfig":
        known = {k for k in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})

    def to_json(self, path: Optional[str] = None, indent: int = 2) -> str:
        s = json.dumps(self.to_dict(), indent=indent)
        if path:
            with open(path, "w") as f:
                f.write(s)
        return s

    @classmethod
    def from_json(cls, path_or_str: str) -> "EngineConfig":
        """Load from a file path or a raw JSON string."""
        try:
            with open(path_or_str) as f:
                d = json.load(f)
        except (FileNotFoundError, OSError):
            d = json.loads(path_or_str)
        return cls.from_dict(d)

    def to_yaml(self, path: Optional[str] = None) -> str:
        """
        Save as YAML (requires PyYAML).
        Falls back to JSON with a warning if PyYAML is not installed.
        """
        try:
            import yaml  # type: ignore
            s = yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)
            if path:
                with open(path, "w") as f:
                    f.write(s)
            return s
        except ImportError:
            import warnings
            warnings.warn("PyYAML not installed; falling back to JSON.")
            return self.to_json(path)

    @classmethod
    def from_yaml(cls, path: str) -> "EngineConfig":
        try:
            import yaml  # type: ignore
            with open(path) as f:
                d = yaml.safe_load(f)
        except ImportError:
            raise ImportError("PyYAML is required to load YAML configs: pip install pyyaml")
        return cls.from_dict(d)


# Preset configurations for common use cases
PRESETS: Dict[str, EngineConfig] = {
    "infrastructure":  EngineConfig(build="overwatch", temperature=0.5, beta=0.8,
                                    label="infrastructure",
                                    description="Power grid, utilities, critical infrastructure"),
    "therapeutic":     EngineConfig(build="kairos", allow_regression=True,
                                    kairos_temperature=0.7, kairos_beta=0.6,
                                    label="therapeutic",
                                    description="Coaching, therapy, human development"),
    "defense":         EngineConfig(build="defense", temperature=0.5, beta=0.8,
                                    w_H=1.0, w_E=2.0, w_v=0.5,
                                    label="defense",
                                    description="Autonomous adversarial defense"),
    "unified_research": EngineConfig(build="unified", temperature=0.4, beta=0.8,
                                     w_H=1.0, w_E=2.0, w_v=0.5,
                                     uf_alpha=1.0, uf_beta=1.0, uf_gamma=1.0, uf_delta=1.0,
                                     label="unified_research",
                                     description="Full unified field for research / AI safety"),
}
