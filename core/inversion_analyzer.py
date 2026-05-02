"""
Inversion Analyzer - Core stage detection and trap identification.
Integrates recalibration and dissolution logic.
"""

from typing import List, Optional
from .sap_types import NSDTVector, SAPStage, SystemState
from .recalibration import RecalibrationEngine
from .dissolution import DissolutionEngine
from .tumbling_inversion import compute_inversion, compute_arc_direction
from .stage_6_flow import classify_flow_quality
from .stage_7_crucible import classify_crucible_mode
from .stage_8_gratitude import classify_crystallization, engage_gratitude_mechanism

class InversionAnalyzer:
    @staticmethod
    def classify_operating_margin(nsdt: NSDTVector) -> dict:
        """
        Stage 6 Industrial Classifier: Safety Margin Utilization
        
        Determines if the system is in Sustainable Margin (Middle Path from Stage 5)
        or Brittle Margin (default tumble). Uses Stability (S) and Tension (T).
        
        Industrial criteria:
          - Sustainable: S between 40-70, T < 50 → equipment is in efficient range.
          - Brittle: S > 75 and T < 30 → appears stable but no slack; failure risk.
        """
        s = nsdt.stability
        t = nsdt.tension
        
        if 40 <= s <= 70 and t < 50:
            margin_type = "sustainable"
            directive = "Maintain current load. Safety margin is optimal."
        elif s > 75 and t < 30:
            margin_type = "brittle"
            directive = "REDUCED SAFETY MARGIN. Apparent stability masks fatigue. Reduce load or schedule inspection."
        else:
            margin_type = "nominal"
            directive = "Operating within expected parameters. No immediate margin risk."
        
        return {
            "margin_type": margin_type,
            "directive": directive,
            "stability": s,
            "tension": t
        }
    
    @staticmethod
    def classify_failure_isolation(nsdt: NSDTVector) -> dict:
        """
        Stage 7 Industrial Classifier: Failure Isolation / Component Stress-Testing
        
        Detects whether a breakdown is being contained (distillation)
        or cascading (collapse). Uses Complexity (N) and Coherence (C).
        
        Industrial criteria:
          - Distillation: N > 70 and C > 60 → system is isolating the fault.
          - Collapse: N > 70 and C < 40 → cascading failure.
        """
        n = nsdt.complexity
        c = nsdt.coherence
        
        if n > 70 and c > 60:
            # High complexity, high coherence -> system is isolating the fault.
            mode = "distillation"
            directive = "Failure isolated to specific subsystem. Rerouting around affected module."
        elif n > 70 and c < 40:
            # High complexity, low coherence -> cascading failure.
            mode = "collapse"
            directive = "CRITICAL: Cascading failure detected. Emergency shutdown recommended."
        else:
            mode = "degraded"
            directive = "Degraded operation. Monitor closely; failure not yet contained."
        
        return {
            "failure_isolation_mode": mode,
            "directive": directive,
            "complexity": n,
            "coherence": c
        }
    
    @staticmethod
    def classify_resource_recirculation(nsdt: NSDTVector) -> dict:
        """
        Stage 8 Industrial Classifier: Resource Recirculation / Entropy Accounting
        
        Determines if the system is ready to dissolve (return to solution)
        or will shatter (catastrophic failure). Uses Stability (S) and Tension (T).
        
        Industrial criteria:
          - Shattering: S > 80 and T < 20 → brittle crystal, imminent failure.
          - Dissolution: 50 <= S <= 70 and 30 <= T <= 50 → controlled decommissioning.
        """
        s = nsdt.stability
        t = nsdt.tension
        # Divergence: high Stability with hidden high Tension
        divergence = abs(s - t)  # Simplified; real formula could be (s - t) when t low.
        
        # Industrial criteria:
        # Dissolution path: s and t converge (both moderate, e.g., 50-60)
        # Shattering path: s high (>80) and t low (<20) -> brittle crystal.
        if s > 80 and t < 20:
            trajectory = "shattering"
            directive = "STRUCTURAL BRITTLENESS IMMINENT. Immediate de-energization required."
        elif 50 <= s <= 70 and 30 <= t <= 50:
            trajectory = "dissolution"
            directive = "Controlled decommissioning or resource recovery recommended. Energy can be recirculated."
        else:
            trajectory = "uncertain"
            directive = "Monitor divergence. No immediate dissolution or shattering signal."
        
        return {
            "recirculation_trajectory": trajectory,
            "directive": directive,
            "revealed_stability": s,
            "concealed_tension": t,
            "divergence": divergence
        }
    
    @staticmethod
    def compute_stage(nsdt: NSDTVector, allow_recalibration: bool = True, previous_state: Optional[SystemState] = None) -> SystemState:
        p_score = nsdt.physical_score()
        c_score = nsdt.conscious_score()

        # Stage determination logic
        if nsdt.coherence >= 95 and nsdt.adaptability >= 80:
            stage = SAPStage.RELEASE
        elif p_score >= 70 and c_score < 60:
            stage = SAPStage.FOUNDATION if nsdt.stability > nsdt.tension else SAPStage.INTEGRATION
        elif p_score < 50 and c_score >= 70:
            stage = SAPStage.NAVIGATION if nsdt.complexity < 40 else SAPStage.THRESHOLD
        elif p_score >= 60 and c_score >= 60:
            stage = SAPStage.UNITY
        else:
            stage = SAPStage.ANALYSIS

        is_trap = False
        trap_reason = ""
        if stage == SAPStage.UNITY and nsdt.adaptability < 30:
            is_trap = True
            trap_reason = "Denying inversion: claiming stability in both domains"

        # Update history
        nsdt_vector = [nsdt.complexity, nsdt.stability, nsdt.adaptability, nsdt.tension, nsdt.coherence]
        history = []
        if previous_state and previous_state.nsdt_history:
            history = previous_state.nsdt_history[-5:]   # keep last 5
        history.append(nsdt_vector)

        # Build state object with Tumbling Inversion fields
        state = SystemState(
            stage=stage,
            nsdt=nsdt,
            nsdt_vector=nsdt_vector,
            nsdt_history=history,
            is_trap=is_trap,
            trap_reason=trap_reason,
            recommended_action=InversionAnalyzer._recommend_action(stage, is_trap, nsdt),
            unified_field_value=InversionAnalyzer._unified_field(nsdt),
            middle_path_accessed=previous_state.middle_path_accessed if previous_state else False,
            witness_position_active=previous_state.witness_position_active if previous_state else False,
            gratitude_mechanism_engaged=previous_state.gratitude_mechanism_engaged if previous_state else False,
        )

        # Stage 5 Middle Path detection
        if stage == SAPStage.UNITY:  # Stage 5
            # Compute witness readiness (Adaptability + Coherence > Tension + 30?)
            witness_score = (nsdt.adaptability * 0.4) + (nsdt.coherence * 0.4) - (nsdt.tension * 0.2)
            state.middle_path_accessed = witness_score > 50
            state.witness_position_active = state.middle_path_accessed

        # Compute inversion for this stage
        inv = compute_inversion(nsdt_vector, int(stage))
        state.inversion_state = inv.__dict__

        # Compute arc direction using history
        if len(history) >= 2:
            arc, conf = compute_arc_direction(history)
            state.arc_direction = arc

        # Stage specific analysis
        if stage == SAPStage.HARMONY:  # Stage 6
            state.flow_analysis = classify_flow_quality(nsdt_vector, state.middle_path_accessed)
        elif stage == SAPStage.FOUNDATION:  # Stage 7
            state.crucible_analysis = classify_crucible_mode(nsdt_vector, state.middle_path_accessed, history)
        elif stage == SAPStage.INTEGRATION:  # Stage 8
            state.crystallization_analysis = classify_crystallization(nsdt_vector, state.middle_path_accessed, history)

        # Build extra classifiers for backward compatibility
        extra = {}
        if stage == SAPStage.HARMONY:
            extra["operating_margin"] = InversionAnalyzer.classify_operating_margin(nsdt)
        elif stage == SAPStage.FOUNDATION:
            extra["failure_isolation"] = InversionAnalyzer.classify_failure_isolation(nsdt)
        elif stage == SAPStage.INTEGRATION:
            extra["resource_recirculation"] = InversionAnalyzer.classify_resource_recirculation(nsdt)
        state.extra = extra

        # Apply recalibration if enabled and applicable
        if allow_recalibration:
            should_recal, reason = RecalibrationEngine.should_recalibrate(state)
            if should_recal:
                state = RecalibrationEngine.apply_recalibration(state)

        # Check for dissolution (Stage 9 -> 0)
        should_diss, reason = DissolutionEngine.should_dissolve(state)
        if should_diss:
            state = DissolutionEngine.dissolve(state)

        return state

    @staticmethod
    def engage_gratitude_mechanism(state: SystemState) -> SystemState:
        """Apply the Gratitude Mechanism to reduce Revealed/Concealed divergence."""
        if state.nsdt_vector is None:
            return state
        new_vector = engage_gratitude_mechanism(state.nsdt_vector)
        state.nsdt_vector = new_vector
        state.gratitude_mechanism_engaged = True
        # Recompute crystallization with new vector
        if state.stage == SAPStage.INTEGRATION:
            state.crystallization_analysis = classify_crystallization(
                new_vector,
                state.middle_path_accessed,
                state.nsdt_history
            )
        return state

    @staticmethod
    def _recommend_action(stage: SAPStage, is_trap: bool, nsdt: NSDTVector) -> str:
        if is_trap:
            return "INTERVENE: Trap Detected"
        if stage == SAPStage.THRESHOLD and nsdt.tension > 80:
            return "PIVOT: Consider Graceful Regression or Prepare for Crisis"
        if stage == SAPStage.INTEGRATION:
            return "WARNING: Unsustainable Peak State"
        if stage == SAPStage.RELEASE:
            return "RELEASE: System ready for dissolution"
        return "HOLD: Monitor"

    @staticmethod
    def _unified_field(nsdt: NSDTVector) -> float:
        G = nsdt.stability / 100.0
        P = nsdt.adaptability / 100.0
        E = nsdt.tension / 100.0
        L = nsdt.coherence / 100.0
        return (0.25 * G) + (0.30 * P) + (0.20 * E) + (0.25 * L)
