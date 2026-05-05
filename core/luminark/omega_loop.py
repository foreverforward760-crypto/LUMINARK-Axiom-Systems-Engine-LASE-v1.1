"""
luminark/omega_loop.py – LUMINARK Omega Loop
Cross-Build Telemetry Router

The Omega Loop allows cross-domain contamination checks by routing 5D NSDT
vectors between the four LUMINARK builds (Overwatch Strict, Kairos, Active
Defense, and Mycelial/Unified Field) whenever a threshold event occurs.

KEY USE CASE — Axiom Yield Broker → Kairos:
  If the AYB logistics engine registers a massive failure (Tension spike,
  Stage 7+ route collapse), the Omega Loop automatically feeds this vector
  into the Kairos engine. Kairos proactively adjusts the human operator's
  biofeedback protocol, anticipating the physiological stress the external
  infrastructure event is about to cause — BEFORE the operator consciously
  registers it.

ARCHITECTURE:
  - Each build registers as a "node" with a domain tag and a callback
  - The OmegaLoop evaluates routing rules on every NSDT publication
  - Matching rules trigger downstream nodes with transformed NSDT vectors
  - The domain bridge (sap_domain_bridge.py) handles cross-domain translation

DESIGN PRINCIPLES:
  - Synchronous by default (no threads/asyncio) — easy to test and reason about
  - Optional async dispatch via asyncio.create_task() if needed
  - All routing decisions are logged (audit trail for safety-critical deployments)
  - No circular routing (publication from node A cannot trigger node A again)
"""

import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Any


# ── Data types ────────────────────────────────────────────────────────────────

@dataclass
class NSDTEvent:
    """
    A 5D NSDT event publication from any domain node.

    Fields
    ------
    source_domain : str   — e.g. "logistics", "biometric", "grid", "cognitive"
    source_id     : str   — specific system/carrier/node identifier
    complexity    : float — [0, 10]
    stability     : float — [0, 10]
    tension       : float — [0, 10]
    adaptability  : float — [0, 10]
    coherence     : float — [0, 10]
    stage         : int   — SAP stage at time of publication
    trap_score    : float — normalised trap score [0, 100]
    timestamp     : float — unix timestamp (auto-set if 0)
    metadata      : dict  — domain-specific extras
    """
    source_domain: str
    source_id:     str
    complexity:    float
    stability:     float
    tension:       float
    adaptability:  float
    coherence:     float
    stage:         int   = 0
    trap_score:    float = 0.0
    timestamp:     float = 0.0
    metadata:      Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

    def to_vector(self) -> List[float]:
        return [self.complexity, self.stability, self.tension,
                self.adaptability, self.coherence]


@dataclass
class RoutingRule:
    """
    A rule that triggers downstream routing when conditions are met.

    Fields
    ------
    name           : str — human-readable rule identifier
    source_domains : list — domains that can trigger this rule (empty = any)
    min_stage      : int  — minimum stage to trigger (inclusive)
    min_trap       : float — minimum trap score to trigger
    min_tension    : float — minimum tension to trigger
    target_domains : list — domains to notify when rule fires
    transform      : callable or None — transform NSDTEvent before forwarding
    priority       : int  — lower = evaluated first
    """
    name:           str
    target_domains: List[str]
    source_domains: List[str] = field(default_factory=list)
    min_stage:      int       = 0
    min_trap:       float     = 0.0
    min_tension:    float     = 0.0
    transform:      Optional[Callable] = None
    priority:       int       = 100

    def matches(self, event: NSDTEvent) -> bool:
        if self.source_domains and event.source_domain not in self.source_domains:
            return False
        if event.stage < self.min_stage:
            return False
        if event.trap_score < self.min_trap:
            return False
        if event.tension < self.min_tension:
            return False
        return True


# ── Omega Loop ────────────────────────────────────────────────────────────────

class OmegaLoop:
    """
    Cross-build telemetry router.

    Usage
    -----
    loop = OmegaLoop()

    # Register nodes (callbacks receive NSDTEvent)
    loop.register("kairos",    kairos_handler)
    loop.register("overwatch", overwatch_handler)

    # Define routing rules
    loop.add_rule(RoutingRule(
        name="logistics-crisis-to-kairos",
        source_domains=["logistics"],
        min_stage=7,
        min_trap=50.0,
        target_domains=["kairos"],
    ))

    # Publish events
    loop.publish(NSDTEvent(
        source_domain="logistics", source_id="carrier-TX-441",
        complexity=7.2, stability=3.1, tension=8.5,
        adaptability=2.0, coherence=3.8,
        stage=7, trap_score=72.0,
    ))
    """

    def __init__(self, log: bool = True):
        self._nodes:    Dict[str, Callable[[NSDTEvent], Any]] = {}
        self._rules:    List[RoutingRule] = []
        self._log:      bool = log
        self._history:  List[Dict] = []

    def register(self, domain: str, handler: Callable[[NSDTEvent], Any]) -> None:
        """Register a domain node with its event handler callback."""
        self._nodes[domain] = handler
        if self._log:
            print(f"[OmegaLoop] Registered node: {domain}")

    def unregister(self, domain: str) -> None:
        """Remove a domain node."""
        self._nodes.pop(domain, None)

    def add_rule(self, rule: RoutingRule) -> None:
        """Add a routing rule. Rules are evaluated in priority order."""
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority)
        if self._log:
            print(f"[OmegaLoop] Rule added: '{rule.name}' → {rule.target_domains}")

    def publish(self, event: NSDTEvent) -> List[Dict]:
        """
        Publish an NSDT event. Evaluates all rules; dispatches to matching targets.

        Returns
        -------
        list of dispatch records (for audit/testing)
        """
        dispatches = []
        for rule in self._rules:
            if not rule.matches(event):
                continue
            for target in rule.target_domains:
                if target == event.source_domain:
                    continue  # no circular routing
                if target not in self._nodes:
                    if self._log:
                        print(f"[OmegaLoop] Warning: target '{target}' not registered")
                    continue

                # Apply transform if defined
                forwarded = rule.transform(event) if rule.transform else event

                record = {
                    "rule":        rule.name,
                    "source":      event.source_domain,
                    "target":      target,
                    "source_id":   event.source_id,
                    "stage":       event.stage,
                    "trap_score":  event.trap_score,
                    "timestamp":   time.time(),
                }
                try:
                    self._nodes[target](forwarded)
                    record["status"] = "dispatched"
                except Exception as e:
                    record["status"] = f"error: {e}"
                    if self._log:
                        print(f"[OmegaLoop] Dispatch error to '{target}': {e}")

                dispatches.append(record)
                self._history.append(record)
                if self._log:
                    print(f"[OmegaLoop] {record['source']} → {record['target']} "
                          f"[{rule.name}] stage={event.stage} trap={event.trap_score:.1f}")

        return dispatches

    def get_history(self, limit: int = 100) -> List[Dict]:
        """Return dispatch history (most recent first)."""
        return list(reversed(self._history[-limit:]))

    def clear_history(self) -> None:
        self._history.clear()


# ── Pre-built routing rules ───────────────────────────────────────────────────

def logistics_crisis_to_kairos(loop: OmegaLoop) -> None:
    """
    Rule: When AYB logistics reaches Stage 7+ or Trap > 50,
    forward to Kairos so the human operator receives proactive biofeedback.
    """
    loop.add_rule(RoutingRule(
        name="logistics-crisis-to-kairos",
        source_domains=["logistics", "axiom_yield_broker", "ayb"],
        min_stage=7,
        min_trap=50.0,
        target_domains=["kairos"],
        priority=10,
    ))


def grid_stress_to_overwatch(loop: OmegaLoop) -> None:
    """
    Rule: When Mycelial/grid network detects external threat (high Tension),
    forward to Overwatch for immediate infrastructure analysis.
    """
    loop.add_rule(RoutingRule(
        name="grid-threat-to-overwatch",
        source_domains=["mycelial", "grid", "ercot"],
        min_tension=7.5,
        min_stage=5,
        target_domains=["overwatch"],
        priority=5,
    ))


def any_critical_to_defense(loop: OmegaLoop) -> None:
    """
    Rule: Any domain reaching Stage 8 with Trap > 75 triggers Active Defense.
    """
    loop.add_rule(RoutingRule(
        name="any-critical-to-defense",
        min_stage=8,
        min_trap=75.0,
        target_domains=["active_defense"],
        priority=1,  # highest priority
    ))


def install_default_rules(loop: OmegaLoop) -> None:
    """Install all three default routing rules."""
    logistics_crisis_to_kairos(loop)
    grid_stress_to_overwatch(loop)
    any_critical_to_defense(loop)


# ── Self-test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    received = []

    def kairos_handler(event: NSDTEvent):
        received.append(("kairos", event.source_domain, event.stage))

    def overwatch_handler(event: NSDTEvent):
        received.append(("overwatch", event.source_domain, event.stage))

    def defense_handler(event: NSDTEvent):
        received.append(("defense", event.source_domain, event.stage))

    loop = OmegaLoop(log=True)
    loop.register("kairos", kairos_handler)
    loop.register("overwatch", overwatch_handler)
    loop.register("active_defense", defense_handler)
    install_default_rules(loop)

    print("\n--- Test: Logistics crisis (Stage 7, Trap 72) ---")
    loop.publish(NSDTEvent(
        source_domain="logistics", source_id="carrier-TX-441",
        complexity=7.2, stability=3.1, tension=8.5,
        adaptability=2.0, coherence=3.8,
        stage=7, trap_score=72.0,
    ))

    print("\n--- Test: Grid threat (Stage 6, Tension 8.0) ---")
    loop.publish(NSDTEvent(
        source_domain="grid", source_id="ercot-zone-h",
        complexity=6.5, stability=4.0, tension=8.0,
        adaptability=3.5, coherence=4.2,
        stage=6, trap_score=45.0,
    ))

    print("\n--- Test: Normal event (Stage 3) — should not route ---")
    dispatches = loop.publish(NSDTEvent(
        source_domain="logistics", source_id="carrier-OK-220",
        complexity=3.0, stability=7.5, tension=2.0,
        adaptability=7.0, coherence=6.5,
        stage=3, trap_score=10.0,
    ))

    print(f"\nResults:")
    for target, source, stage in received:
        print(f"  ✅  {source} → {target} (stage={stage})")

    print(f"\nHistory: {len(loop.get_history())} records")
    assert any(r[0] == "kairos" and r[1] == "logistics" for r in received), "logistics→kairos failed"
    assert any(r[0] == "overwatch" and r[1] == "grid" for r in received), "grid→overwatch failed"
    assert not dispatches, "Normal event should not route"
    print("\n✅ All Omega Loop tests passed")
