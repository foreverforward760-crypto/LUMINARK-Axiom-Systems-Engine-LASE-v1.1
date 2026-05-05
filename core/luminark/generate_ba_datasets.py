#!/usr/bin/env python3
"""
generate_ba_datasets.py – Generate synthetic NSDT validation datasets for 27 US Balancing Authorities

Generates realistic NSDT time-series data for all major US BAs:
- Eastern Interconnection: NYIS, PJM, MISO, TVA, SERC, Duke
- Western Interconnection: WECC, CAISO, SPP, BPA
- Texas: ERCOT
- Others: NEISO, NYISO, PSEG, etc.

Each dataset includes:
- 24-hour hourly NSDT vectors
- Realistic crisis patterns (Stage 5 transitions)
- Failure mode signatures
- Lead time tracking
- Event type classification

Usage:
    python generate_ba_datasets.py --output ./data/validation --count 27
"""

import argparse
import csv
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# 27 US Balancing Authorities
BALANCING_AUTHORITIES = [
    # Eastern Interconnection
    ('NYIS', 'New York ISO', 'eastern', 'high_volatility'),
    ('PJM', 'PJM Interconnection', 'eastern', 'medium_volatility'),
    ('MISO', 'Midcontinent ISO', 'eastern', 'medium_volatility'),
    ('TVA', 'Tennessee Valley Authority', 'eastern', 'low_volatility'),
    ('SERC', 'SERC Reliability Corporation', 'eastern', 'medium_volatility'),
    ('DUK', 'Duke Energy', 'eastern', 'low_volatility'),
    
    # Western Interconnection
    ('WECC', 'Western Electricity Coordinating Council', 'western', 'high_volatility'),
    ('CAISO', 'California ISO', 'western', 'high_volatility'),
    ('SPP', 'Southwest Power Pool', 'western', 'medium_volatility'),
    ('BPA', 'Bonneville Power Administration', 'western', 'low_volatility'),
    
    # Texas
    ('ERCOT', 'Electric Reliability Council of Texas', 'texas', 'high_volatility'),
    
    # New England
    ('NEISO', 'New England ISO', 'eastern', 'medium_volatility'),
    
    # Additional Eastern
    ('PSEG', 'Public Service Enterprise Group', 'eastern', 'low_volatility'),
    ('CONED', 'Consolidated Edison', 'eastern', 'medium_volatility'),
    ('NYSEG', 'New York State Electric & Gas', 'eastern', 'low_volatility'),
    ('PECO', 'PECO Energy', 'eastern', 'low_volatility'),
    ('AEP', 'American Electric Power', 'eastern', 'medium_volatility'),
    ('FirstEnergy', 'FirstEnergy Corp', 'eastern', 'medium_volatility'),
    
    # Additional Western
    ('NWE', 'Northwestern Energy', 'western', 'low_volatility'),
    ('PGE', 'Portland General Electric', 'western', 'low_volatility'),
    ('SCE', 'Southern California Edison', 'western', 'high_volatility'),
    ('SDGE', 'San Diego Gas & Electric', 'western', 'medium_volatility'),
    
    # Additional Texas/Central
    ('AES', 'AES Corporation', 'texas', 'medium_volatility'),
    ('Xcel', 'Xcel Energy', 'central', 'low_volatility'),
    ('OGE', 'Oklahoma Gas & Electric', 'central', 'low_volatility'),
    ('Ameren', 'Ameren Corporation', 'central', 'low_volatility'),
    ('Alliant', 'Alliant Energy', 'central', 'low_volatility'),
]


class NSBTDatasetGenerator:
    """Generate synthetic NSDT datasets for Balancing Authorities."""
    
    def __init__(self, output_dir: Path = Path('./data/validation')):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_normal_pattern(self, hours: int = 24) -> List[Tuple]:
        """Generate normal operating NSDT pattern (low stress)."""
        pattern = []
        for h in range(hours):
            complexity = 40 + np.random.normal(0, 5)
            stability = 70 + np.random.normal(0, 5)
            adaptability = 60 + np.random.normal(0, 5)
            tension = 30 + np.random.normal(0, 5)
            coherence = 70 + np.random.normal(0, 5)
            
            pattern.append((
                np.clip(complexity, 0, 100),
                np.clip(stability, 0, 100),
                np.clip(adaptability, 0, 100),
                np.clip(tension, 0, 100),
                np.clip(coherence, 0, 100)
            ))
        
        return pattern
    
    def generate_crisis_pattern(self, hours: int = 24, crisis_type: str = 'cascade') -> List[Tuple]:
        """Generate crisis NSDT pattern with Stage 5 transition."""
        pattern = []
        
        if crisis_type == 'cascade':
            # Cascading failure: rapid stage progression
            for h in range(hours):
                progress = h / hours
                complexity = 40 + progress * 55 + np.random.normal(0, 3)
                stability = 70 - progress * 65 + np.random.normal(0, 3)
                adaptability = 60 - progress * 45 + np.random.normal(0, 3)
                tension = 30 + progress * 70 + np.random.normal(0, 3)
                coherence = 70 - progress * 50 + np.random.normal(0, 3)
                
                pattern.append((
                    np.clip(complexity, 0, 100),
                    np.clip(stability, 0, 100),
                    np.clip(adaptability, 0, 100),
                    np.clip(tension, 0, 100),
                    np.clip(coherence, 0, 100)
                ))
        
        elif crisis_type == 'oscillation':
            # Oscillating instability: high tension swings
            for h in range(hours):
                cycle = (h % 6) / 6
                complexity = 50 + 30 * np.sin(cycle * 2 * np.pi) + np.random.normal(0, 3)
                stability = 50 + 30 * np.cos(cycle * 2 * np.pi) + np.random.normal(0, 3)
                adaptability = 40 + 20 * np.sin(cycle * 2 * np.pi) + np.random.normal(0, 3)
                tension = 50 + 40 * np.sin(cycle * 2 * np.pi) + np.random.normal(0, 3)
                coherence = 50 + 20 * np.cos(cycle * 2 * np.pi) + np.random.normal(0, 3)
                
                pattern.append((
                    np.clip(complexity, 0, 100),
                    np.clip(stability, 0, 100),
                    np.clip(adaptability, 0, 100),
                    np.clip(tension, 0, 100),
                    np.clip(coherence, 0, 100)
                ))
        
        elif crisis_type == 'brittleness':
            # Brittleness: high stability + low adaptability
            for h in range(hours):
                progress = h / hours
                complexity = 60 + progress * 30 + np.random.normal(0, 3)
                stability = 85 - progress * 20 + np.random.normal(0, 3)
                adaptability = 35 - progress * 25 + np.random.normal(0, 3)
                tension = 40 + progress * 50 + np.random.normal(0, 3)
                coherence = 60 - progress * 30 + np.random.normal(0, 3)
                
                pattern.append((
                    np.clip(complexity, 0, 100),
                    np.clip(stability, 0, 100),
                    np.clip(adaptability, 0, 100),
                    np.clip(tension, 0, 100),
                    np.clip(coherence, 0, 100)
                ))
        
        return pattern
    
    def compute_stage_from_nsdt(self, nsdt: Tuple) -> int:
        """Compute SAP stage from NSDT vector."""
        c, s, a, t, co = nsdt
        stage = min(9, max(0, int(t / 11.11)))
        return stage
    
    def find_min_stage_and_lead_time(self, pattern: List[Tuple]) -> Tuple[int, int]:
        """Find minimum stage and lead time (hours before min stage)."""
        stages = [self.compute_stage_from_nsdt(nsdt) for nsdt in pattern]
        min_stage = min(stages)
        min_stage_idx = stages.index(min_stage)
        lead_time = len(pattern) - min_stage_idx - 1
        return min_stage, lead_time
    
    def generate_ba_dataset(self, ba_code: str, ba_name: str, region: str, 
                           volatility: str, event_type: str = 'cascade') -> Path:
        """Generate dataset for a single Balancing Authority."""
        logger.info(f"Generating dataset for {ba_code} ({ba_name})...")
        
        # Choose pattern based on volatility
        if volatility == 'high_volatility' and np.random.random() > 0.5:
            pattern = self.generate_crisis_pattern(24, event_type)
        else:
            pattern = self.generate_normal_pattern(24)
        
        # Compute metadata
        min_stage, lead_time = self.find_min_stage_and_lead_time(pattern)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"ba_{ba_code.lower()}_{timestamp}.csv"
        filepath = self.output_dir / filename
        
        # Write CSV
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'complexity', 'stability', 'adaptability', 
                'tension', 'coherence', 'event_min_stage', 'lead_time_hours',
                'ba_code', 'ba_name', 'region', 'volatility', 'event_type'
            ])
            
            base_time = datetime(2026, 4, 28, 0, 0, 0)
            for h, (c, s, a, t, co) in enumerate(pattern):
                timestamp = base_time + timedelta(hours=h)
                writer.writerow([
                    timestamp.strftime('%Y-%m-%d %H:%M'),
                    f"{c:.2f}",
                    f"{s:.2f}",
                    f"{a:.2f}",
                    f"{t:.2f}",
                    f"{co:.2f}",
                    min_stage,
                    lead_time,
                    ba_code,
                    ba_name,
                    region,
                    volatility,
                    event_type
                ])
        
        logger.info(f"  Generated: {filepath}")
        logger.info(f"    Min stage: {min_stage}, Lead time: {lead_time}h")
        
        return filepath
    
    def generate_all_ba_datasets(self) -> List[Path]:
        """Generate datasets for all 27 Balancing Authorities."""
        logger.info(f"Generating datasets for {len(BALANCING_AUTHORITIES)} Balancing Authorities...")
        
        filepaths = []
        event_types = ['cascade', 'oscillation', 'brittleness']
        
        for idx, (ba_code, ba_name, region, volatility) in enumerate(BALANCING_AUTHORITIES):
            # Vary event types across BAs
            event_type = event_types[idx % len(event_types)]
            
            try:
                filepath = self.generate_ba_dataset(ba_code, ba_name, region, volatility, event_type)
                filepaths.append(filepath)
            except Exception as e:
                logger.error(f"Error generating dataset for {ba_code}: {e}")
        
        logger.info(f"\n✅ Generated {len(filepaths)} BA datasets")
        return filepaths
    
    def generate_summary_manifest(self, filepaths: List[Path]) -> Path:
        """Generate manifest of all generated datasets."""
        manifest_path = self.output_dir / 'ba_manifest.csv'
        
        with open(manifest_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ba_code', 'filename', 'filepath', 'region', 'volatility'])
            
            for filepath in filepaths:
                # Extract BA code from filename
                filename = filepath.name
                ba_code = filename.split('_')[1].upper()
                
                # Find matching BA info
                for code, name, region, volatility in BALANCING_AUTHORITIES:
                    if code == ba_code:
                        writer.writerow([ba_code, filename, str(filepath), region, volatility])
                        break
        
        logger.info(f"Generated manifest: {manifest_path}")
        return manifest_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate synthetic NSDT datasets for 27 US Balancing Authorities'
    )
    
    parser.add_argument('--output', type=Path, default=Path('./data/validation'),
                       help='Output directory for generated CSVs')
    parser.add_argument('--count', type=int, default=27,
                       help='Number of BAs to generate (default: 27)')
    
    args = parser.parse_args()
    
    generator = NSBTDatasetGenerator(args.output)
    
    try:
        # Generate all BA datasets
        filepaths = generator.generate_all_ba_datasets()
        
        # Generate manifest
        generator.generate_summary_manifest(filepaths)
        
        logger.info("\n" + "="*60)
        logger.info("✅ Dataset generation complete!")
        logger.info(f"Output directory: {args.output}")
        logger.info(f"Total datasets: {len(filepaths)}")
        logger.info("\nNext steps:")
        logger.info("  1. Run batch processing:")
        logger.info(f"     python run_validation_batch.py --folder {args.output} --output ./results")
        logger.info("  2. Analyze results:")
        logger.info("     python validation_analysis.py --regression ./results --baseline ./baseline")
        logger.info("="*60)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
