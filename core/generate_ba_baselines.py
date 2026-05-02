#!/usr/bin/env python3
"""
generate_ba_baselines.py – Generate baseline thresholds and failure mode signatures for 27 BAs

Creates:
- Baseline pressure thresholds per BA
- Failure mode signature profiles
- Regional comparative analysis
- Risk classification matrix
- Production-ready baseline JSON for regression testing

Usage:
    python generate_ba_baselines.py --results ./results --output ./baseline
"""

import argparse
import csv
import json
import logging
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class BaselineGenerator:
    """Generate baselines and failure mode signatures from validation results."""
    
    def __init__(self, results_dir: Path, output_dir: Path = Path('./baseline')):
        self.results_dir = results_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ba_analyses = {}
        self.regional_stats = {}
    
    def load_classified_csvs(self) -> Dict[str, pd.DataFrame]:
        """Load all classified CSV files from results directory."""
        logger.info(f"Loading classified CSVs from {self.results_dir}...")
        
        classified_files = list(self.results_dir.glob("ba_*_classified.csv"))
        logger.info(f"Found {len(classified_files)} classified files")
        
        dataframes = {}
        for filepath in classified_files:
            ba_code = filepath.name.split('_')[1].upper()
            try:
                df = pd.read_csv(filepath)
                dataframes[ba_code] = df
            except Exception as e:
                logger.warning(f"Error loading {filepath}: {e}")
        
        return dataframes
    
    def analyze_ba_metrics(self, ba_code: str, df: pd.DataFrame) -> Dict:
        """Analyze metrics for a single BA."""
        analysis = {
            'ba_code': ba_code,
            'total_rows': len(df),
            'stage_stats': {
                'min': int(df['sap_stage'].min()),
                'max': int(df['sap_stage'].max()),
                'mean': round(float(df['sap_stage'].mean()), 2),
                'std': round(float(df['sap_stage'].std()), 2)
            },
            'pressure_stats': {
                'min': round(float(df['pressure_score'].min()), 2),
                'max': round(float(df['pressure_score'].max()), 2),
                'mean': round(float(df['pressure_score'].mean()), 2),
                'std': round(float(df['pressure_score'].std()), 2),
                'p95': round(float(df['pressure_score'].quantile(0.95)), 2),
                'p99': round(float(df['pressure_score'].quantile(0.99)), 2)
            },
            'signal_distribution': df['decision_signal'].value_counts().to_dict(),
            'critical_events': int((df['decision_signal'] == 'CRITICAL').sum()),
            'critical_percentage': round(
                (df['decision_signal'] == 'CRITICAL').sum() / len(df) * 100, 2
            ),
            'witness_positions': int(df['is_witness'].sum()) if 'is_witness' in df.columns else 0,
            'observer_effect_active': int((df['observer_effect_multiplier'] > 1.0).sum()) if 'observer_effect_multiplier' in df.columns else 0
        }
        
        return analysis
    
    def compute_regional_baselines(self, ba_data: Dict[str, Dict]) -> Dict:
        """Compute regional baseline statistics."""
        logger.info("Computing regional baselines...")
        
        regional_groups = {}
        
        for ba_code, analysis in ba_data.items():
            # Extract region from ba_code (would need mapping in production)
            # For now, use volatility as proxy
            region = 'unknown'
            if ba_code in ['NYIS', 'PJM', 'MISO', 'TVA', 'SERC', 'DUK']:
                region = 'eastern'
            elif ba_code in ['WECC', 'CAISO', 'SPP', 'BPA', 'NWE', 'PGE', 'SCE', 'SDGE']:
                region = 'western'
            elif ba_code in ['ERCOT', 'AES']:
                region = 'texas'
            else:
                region = 'central'
            
            if region not in regional_groups:
                regional_groups[region] = []
            
            regional_groups[region].append(analysis)
        
        regional_baselines = {}
        for region, analyses in regional_groups.items():
            pressure_means = [a['pressure_stats']['mean'] for a in analyses]
            critical_percentages = [a['critical_percentage'] for a in analyses]
            
            regional_baselines[region] = {
                'ba_count': len(analyses),
                'pressure_mean_avg': round(np.mean(pressure_means), 2),
                'pressure_mean_std': round(np.std(pressure_means), 2),
                'critical_percentage_avg': round(np.mean(critical_percentages), 2),
                'critical_percentage_std': round(np.std(critical_percentages), 2),
                'threshold_warning': round(np.mean(pressure_means) + np.std(pressure_means), 2),
                'threshold_critical': round(np.mean(pressure_means) + 2 * np.std(pressure_means), 2)
            }
        
        return regional_baselines
    
    def generate_failure_signatures(self, ba_data: Dict[str, Dict]) -> Dict:
        """Generate failure mode signature profiles."""
        logger.info("Generating failure mode signatures...")
        
        signatures = {
            'cascade_failure': {
                'description': 'Rapid stage progression with high pressure escalation',
                'indicators': {
                    'stage_progression_rate': '>1 stage per hour',
                    'pressure_escalation': '>10 points per hour',
                    'adaptability_decline': '>5 points per hour'
                },
                'lead_time_range': '1-4 hours',
                'intervention_priority': 'CRITICAL'
            },
            'oscillation_instability': {
                'description': 'Repeated high-tension cycles with unstable equilibrium',
                'indicators': {
                    'tension_oscillation_amplitude': '>30 points',
                    'cycle_frequency': '4-8 hour cycles',
                    'coherence_degradation': 'progressive'
                },
                'lead_time_range': '6-12 hours',
                'intervention_priority': 'HIGH'
            },
            'brittleness_risk': {
                'description': 'High stability masking low adaptability (Tumbling Inversion)',
                'indicators': {
                    'stability': '>80',
                    'adaptability': '<40',
                    'stage_parity': 'even',
                    'crystallization_risk': 'high'
                },
                'lead_time_range': '8-24 hours',
                'intervention_priority': 'MEDIUM'
            }
        }
        
        return signatures
    
    def generate_risk_matrix(self, ba_data: Dict[str, Dict]) -> Dict:
        """Generate BA risk classification matrix."""
        logger.info("Generating risk classification matrix...")
        
        risk_matrix = {}
        
        for ba_code, analysis in ba_data.items():
            pressure_mean = analysis['pressure_stats']['mean']
            critical_pct = analysis['critical_percentage']
            stage_max = analysis['stage_stats']['max']
            
            # Risk classification
            if critical_pct > 30 or pressure_mean > 50 or stage_max >= 8:
                risk_level = 'HIGH'
            elif critical_pct > 10 or pressure_mean > 30 or stage_max >= 6:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            risk_matrix[ba_code] = {
                'risk_level': risk_level,
                'pressure_mean': pressure_mean,
                'critical_percentage': critical_pct,
                'max_stage_observed': stage_max,
                'monitoring_frequency': 'hourly' if risk_level == 'HIGH' else 'daily',
                'intervention_threshold': 50 if risk_level == 'HIGH' else 70
            }
        
        return risk_matrix
    
    def generate_all_baselines(self) -> Dict:
        """Generate all baseline artifacts."""
        logger.info("="*60)
        logger.info("BASELINE GENERATION")
        logger.info("="*60)
        
        # Load classified data
        dataframes = self.load_classified_csvs()
        
        # Analyze each BA
        logger.info(f"\nAnalyzing {len(dataframes)} BAs...")
        ba_data = {}
        for ba_code, df in dataframes.items():
            analysis = self.analyze_ba_metrics(ba_code, df)
            ba_data[ba_code] = analysis
            logger.info(f"  {ba_code}: pressure_mean={analysis['pressure_stats']['mean']}, critical={analysis['critical_percentage']}%")
        
        # Compute regional baselines
        regional_baselines = self.compute_regional_baselines(ba_data)
        
        # Generate failure signatures
        failure_signatures = self.generate_failure_signatures(ba_data)
        
        # Generate risk matrix
        risk_matrix = self.generate_risk_matrix(ba_data)
        
        # Compile all baselines
        all_baselines = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'ba_count': len(ba_data),
            'ba_analyses': ba_data,
            'regional_baselines': regional_baselines,
            'failure_signatures': failure_signatures,
            'risk_matrix': risk_matrix,
            'global_thresholds': {
                'pressure_warning': 40,
                'pressure_critical': 70,
                'stage_warning': 5,
                'stage_critical': 7,
                'critical_event_percentage_warning': 15,
                'critical_event_percentage_critical': 30
            }
        }
        
        return all_baselines
    
    def save_baselines(self, baselines: Dict) -> Path:
        """Save baselines to JSON."""
        baseline_path = self.output_dir / 'ba_baselines.json'
        
        with open(baseline_path, 'w') as f:
            json.dump(baselines, f, indent=2)
        
        logger.info(f"\nSaved baselines: {baseline_path}")
        return baseline_path
    
    def save_ba_summary_csv(self, baselines: Dict) -> Path:
        """Save BA summary as CSV for easy viewing."""
        summary_path = self.output_dir / 'ba_summary.csv'
        
        with open(summary_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'BA Code', 'Pressure Mean', 'Pressure Max', 'Pressure P95',
                'Critical %', 'Max Stage', 'Risk Level', 'Monitoring Freq', 'Intervention Threshold'
            ])
            
            for ba_code in sorted(baselines['ba_analyses'].keys()):
                analysis = baselines['ba_analyses'][ba_code]
                risk = baselines['risk_matrix'][ba_code]
                
                writer.writerow([
                    ba_code,
                    analysis['pressure_stats']['mean'],
                    analysis['pressure_stats']['max'],
                    analysis['pressure_stats']['p95'],
                    analysis['critical_percentage'],
                    analysis['stage_stats']['max'],
                    risk['risk_level'],
                    risk['monitoring_frequency'],
                    risk['intervention_threshold']
                ])
        
        logger.info(f"Saved BA summary: {summary_path}")
        return summary_path
    
    def save_regional_summary(self, baselines: Dict) -> Path:
        """Save regional summary."""
        regional_path = self.output_dir / 'regional_baselines.json'
        
        with open(regional_path, 'w') as f:
            json.dump(baselines['regional_baselines'], f, indent=2)
        
        logger.info(f"Saved regional baselines: {regional_path}")
        return regional_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate baseline thresholds and failure mode signatures'
    )
    
    parser.add_argument('--results', type=Path, default=Path('./results'),
                       help='Results directory with classified CSVs')
    parser.add_argument('--output', type=Path, default=Path('./baseline'),
                       help='Output directory for baselines')
    
    args = parser.parse_args()
    
    generator = BaselineGenerator(args.results, args.output)
    
    try:
        # Generate all baselines
        baselines = generator.generate_all_baselines()
        
        # Save artifacts
        generator.save_baselines(baselines)
        generator.save_ba_summary_csv(baselines)
        generator.save_regional_summary(baselines)
        
        logger.info("\n" + "="*60)
        logger.info("✅ Baseline generation complete!")
        logger.info(f"Output directory: {args.output}")
        logger.info("\nGenerated files:")
        logger.info("  - ba_baselines.json (full baseline data)")
        logger.info("  - ba_summary.csv (BA summary table)")
        logger.info("  - regional_baselines.json (regional statistics)")
        logger.info("\nNext steps:")
        logger.info("  1. Review baselines for accuracy")
        logger.info("  2. Deploy baselines for regression testing")
        logger.info("  3. Monitor new datasets against thresholds")
        logger.info("="*60)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
