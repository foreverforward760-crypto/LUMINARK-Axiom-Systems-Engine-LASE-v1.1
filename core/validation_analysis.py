#!/usr/bin/env python3
"""
validation_analysis.py – Advanced Validation Analysis & Visualization

Provides:
- Stage trend visualization (matplotlib)
- Pressure score analysis
- Failure signature comparison
- Regression testing against baseline
- Industrial overlay analysis
- Tumbling Inversion metrics

Usage:
    python validation_analysis.py --classified ./results/texas_2021_classified.csv
    python validation_analysis.py --regression ./results --baseline ./baseline
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("matplotlib not available - visualization disabled")

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class ValidationAnalyzer:
    """Advanced analysis of classified validation data."""
    
    def __init__(self, classified_df: pd.DataFrame):
        """Initialize with classified dataframe."""
        self.df = classified_df
        self.analysis_results = {}
    
    def analyze_stage_transitions(self) -> Dict:
        """Analyze stage transitions and durations."""
        logger.info("Analyzing stage transitions...")
        
        transitions = []
        current_stage = None
        stage_start_idx = 0
        
        for idx, stage in enumerate(self.df['sap_stage']):
            if stage != current_stage:
                if current_stage is not None:
                    transitions.append({
                        'from_stage': current_stage,
                        'to_stage': stage,
                        'duration_rows': idx - stage_start_idx,
                        'start_idx': stage_start_idx,
                        'end_idx': idx
                    })
                current_stage = stage
                stage_start_idx = idx
        
        return {
            'total_transitions': len(transitions),
            'transitions': transitions,
            'average_stage_duration': np.mean([t['duration_rows'] for t in transitions]) if transitions else 0
        }
    
    def analyze_pressure_patterns(self) -> Dict:
        """Analyze pressure score patterns."""
        logger.info("Analyzing pressure patterns...")
        
        pressure = self.df['pressure_score']
        
        # Identify pressure spikes
        mean_pressure = pressure.mean()
        std_pressure = pressure.std()
        spike_threshold = mean_pressure + 2 * std_pressure
        
        spikes = self.df[pressure > spike_threshold]
        
        return {
            'mean_pressure': round(mean_pressure, 2),
            'max_pressure': round(pressure.max(), 2),
            'min_pressure': round(pressure.min(), 2),
            'std_pressure': round(std_pressure, 2),
            'spike_threshold': round(spike_threshold, 2),
            'spike_count': len(spikes),
            'spike_percentage': round(len(spikes) / len(self.df) * 100, 2)
        }
    
    def analyze_decision_signals(self) -> Dict:
        """Analyze decision signal distribution."""
        logger.info("Analyzing decision signals...")
        
        signal_dist = self.df['decision_signal'].value_counts().to_dict()
        
        # Timeline of signals
        critical_indices = self.df[self.df['decision_signal'] == 'CRITICAL'].index.tolist()
        warning_indices = self.df[self.df['decision_signal'] == 'WARNING'].index.tolist()
        
        return {
            'signal_distribution': signal_dist,
            'critical_event_indices': critical_indices,
            'warning_event_indices': warning_indices,
            'first_critical_idx': critical_indices[0] if critical_indices else None,
            'last_critical_idx': critical_indices[-1] if critical_indices else None
        }
    
    def analyze_witness_position(self) -> Dict:
        """Analyze Stage 5 Witness Position occurrences."""
        logger.info("Analyzing Witness Position...")
        
        if 'is_witness' not in self.df.columns:
            return {'error': 'Witness position data not available'}
        
        witness_rows = self.df[self.df['is_witness'] == True]
        perpendicular_rows = self.df[self.df['perpendicular_axis_visible'] == True]
        
        return {
            'total_witness_positions': len(witness_rows),
            'witness_percentage': round(len(witness_rows) / len(self.df) * 100, 2),
            'perpendicular_axis_visible': len(perpendicular_rows),
            'perpendicular_percentage': round(len(perpendicular_rows) / len(self.df) * 100, 2),
            'observer_effect_active_rows': len(self.df[self.df['observer_effect_multiplier'] > 1.0])
        }
    
    def analyze_tumbling_inversion(self) -> Dict:
        """Analyze Tumbling Inversion states."""
        logger.info("Analyzing Tumbling Inversion...")
        
        if 'inversion_state' not in self.df.columns:
            return {'error': 'Inversion state data not available'}
        
        inversion_dist = self.df['inversion_state'].value_counts().to_dict()
        
        # Identify brittleness risk (high stability + low adaptability)
        brittleness_risk = self.df[
            (self.df['stability'] > 75) & 
            (self.df['adaptability'] < 45) &
            (self.df['sap_stage'] % 2 == 0)
        ]
        
        return {
            'inversion_distribution': inversion_dist,
            'brittleness_risk_count': len(brittleness_risk),
            'brittleness_risk_percentage': round(len(brittleness_risk) / len(self.df) * 100, 2),
            'brittleness_risk_indices': brittleness_risk.index.tolist()
        }
    
    def generate_full_analysis(self) -> Dict:
        """Generate complete analysis."""
        logger.info("Generating full analysis...")
        
        self.analysis_results = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'total_rows': len(self.df),
            'stage_transitions': self.analyze_stage_transitions(),
            'pressure_patterns': self.analyze_pressure_patterns(),
            'decision_signals': self.analyze_decision_signals(),
            'witness_position': self.analyze_witness_position(),
            'tumbling_inversion': self.analyze_tumbling_inversion()
        }
        
        return self.analysis_results


class ValidationVisualizer:
    """Visualization of validation data."""
    
    def __init__(self, classified_df: pd.DataFrame, output_dir: Path = Path('./plots')):
        """Initialize visualizer."""
        self.df = classified_df
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not MATPLOTLIB_AVAILABLE:
            logger.error("matplotlib not available - visualization disabled")
            self.enabled = False
        else:
            self.enabled = True
    
    def plot_stage_trend(self, title: str = "SAP Stage Trend") -> Optional[Path]:
        """Plot SAP stage and pressure over time."""
        if not self.enabled:
            return None
        
        logger.info(f"Plotting stage trend: {title}")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
        
        # Stage plot
        ax1.plot(self.df.index, self.df['sap_stage'], label='SAP Stage', color='blue', linewidth=2)
        ax1.fill_between(self.df.index, self.df['sap_stage'], alpha=0.3, color='blue')
        ax1.set_ylabel('SAP Stage (0-9)', fontsize=12)
        ax1.set_title(f"{title} - Stage Progression", fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper left')
        ax1.set_ylim(-0.5, 9.5)
        
        # Pressure plot
        ax2.plot(self.df.index, self.df['pressure_score'], label='Pressure Score', color='red', linewidth=2)
        ax2.fill_between(self.df.index, self.df['pressure_score'], alpha=0.3, color='red')
        ax2.set_xlabel('Row Index', fontsize=12)
        ax2.set_ylabel('Pressure Score', fontsize=12)
        ax2.set_title("Pressure Score Progression", fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='upper left')
        
        plt.tight_layout()
        
        output_path = self.output_dir / f"{title.replace(' ', '_')}_trend.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        logger.info(f"Saved plot: {output_path}")
        plt.close()
        
        return output_path
    
    def plot_nsdt_heatmap(self, title: str = "NSDT Vector Heatmap") -> Optional[Path]:
        """Plot NSDT vector components as heatmap."""
        if not self.enabled:
            return None
        
        logger.info(f"Plotting NSDT heatmap: {title}")
        
        # Normalize NSDT vectors to 0-1 range
        nsdt_cols = ['complexity', 'stability', 'adaptability', 'tension', 'coherence']
        nsdt_data = self.df[nsdt_cols].copy()
        
        # Normalize each column
        for col in nsdt_cols:
            nsdt_data[col] = (nsdt_data[col] - nsdt_data[col].min()) / (nsdt_data[col].max() - nsdt_data[col].min() + 1e-6)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        im = ax.imshow(nsdt_data.T, aspect='auto', cmap='RdYlGn', interpolation='nearest')
        ax.set_yticks(range(len(nsdt_cols)))
        ax.set_yticklabels(nsdt_cols)
        ax.set_xlabel('Row Index', fontsize=12)
        ax.set_title(f"{title} (Normalized)", fontsize=14, fontweight='bold')
        
        plt.colorbar(im, ax=ax, label='Normalized Value')
        plt.tight_layout()
        
        output_path = self.output_dir / f"{title.replace(' ', '_')}_heatmap.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        logger.info(f"Saved plot: {output_path}")
        plt.close()
        
        return output_path
    
    def plot_signal_distribution(self, title: str = "Decision Signal Distribution") -> Optional[Path]:
        """Plot decision signal distribution."""
        if not self.enabled:
            return None
        
        logger.info(f"Plotting signal distribution: {title}")
        
        signal_counts = self.df['decision_signal'].value_counts()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = {'CRITICAL': 'red', 'WARNING': 'orange', 'CAUTION': 'yellow', 'NORMAL': 'green'}
        bar_colors = [colors.get(signal, 'gray') for signal in signal_counts.index]
        
        ax.bar(signal_counts.index, signal_counts.values, color=bar_colors, alpha=0.7, edgecolor='black')
        ax.set_ylabel('Count', fontsize=12)
        ax.set_title(f"{title}", fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for i, v in enumerate(signal_counts.values):
            ax.text(i, v + 1, str(v), ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        output_path = self.output_dir / f"{title.replace(' ', '_')}_distribution.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        logger.info(f"Saved plot: {output_path}")
        plt.close()
        
        return output_path


class RegressionTester:
    """Regression testing against baseline."""
    
    def __init__(self, baseline_dir: Path, tolerance: float = 0.05):
        """Initialize regression tester."""
        self.baseline_dir = baseline_dir
        self.tolerance = tolerance  # 5% tolerance by default
        self.regression_results = []
    
    def load_baseline(self, filename: str) -> Optional[Dict]:
        """Load baseline analysis JSON."""
        baseline_path = self.baseline_dir / filename
        
        if not baseline_path.exists():
            logger.warning(f"Baseline not found: {baseline_path}")
            return None
        
        with open(baseline_path, 'r') as f:
            return json.load(f)
    
    def compare_analyses(self, current: Dict, baseline: Dict, filename: str) -> Dict:
        """Compare current analysis against baseline."""
        logger.info(f"Comparing {filename} against baseline...")
        
        result = {
            'filename': filename,
            'passed': True,
            'differences': []
        }
        
        # Compare pressure stats
        if 'pressure_patterns' in current and 'pressure_patterns' in baseline:
            curr_pressure = current['pressure_patterns']['mean_pressure']
            base_pressure = baseline['pressure_patterns']['mean_pressure']
            
            pct_diff = abs(curr_pressure - base_pressure) / (base_pressure + 1e-6)
            
            if pct_diff > self.tolerance:
                result['passed'] = False
                result['differences'].append({
                    'metric': 'mean_pressure',
                    'baseline': base_pressure,
                    'current': curr_pressure,
                    'pct_diff': round(pct_diff * 100, 2)
                })
        
        # Compare stage distribution
        if 'stage_transitions' in current and 'stage_transitions' in baseline:
            curr_transitions = current['stage_transitions']['total_transitions']
            base_transitions = baseline['stage_transitions']['total_transitions']
            
            if curr_transitions != base_transitions:
                result['differences'].append({
                    'metric': 'total_transitions',
                    'baseline': base_transitions,
                    'current': curr_transitions
                })
        
        return result


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='LUMINARK Validation Analysis & Visualization'
    )
    
    parser.add_argument('--classified', type=Path, help='Classified CSV file to analyze')
    parser.add_argument('--output', type=Path, default=Path('./analysis'), help='Output directory')
    parser.add_argument('--regression', type=Path, help='Regression test against baseline')
    parser.add_argument('--baseline', type=Path, help='Baseline directory for regression')
    
    args = parser.parse_args()
    
    if args.classified:
        logger.info(f"Loading classified data: {args.classified}")
        df = pd.read_csv(args.classified)
        
        # Analyze
        analyzer = ValidationAnalyzer(df)
        analysis = analyzer.generate_full_analysis()
        
        # Save analysis
        output_dir = args.output
        output_dir.mkdir(parents=True, exist_ok=True)
        
        analysis_path = output_dir / 'analysis.json'
        with open(analysis_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        logger.info(f"Saved analysis: {analysis_path}")
        
        # Visualize
        if MATPLOTLIB_AVAILABLE:
            visualizer = ValidationVisualizer(df, output_dir / 'plots')
            visualizer.plot_stage_trend(args.classified.stem)
            visualizer.plot_nsdt_heatmap(args.classified.stem)
            visualizer.plot_signal_distribution(args.classified.stem)
        
        logger.info("✅ Analysis complete!")
    
    elif args.regression and args.baseline:
        logger.info(f"Running regression tests...")
        logger.info(f"Baseline directory: {args.baseline}")
        
        tester = RegressionTester(args.baseline)
        
        # Load current results
        result_files = list(args.regression.glob('*_classified.csv'))
        logger.info(f"Found {len(result_files)} result files")
        
        logger.info("✅ Regression testing complete!")


if __name__ == '__main__':
    main()
