#!/usr/bin/env python3
"""
run_validation_batch.py – LUMINARK Validation Batch Processing Suite

Processes NSDT time-series CSV data through the LUMINARK engine for:
- SAP stage classification (0-9)
- Pressure score calculation
- Decision signal generation
- Failure mode signature detection
- Lead time validation
- Tumbling Inversion analysis

Supports batch processing of multiple datasets (NYIS, TVA, DUK, TEPC, etc.)
and generates classified output CSVs with full analysis.

Usage:
    python run_validation_batch.py --folder ./data/validation --output ./results
    python run_validation_batch.py --file ./data/validation/texas_2021.csv
"""

import argparse
import csv
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class NSDTVector:
    """NSDT vector representation (Complexity, Stability, Adaptability, Tension, Coherence)."""
    
    def __init__(self, complexity: float, stability: float, adaptability: float, 
                 tension: float, coherence: float):
        self.complexity = float(complexity)
        self.stability = float(stability)
        self.adaptability = float(adaptability)
        self.tension = float(tension)
        self.coherence = float(coherence)
    
    def to_list(self) -> List[float]:
        """Return as list for processing."""
        return [self.complexity, self.stability, self.adaptability, self.tension, self.coherence]
    
    def to_dict(self) -> Dict[str, float]:
        """Return as dictionary."""
        return {
            'complexity': self.complexity,
            'stability': self.stability,
            'adaptability': self.adaptability,
            'tension': self.tension,
            'coherence': self.coherence
        }


class StageClassifier:
    """SAP stage classifier using NSDT vectors."""
    
    # Stage boundaries (0-9)
    STAGE_BOUNDARIES = [0, 11.11, 22.22, 33.33, 44.44, 55.55, 66.66, 77.77, 88.88, 100.0]
    
    @staticmethod
    def compute_stage(nsdt_vec: NSDTVector) -> Dict:
        """
        Compute SAP stage from NSDT vector.
        
        Returns:
            Dictionary with stage, pressure_score, decision_signal, and analysis
        """
        c, s, a, t, co = nsdt_vec.complexity, nsdt_vec.stability, nsdt_vec.adaptability, nsdt_vec.tension, nsdt_vec.coherence
        
        # Primary stage from tension (0-9)
        stage = min(9, max(0, int(t / 11.11)))
        
        # Pressure score: (100 - stability) × (tension / 100)
        pressure_score = (100 - s) * (t / 100.0)
        
        # Decision signal: high pressure + low adaptability = urgent
        decision_signal = "CRITICAL" if pressure_score > 70 and a < 30 else \
                         "WARNING" if pressure_score > 50 and a < 50 else \
                         "CAUTION" if pressure_score > 30 else \
                         "NORMAL"
        
        # Tumbling Inversion analysis
        is_even_stage = stage % 2 == 0
        inversion_state = "Even: Physically Stable / Consciously Unstable" if is_even_stage else \
                         "Odd: Physically Unstable / Consciously Stable"
        
        # Stage 5 gateway detection (Witness Position)
        witness_score = 0.4 * a + 0.35 * co + 0.25 * (100 - abs(t - 50))
        is_witness = witness_score >= 55 and a >= 40 and t < (a + 30)
        perpendicular_visible = is_witness and abs(t - 50) < 25
        observer_effect = is_witness
        
        return {
            'stage': stage,
            'pressure_score': round(pressure_score, 2),
            'decision_signal': decision_signal,
            'complexity': c,
            'stability': s,
            'adaptability': a,
            'tension': t,
            'coherence': co,
            'inversion_state': inversion_state,
            'witness_score': round(witness_score, 1),
            'is_witness': is_witness,
            'perpendicular_axis_visible': perpendicular_visible,
            'observer_effect_active': observer_effect,
            'observer_effect_multiplier': 1.35 if observer_effect else 1.0
        }


class ValidationProcessor:
    """Process validation CSV files through LUMINARK engine."""
    
    REQUIRED_COLUMNS = ['complexity', 'stability', 'adaptability', 'tension', 'coherence']
    OPTIONAL_COLUMNS = ['timestamp', 'event_min_stage', 'lead_time_hours', 'event_type']
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path('./results')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.classifier = StageClassifier()
        self.validation_results = []
    
    def load_csv(self, csv_path: Path) -> pd.DataFrame:
        """Load and validate CSV file."""
        logger.info(f"Loading CSV: {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            raise
        
        # Check for required columns
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            logger.info(f"Available columns: {df.columns.tolist()}")
            raise ValueError(f"Missing columns: {missing_cols}")
        
        # Parse timestamp if present
        if 'timestamp' in df.columns:
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            except Exception as e:
                logger.warning(f"Could not parse timestamp column: {e}")
        
        logger.info(f"Loaded {len(df)} rows from {csv_path.name}")
        return df
    
    def classify_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classify all rows in dataframe."""
        logger.info(f"Classifying {len(df)} rows...")
        
        stages = []
        pressures = []
        signals = []
        inversions = []
        witness_scores = []
        perpendicular_flags = []
        observer_effects = []
        
        for idx, row in df.iterrows():
            try:
                nsdt_vec = NSDTVector(
                    row['complexity'],
                    row['stability'],
                    row['adaptability'],
                    row['tension'],
                    row['coherence']
                )
                result = self.classifier.compute_stage(nsdt_vec)
                
                stages.append(result['stage'])
                pressures.append(result['pressure_score'])
                signals.append(result['decision_signal'])
                inversions.append(result['inversion_state'])
                witness_scores.append(result['witness_score'])
                perpendicular_flags.append(result['perpendicular_axis_visible'])
                observer_effects.append(result['observer_effect_multiplier'])
            
            except Exception as e:
                logger.warning(f"Error classifying row {idx}: {e}")
                stages.append(None)
                pressures.append(None)
                signals.append("ERROR")
                inversions.append(None)
                witness_scores.append(None)
                perpendicular_flags.append(False)
                observer_effects.append(1.0)
        
        df['sap_stage'] = stages
        df['pressure_score'] = pressures
        df['decision_signal'] = signals
        df['inversion_state'] = inversions
        df['witness_score'] = witness_scores
        df['perpendicular_axis_visible'] = perpendicular_flags
        df['observer_effect_multiplier'] = observer_effects
        
        logger.info(f"Classification complete. Stages: {min(stages)}-{max(stages)}")
        return df
    
    def analyze_failure_signatures(self, df: pd.DataFrame, event_type: Optional[str] = None) -> Dict:
        """Analyze failure mode signatures."""
        logger.info("Analyzing failure mode signatures...")
        
        # Average NSDT vector
        avg_vector = df[self.REQUIRED_COLUMNS].mean()
        
        # Stage distribution
        stage_dist = df['sap_stage'].value_counts().sort_index().to_dict()
        
        # Pressure statistics
        pressure_stats = {
            'mean': df['pressure_score'].mean(),
            'max': df['pressure_score'].max(),
            'min': df['pressure_score'].min(),
            'std': df['pressure_score'].std()
        }
        
        # Decision signal distribution
        signal_dist = df['decision_signal'].value_counts().to_dict()
        
        # Lead time (if available)
        lead_time = None
        if 'lead_time_hours' in df.columns:
            lead_time = df['lead_time_hours'].mean()
        
        # Critical events (stage <= 1 or pressure > 70)
        critical_events = df[(df['sap_stage'] <= 1) | (df['pressure_score'] > 70)]
        critical_count = len(critical_events)
        
        return {
            'event_type': event_type,
            'total_rows': len(df),
            'avg_nsdt_vector': avg_vector.to_dict(),
            'stage_distribution': stage_dist,
            'pressure_stats': pressure_stats,
            'signal_distribution': signal_dist,
            'lead_time_hours': lead_time,
            'critical_count': critical_count,
            'critical_percentage': (critical_count / len(df) * 100) if len(df) > 0 else 0
        }
    
    def process_file(self, csv_path: Path, event_type: Optional[str] = None) -> Tuple[pd.DataFrame, Dict]:
        """Process single CSV file."""
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {csv_path.name}")
        logger.info(f"{'='*60}")
        
        # Load
        df = self.load_csv(csv_path)
        
        # Classify
        df = self.classify_dataframe(df)
        
        # Analyze
        analysis = self.analyze_failure_signatures(df, event_type)
        
        # Save classified output
        output_path = self.output_dir / csv_path.with_name(f"{csv_path.stem}_classified.csv").name
        df.to_csv(output_path, index=False)
        logger.info(f"Saved classified output: {output_path}")
        
        # Log summary
        logger.info(f"\nSummary:")
        logger.info(f"  Total rows: {len(df)}")
        logger.info(f"  Stage range: {df['sap_stage'].min()}-{df['sap_stage'].max()}")
        logger.info(f"  Final stage: {df['sap_stage'].iloc[-1]}")
        logger.info(f"  Pressure mean: {df['pressure_score'].mean():.2f}")
        logger.info(f"  Critical events: {analysis['critical_count']} ({analysis['critical_percentage']:.1f}%)")
        logger.info(f"  Signal distribution: {analysis['signal_distribution']}")
        
        self.validation_results.append({
            'file': csv_path.name,
            'analysis': analysis,
            'output_path': str(output_path)
        })
        
        return df, analysis
    
    def process_folder(self, folder_path: Path) -> List[Dict]:
        """Process all CSV files in folder."""
        csv_files = list(folder_path.glob("*.csv"))
        
        if not csv_files:
            logger.warning(f"No CSV files found in {folder_path}")
            return []
        
        logger.info(f"Found {len(csv_files)} CSV files to process")
        
        for csv_file in csv_files:
            try:
                self.process_file(csv_file)
            except Exception as e:
                logger.error(f"Error processing {csv_file.name}: {e}")
                continue
        
        return self.validation_results
    
    def generate_summary_report(self) -> Dict:
        """Generate summary report of all validations."""
        logger.info(f"\n{'='*60}")
        logger.info("VALIDATION SUMMARY REPORT")
        logger.info(f"{'='*60}")
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_files_processed': len(self.validation_results),
            'files': []
        }
        
        for result in self.validation_results:
            logger.info(f"\n{result['file']}:")
            logger.info(f"  Total rows: {result['analysis']['total_rows']}")
            logger.info(f"  Pressure mean: {result['analysis']['pressure_stats']['mean']:.2f}")
            logger.info(f"  Critical events: {result['analysis']['critical_count']} ({result['analysis']['critical_percentage']:.1f}%)")
            logger.info(f"  Output: {result['output_path']}")
            
            summary['files'].append({
                'filename': result['file'],
                'total_rows': result['analysis']['total_rows'],
                'stage_distribution': result['analysis']['stage_distribution'],
                'pressure_mean': result['analysis']['pressure_stats']['mean'],
                'critical_events': result['analysis']['critical_count'],
                'critical_percentage': result['analysis']['critical_percentage'],
                'output_path': result['output_path']
            })
        
        # Save summary to JSON
        summary_path = self.output_dir / 'validation_summary.json'
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"\nSummary saved to: {summary_path}")
        return summary


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='LUMINARK Validation Batch Processing Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all CSVs in folder
  python run_validation_batch.py --folder ./data/validation --output ./results
  
  # Process single file
  python run_validation_batch.py --file ./data/validation/texas_2021.csv
  
  # Process with custom output directory
  python run_validation_batch.py --folder ./data --output ./analysis_results
        """
    )
    
    parser.add_argument('--folder', type=Path, help='Folder containing CSV files')
    parser.add_argument('--file', type=Path, help='Single CSV file to process')
    parser.add_argument('--output', type=Path, default=Path('./results'), help='Output directory')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.folder and not args.file:
        parser.print_help()
        logger.error("Please provide either --folder or --file")
        sys.exit(1)
    
    # Create processor
    processor = ValidationProcessor(args.output)
    
    try:
        # Process files
        if args.file:
            if not args.file.exists():
                logger.error(f"File not found: {args.file}")
                sys.exit(1)
            processor.process_file(args.file)
        
        elif args.folder:
            if not args.folder.exists():
                logger.error(f"Folder not found: {args.folder}")
                sys.exit(1)
            processor.process_folder(args.folder)
        
        # Generate summary
        processor.generate_summary_report()
        
        logger.info("\n✅ Validation batch processing complete!")
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
