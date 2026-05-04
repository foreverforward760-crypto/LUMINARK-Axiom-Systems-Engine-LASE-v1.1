"""
OCTO-MYCELIAL NEUROMORPHIC SENSORY DEFENSE SYSTEM v4.0
ENHANCED WITH RISS SCORING & THREAT TAXONOMY
LUMINARK Axiom Systems Engine (LASE)
Meridian Axiom Alignment Technologies (MAAT)

Integration of:
- Octo-Mycelial v3.5 (biological sensory capabilities)
- RISS (Recursive Impact & State Score) - SAR-aware threat scoring
- Cyber Kill Chain threat taxonomy
- Network variability as direct HRV analog

New capabilities:
✓ RISS scoring with SAR stage weights
✓ Cyber kill chain threat classification
✓ Network variability = HRV direct mapping
✓ Threat history & temporal analysis
✓ All original v3.5 capabilities preserved

Run: python octo_mycelial_v4.py --mode demo
"""

import asyncio
import json
import time
import random
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set, Any
from enum import Enum
from functools import lru_cache

import numpy as np
import pandas as pd
import networkx as nx
from scipy import signal, fft
from scipy.spatial import KDTree
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt


# ============================================================================
# ENUMS & DATA STRUCTURES
# ============================================================================

class PolyvagalState(Enum):
    VENTRAL_RENEWAL = "ventral renewal"
    SYMPATHETIC_THRESHOLD = "sympathetic threshold"
    DORSAL_TRAP = "dorsal trap"

class ChipState(Enum):
    VENTRAL_RENEWAL = "ventral renewal"
    SYMPATHETIC_THRESHOLD = "sympathetic threshold"
    DORSAL_TRAP = "dorsal trap"

class EthicalPrinciple(Enum):
    TRANSPARENCY = "transparency"
    ACCOUNTABILITY = "accountability"
    PRIVACY = "privacy"
    FAIRNESS = "fairness"
    HUMAN_OVERRIDE = "human_override"

class ThreatType(Enum):
    """Cyber Kill Chain threat taxonomy"""
    RECON = "reconnaissance"
    LATERAL_MOVEMENT = "lateral_movement"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    EXFILTRATION = "exfiltration"
    IMPACT = "impact"
    COMMAND_CONTROL = "command_and_control"


@dataclass
class PhysiologicalMetrics:
    hrv_score: float
    sleep_score: float
    resp_score: float
    o2_score: float
    combined: float
    network_variability: float
    timestamp: datetime

    def to_dict(self):
        return {
            'hrv': self.hrv_score, 'sleep': self.sleep_score,
            'resp': self.resp_score, 'o2': self.o2_score,
            'combined': self.combined,
            'network_variability': self.network_variability,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ThreatEvent:
    node_id: int
    threat_type: ThreatType
    timestamp: float
    riss_score: int
    severity: str
    contained: bool = False

    def to_dict(self):
        return {
            'node_id': self.node_id,
            'threat_type': self.threat_type.value,
            'timestamp': self.timestamp,
            'riss_score': self.riss_score,
            'severity': self.severity,
            'contained': self.contained
        }


# ============================================================================
# RISS CALCULATOR
# ============================================================================

class RISSCalculator:
    """
    Recursive Impact & State Score Calculator
    SAR stage weights integrated with threat assessment.

    Formula:
        RISS = (base_score + scale_factor + variability_penalty) * stage_weight
    """

    def __init__(self):
        self.stage_weights = {
            1: 0.3, 2: 0.5, 3: 0.7, 4: 1.0,
            5: 1.8,  # THRESHOLD — critical decision point
            6: 1.5, 7: 1.6,
            8: 2.2,  # TRAP — maximum danger
            9: 1.4
        }
        self.threat_base_scores = {
            ThreatType.RECON:                 30,
            ThreatType.LATERAL_MOVEMENT:      50,
            ThreatType.PERSISTENCE:           70,
            ThreatType.PRIVILEGE_ESCALATION:  65,
            ThreatType.COMMAND_CONTROL:       75,
            ThreatType.EXFILTRATION:          85,
            ThreatType.IMPACT:                90,
        }

    def calculate_riss(self, threat_type: ThreatType, affected_nodes: int,
                       network_variability: float, sar_stage: int = 5) -> int:
        base               = self.threat_base_scores.get(threat_type, 50)
        scale              = min(50, affected_nodes * 3)
        variability_penalty = (100 - network_variability) * 0.3
        stage_multiplier   = self.stage_weights.get(sar_stage, 1.0)
        raw_riss           = (base + scale + variability_penalty) * stage_multiplier
        return min(100, int(raw_riss))

    def determine_sar_stage(self, threat_type: ThreatType,
                            network_health: float) -> int:
        threat_stage_map = {
            ThreatType.RECON:                1,
            ThreatType.LATERAL_MOVEMENT:     5,
            ThreatType.PERSISTENCE:          4,
            ThreatType.PRIVILEGE_ESCALATION: 6,
            ThreatType.COMMAND_CONTROL:      7,
            ThreatType.EXFILTRATION:         7,
            ThreatType.IMPACT:               8,
        }
        base_stage = threat_stage_map.get(threat_type, 5)
        if network_health < 30:  return 8
        if network_health < 50:  return min(7, base_stage + 1)
        return base_stage


# ============================================================================
# MYCELIUM SENSORY SYSTEM
# ============================================================================

class MyceliumSensorySystem:
    """Armillaria ostoyae — 2,400 acres, 2,500 years"""

    def __init__(self, network_size: int):
        self.network_size        = network_size
        self.conductivity        = 0.85
        self.signal_velocity     = 0.5
        self.resonance_frequencies = [7, 14, 28, 42]

    def detect_chemical_gradient(self, node_positions: np.ndarray,
                                  threat_chemicals: np.ndarray) -> np.ndarray:
        gradient = np.zeros((len(node_positions), len(threat_chemicals)))
        for i, pos in enumerate(node_positions):
            distances     = np.linalg.norm(node_positions - pos, axis=1)
            attenuation   = np.exp(-distances / 10.0)
            chemical_field = np.sum(threat_chemicals * attenuation[:, np.newaxis], axis=0)
            gradient[i]   = chemical_field
        return gradient

    def sense_electrical_patterns(self, node_activity: np.ndarray) -> Dict:
        frequencies    = fft.fftfreq(len(node_activity), 0.01)
        power_spectrum = np.abs(fft.fft(node_activity)) ** 2
        resonance_detected = [
            f for f in self.resonance_frequencies
            if power_spectrum[np.argmin(np.abs(frequencies - f))] > np.mean(power_spectrum) * 3
        ]
        surge_nodes = np.where(
            node_activity > np.mean(node_activity) + 3 * np.std(node_activity)
        )[0]
        return {
            'resonance_frequencies': resonance_detected,
            'energy_surges':         surge_nodes.tolist(),
            'total_power':           float(np.sum(power_spectrum)),
            'dominant_frequency':    float(frequencies[np.argmax(power_spectrum)]),
        }

    def detect_vibrations(self, node_movements: np.ndarray) -> Dict:
        vibrations = np.zeros(len(node_movements))
        for i, movement in enumerate(node_movements):
            coefficients, _ = signal.cwt(np.atleast_1d(movement),
                                         signal.ricker, np.arange(1, 31))
            vibrations[i] = float(np.mean(np.abs(coefficients[5:25])))
        autocorr  = np.correlate(node_movements, node_movements, mode='full')
        periodicity = int(np.argmax(autocorr[len(node_movements) // 2 + 1:]) + 1)
        return {
            'vibration_intensity':   float(np.mean(vibrations)),
            'rhythmic_patterns':     periodicity if periodicity < len(node_movements) // 2 else None,
            'vibration_map':         vibrations,
            'anomalous_vibrations':  np.where(vibrations > np.mean(vibrations) * 2)[0].tolist(),
        }

    def sense_mineral_concentrations(self, node_health: np.ndarray) -> Dict:
        calcium   = node_health * 0.7 + np.random.normal(0, 0.1,  len(node_health))
        potassium = node_health * 0.5 + np.random.normal(0, 0.08, len(node_health))
        magnesium = node_health * 0.3 + np.random.normal(0, 0.05, len(node_health))
        return {
            'calcium_deficit':   np.where(calcium   < 0.4)[0].tolist(),
            'potassium_deficit': np.where(potassium < 0.3)[0].tolist(),
            'magnesium_deficit': np.where(magnesium < 0.2)[0].tolist(),
        }


# ============================================================================
# OCTOPUS SENSORY SYSTEM
# ============================================================================

class OctopusSensorySystem:
    """500M neurons, distributed intelligence"""

    def __init__(self):
        self.polarization_angles = np.linspace(0, 180, 36)

    def polarized_light_vision(self, light_field: np.ndarray) -> Dict:
        if light_field is None or len(light_field) == 0:
            return {}
        pv   = np.array([light_field * np.cos(np.deg2rad(a)) for a in self.polarization_angles])
        ent  = -np.sum(pv * np.log2(pv + 1e-10), axis=0)
        return {
            'polarization_entropy': ent,
            'anomaly_indices':      np.where(ent > np.mean(ent) * 1.5)[0].tolist(),
            'pattern_complexity':   float(np.std(ent)),
        }

    def chemotactile_sensing(self, node_positions: np.ndarray,
                              chemical_signatures: Dict) -> Dict:
        detections = {}
        for node_id, _ in enumerate(node_positions):
            found = []
            for chem_name, chem_field in chemical_signatures.items():
                conc = chem_field.get(node_id, 0) if isinstance(chem_field, dict) else 0
                if conc > 0.1:
                    found.append({'chemical': chem_name, 'concentration': conc})
            if found:
                detections[node_id] = found
        return detections

    def proprioceptive_awareness(self, node_positions: np.ndarray,
                                  node_velocities: np.ndarray) -> Dict:
        pos_uncertainty = np.array([np.linalg.norm(node_positions[i]) * 0.1
                                    for i in range(len(node_positions))])
        return {
            'position_uncertainty':     pos_uncertainty,
            'proprioceptive_anomalies': np.where(pos_uncertainty > 0.5)[0].tolist(),
        }


# ============================================================================
# THERMAL & ENERGY SENSING
# ============================================================================

class ThermalEnergySensing:

    def __init__(self):
        self.thermal_baseline = None
        self.energy_history: List[np.ndarray] = []

    def detect_thermal_anomalies(self, node_temperatures: np.ndarray,
                                  ambient: float) -> Dict:
        temp_diff  = node_temperatures - ambient
        anomalies  = np.where(np.abs(temp_diff) > 2.0)[0]
        gradient   = np.gradient(node_temperatures)
        hi_grad    = np.where(np.abs(gradient) > 1.0)[0]
        return {
            'thermal_anomalies': anomalies.tolist(),
            'thermal_gradients': gradient.tolist(),
            'high_gradient_nodes': hi_grad.tolist(),
        }

    def detect_energy_surges(self, node_energy: np.ndarray) -> Dict:
        self.energy_history.append(node_energy)
        if len(self.energy_history) > 10:
            self.energy_history = self.energy_history[-10:]
        if len(self.energy_history) > 1:
            delta  = node_energy - self.energy_history[-2]
            surges = np.where(delta > np.std(node_energy) * 3)[0]
        else:
            surges = np.array([])
        return {
            'energy_surges':  surges.tolist(),
            'total_energy':   float(np.sum(node_energy)),
            'energy_variance': float(np.var(node_energy)),
        }


# ============================================================================
# BIO-SENSORY FUSION
# ============================================================================

class BioSensoryFusion:

    def __init__(self, network_size: int):
        self.mycelium_sensors = MyceliumSensorySystem(network_size)
        self.octopus_sensors  = OctopusSensorySystem()
        self.attention_weights = {
            'vibration': 0.25, 'chemical': 0.20, 'electrical': 0.15,
            'visual': 0.20, 'proprioceptive': 0.10, 'thermal': 0.10,
        }

    def sense_environment(self, network_state: Dict) -> Dict:
        sd               = {}
        node_positions   = network_state.get('node_positions', np.array([]))
        node_health      = network_state.get('node_health', np.array([]))
        node_activity    = network_state.get('node_activity', np.array([]))
        threat_sigs      = network_state.get('threat_signatures', {})

        if len(node_positions) > 0:
            if 'chemical_signatures' in threat_sigs:
                sd['chemical_gradients'] = self.mycelium_sensors.detect_chemical_gradient(
                    node_positions, threat_sigs['chemical_signatures'])
            sd['electrical_patterns'] = self.mycelium_sensors.sense_electrical_patterns(node_activity)
            sd['vibrations']          = self.mycelium_sensors.detect_vibrations(node_activity)
            sd['mineral_deficiencies'] = self.mycelium_sensors.sense_mineral_concentrations(node_health)

        if 'light_field' in network_state:
            sd['polarized_vision'] = self.octopus_sensors.polarized_light_vision(
                network_state['light_field'])
        sd['chemotactile_detections'] = self.octopus_sensors.chemotactile_sensing(
            node_positions, threat_sigs)
        sd['proprioceptive_awareness'] = self.octopus_sensors.proprioceptive_awareness(
            node_positions, network_state.get('node_velocities', np.array([])))

        sd['fused_threat_assessment'] = self._fuse(sd)
        return sd

    def _fuse(self, sd: Dict) -> Dict:
        num_nodes    = 100
        threat_scores = {i: 0.0 for i in range(num_nodes)}
        if 'vibrations' in sd:
            vmap = sd['vibrations'].get('vibration_map', np.zeros(num_nodes))
            for i in range(min(num_nodes, len(vmap))):
                threat_scores[i] += float(vmap[i]) * self.attention_weights['vibration']
        mx = max(threat_scores.values()) if threat_scores else 1.0
        if mx > 0:
            threat_scores = {k: v / mx for k, v in threat_scores.items()}
        cats = {}
        for n, s in threat_scores.items():
            cats[n] = ('CRITICAL' if s > 0.8 else 'HIGH' if s > 0.6
                       else 'MEDIUM' if s > 0.4 else 'LOW' if s > 0.2 else 'NORMAL')
        return {
            'threat_scores':       threat_scores,
            'threat_categories':   cats,
            'overall_threat_level': float(np.mean(list(threat_scores.values()))),
        }


# ============================================================================
# PHYSIOLOGICAL PIPELINE
# ============================================================================

class PhysiologicalPipeline:

    def load_csv_safe(self, path: Optional[str], column: str) -> List[float]:
        if not path or not os.path.exists(path):
            return []
        try:
            df = pd.read_csv(path)
            return df[column].astype(float).dropna().tolist() if column in df.columns else []
        except Exception:
            return []

    def normalize_hrv(self, hrv_ms: float) -> float:
        return max(0, min(100, ((hrv_ms - 20) / 80) * 100))

    def compute_sleep_score(self, duration_min: float, deep_pct: float) -> float:
        return min(100, (duration_min / 480) * 100) * 0.6 + min(100, (deep_pct / 25) * 100) * 0.4

    def compute_resp_score(self, resp_rate: float) -> float:
        if 12 <= resp_rate <= 20: return 100.0
        if resp_rate < 12:        return max(0.0, (resp_rate / 12) * 100)
        return max(0.0, 100 - (resp_rate - 20) * 10)

    def compute_o2_score(self, o2_percent: float) -> float:
        if o2_percent >= 95: return min(100.0, ((o2_percent - 95) / 5) * 100)
        return max(0.0, ((o2_percent - 80) / 15) * 100)


# ============================================================================
# OCTO-MYCELIAL CHIP v4.0
# ============================================================================

class OctoMycelialChip:
    """
    Enhanced Octo-Mycelial defense system v4.0
    RISS scoring + Cyber Kill Chain taxonomy + Network HRV analog.
    """

    def __init__(self, num_nodes: int = 35,
                 hrv_csv_path: Optional[str] = None,
                 sleep_csv_path: Optional[str] = None,
                 resp_csv_path: Optional[str] = None,
                 o2_csv_path: Optional[str] = None):

        self.G              = nx.random_geometric_graph(num_nodes, radius=0.25)
        self._init_node_states()
        self.bio_fusion     = BioSensoryFusion(num_nodes)
        self.thermal_energy = ThermalEnergySensing()
        self.physio         = PhysiologicalPipeline()
        self.riss           = RISSCalculator()
        self.threat_history: List[ThreatEvent] = []
        self.network_variability = 75.0
        self.hrv_data       = self.physio.load_csv_safe(hrv_csv_path, 'value')
        self.resp_data      = self.physio.load_csv_safe(resp_csv_path, 'breaths_per_minute')
        self.o2_data        = self.physio.load_csv_safe(o2_csv_path, 'o2_percentage')
        self.threats: Set[int]  = set()
        self.isolated: Set[int] = set()
        self.hrv_index      = 0
        self.current_metrics = self._compute_metrics()
        self.sensory_results: Dict   = {}
        self.threat_assessment: Dict = {}
        self._print_init()

    def _init_node_states(self):
        for n in self.G.nodes:
            self.G.nodes[n].update({
                'health': 100.0, 'processing': random.uniform(60, 100),
                'state': 'healthy', 'temperature': 37.0 + random.uniform(-0.5, 0.5),
                'energy': random.uniform(50, 100), 'threat_type': None, 'riss_score': 0,
            })

    def _compute_metrics(self) -> PhysiologicalMetrics:
        hrv  = self.hrv_data[-1]  if self.hrv_data  else 55.0
        resp = float(np.mean(self.resp_data[-10:])) if self.resp_data else 16.0
        o2   = float(np.mean(self.o2_data[-10:]))   if self.o2_data  else 98.0
        hs   = self.physio.normalize_hrv(hrv)
        ss   = self.physio.compute_sleep_score(420, 20.0)
        rs   = self.physio.compute_resp_score(resp)
        os_  = self.physio.compute_o2_score(o2)
        comb = hs * 0.3 + ss * 0.2 + rs * 0.2 + os_ * 0.3
        return PhysiologicalMetrics(hs, ss, rs, os_, comb, self.network_variability, datetime.now())

    def _print_init(self):
        print("=" * 60)
        print("🧬 OCTO-MYCELIAL DEFENSE SYSTEM v4.0 | LASE")
        print(f"🌱 Nodes: {len(self.G.nodes)} | 🐙 Octopus sensors active")
        print(f"📊 RISS Calculator initialized | HRV analog: {self.network_variability:.0f}/100")
        print("=" * 60)

    def get_chip_state(self) -> ChipState:
        v = self.network_variability
        if v > 60: return ChipState.VENTRAL_RENEWAL
        if v > 30: return ChipState.SYMPATHETIC_THRESHOLD
        return ChipState.DORSAL_TRAP

    def inject_threat_v4(self, target_nodes: Optional[List[int]] = None,
                          threat_type: Optional[ThreatType] = None) -> List[ThreatEvent]:
        self.current_metrics = self._compute_metrics()
        state        = self.get_chip_state()
        threat_type  = threat_type or random.choice(list(ThreatType))
        if not target_nodes:
            target_nodes = random.sample(list(self.G.nodes), min(3, len(self.G.nodes)))

        print(f"\n⚠️  THREAT: {threat_type.value.upper()} → nodes {target_nodes}")
        events = []
        damage_pct = {ChipState.VENTRAL_RENEWAL: 0.3,
                      ChipState.SYMPATHETIC_THRESHOLD: 0.5,
                      ChipState.DORSAL_TRAP: 0.7}[state]

        for node in target_nodes:
            if node not in self.G.nodes: continue
            self.G.nodes[node]['health'] = max(0, self.G.nodes[node]['health'] - 100 * damage_pct)
            self.G.nodes[node]['state']  = 'compromised'
            self.G.nodes[node]['threat_type'] = threat_type

            affected   = sum(1 for n in self.G.nodes if self.G.nodes[n]['state'] != 'healthy')
            sar_stage  = self.riss.determine_sar_stage(threat_type, self.network_variability)
            riss_score = self.riss.calculate_riss(threat_type, affected, self.network_variability, sar_stage)
            self.G.nodes[node]['riss_score'] = riss_score

            impact = {ThreatType.RECON: 10, ThreatType.LATERAL_MOVEMENT: 25,
                      ThreatType.PERSISTENCE: 40, ThreatType.PRIVILEGE_ESCALATION: 35,
                      ThreatType.COMMAND_CONTROL: 45, ThreatType.EXFILTRATION: 50,
                      ThreatType.IMPACT: 60}.get(threat_type, 30)
            self.network_variability = max(10, self.network_variability - impact)

            sev = 'CRITICAL' if riss_score > 80 else 'HIGH' if riss_score > 60 else 'MEDIUM'
            ev  = ThreatEvent(node, threat_type, time.time(), riss_score, sev)
            events.append(ev)
            self.threat_history.append(ev)
            self.threats.add(node)
            print(f"   Node {node}: health={self.G.nodes[node]['health']:.0f} | RISS={riss_score} | SAR={sar_stage}")

        print(f"   Network Variability → {self.network_variability:.0f}/100")
        return events

    def comprehensive_sensing(self):
        positions = np.random.randn(len(self.G.nodes), 2) * 10
        health    = np.array([self.G.nodes[n]['health'] / 100.0 for n in self.G.nodes])
        activity  = np.array([self.G.nodes[n]['processing'] for n in self.G.nodes])
        temps     = np.array([self.G.nodes[n]['temperature'] for n in self.G.nodes])
        energy    = np.array([self.G.nodes[n]['energy'] for n in self.G.nodes])

        ns = {
            'node_positions': positions, 'node_health': health,
            'node_activity': activity, 'node_temperatures': temps,
            'node_energy': energy, 'ambient_temperature': 25.0,
            'node_velocities': np.random.randn(len(self.G.nodes), 2) * 0.1,
            'threat_signatures': {'chemical_signatures': np.random.randn(len(self.G.nodes), 5) * 0.1},
        }
        bio      = self.bio_fusion.sense_environment(ns)
        thermal  = self.thermal_energy.detect_thermal_anomalies(temps, 25.0)
        energy_r = self.thermal_energy.detect_energy_surges(energy)
        scores   = bio.get('fused_threat_assessment', {}).get('threat_scores', {})
        for n in thermal.get('thermal_anomalies', []):
            scores[n] = scores.get(n, 0) + 0.3
        for n in energy_r.get('energy_surges', []):
            scores[n] = scores.get(n, 0) + 0.4
        self.sensory_results    = {'bio': bio, 'thermal': thermal, 'energy': energy_r}
        self.threat_assessment  = {
            'combined_threat_scores': scores,
            'threat_nodes': [n for n, s in scores.items() if s > 0.5],
            'overall_threat_level': float(np.mean(list(scores.values()))) if scores else 0.0,
        }

    def isolate_and_regenerate(self):
        for node in list(self.threats):
            if node not in self.G.nodes: continue
            if self.G.nodes[node]['health'] <= 30:
                self.G.remove_node(node)
                self.isolated.add(node)
                new  = max(self.G.nodes) + 1 if self.G.nodes else 0
                self.G.add_node(new)
                self.G.nodes[new].update({
                    'health': 75.0, 'processing': 75.0, 'state': 'regenerated',
                    'temperature': 37.0, 'energy': 80.0, 'threat_type': None, 'riss_score': 0,
                })
                for nb in random.sample(list(self.G.nodes), min(3, len(self.G.nodes) - 1)):
                    if nb != new: self.G.add_edge(new, nb)
                self.network_variability = min(100, self.network_variability + 15)
        self.threats.clear()

    def run_protection_cycle(self):
        print("\n" + "=" * 60)
        self.comprehensive_sensing()
        self.current_metrics = self._compute_metrics()
        state = self.get_chip_state()
        print(f"📈 State: {state.value.upper()} | NV: {self.network_variability:.0f}/100")
        threat_type = random.choice(list(ThreatType))
        events = self.inject_threat_v4(threat_type=threat_type)
        if events:
            avg = sum(e.riss_score for e in events) / len(events)
            print(f"📊 RISS avg: {avg:.0f}/100 | Severity: {events[0].severity}")
        self.isolate_and_regenerate()
        print(f"✅ Cycle complete | Nodes: {len(self.G.nodes)} | Isolated: {len(self.isolated)}")

    def get_system_stats(self) -> Dict:
        riss_scores = [self.G.nodes[n].get('riss_score', 0) for n in self.G.nodes]
        active_riss = [s for s in riss_scores if s > 0]
        return {
            'network':  {'total': len(self.G.nodes), 'isolated': len(self.isolated),
                         'network_variability': self.network_variability},
            'riss':     {'avg': float(np.mean(active_riss)) if active_riss else 0,
                         'max': max(riss_scores) if riss_scores else 0,
                         'critical': sum(1 for s in riss_scores if s >= 80)},
            'threats':  {'total': len(self.threat_history),
                         'types': {t.value: sum(1 for e in self.threat_history
                                               if e.threat_type == t) for t in ThreatType}},
        }


# ============================================================================
# MAIN
# ============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Octo-Mycelial Defense System v4.0')
    parser.add_argument('--mode',   choices=['demo', 'simulate'], default='demo')
    parser.add_argument('--nodes',  type=int, default=25)
    parser.add_argument('--cycles', type=int, default=4)
    args = parser.parse_args()

    print("🧬 OCTO-MYCELIAL NEUROMORPHIC DEFENSE SYSTEM v4.0")
    chip = OctoMycelialChip(num_nodes=args.nodes)

    for cycle in range(args.cycles):
        print(f"\n🔄 CYCLE {cycle + 1}/{args.cycles}")
        chip.run_protection_cycle()

    stats = chip.get_system_stats()
    print(f"\n📊 Final Stats: {json.dumps(stats, indent=2)}")


if __name__ == "__main__":
    main()
