"""
Kickstarter Project Filter and Processor

This module processes raw Kickstarter data, filtering and transforming projects
based on their state and attributes. It implements a specialized handling approach
for canceled projects, converting them to failed status if they meet specific criteria.

Key features:
- Filters out projects with excluded states (suspended, started, live, submitted)
- Handles canceled projects by:
  - Converting to "failed" if ≤60% campaign time was remaining at cancellation
  - Excluding if >60% campaign time was remaining at cancellation
- Preserves successful and failed projects unchanged
- Generates detailed statistics on the filtering process

Usage:
    python Tools/filter_kickstarter.py [--input INPUT_FILE] [--output OUTPUT_FILE] [--stats STATS_FILE]

The script outputs both the filtered data and comprehensive statistics about the
filtering process, which are used by visualization tools to explain the methodology.

Copyright (c) 2025 Angus Fung
"""

import json
import logging
import argparse
from typing import Tuple, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_INPUT_FILE = Path("/Users/Angusf777/Desktop/FYP OFFICIAL/Data/Kickstarter_2024-12-12T03_20_04_455Z.json")
DEFAULT_OUTPUT_FILE = Path("/Users/Angusf777/Desktop/FYP OFFICIAL/Data/Kickstarter_filtered.json")
DEFAULT_STATS_FILE = Path("/Users/Angusf777/Desktop/FYP OFFICIAL/Data/filtering_stats.json")

EXCLUDED_STATES = {'suspended', 'started', 'live', 'submitted'}
CONVERSION_THRESHOLD = 60  # Percentage threshold for converting canceled to failed

def parse_arguments():
    """
    Parse command line arguments for the filter_kickstarter script.
    
    Returns:
        argparse.Namespace: Object containing the parsed command line arguments
    """
    parser = argparse.ArgumentParser(description='Filter and process Kickstarter project data.')
    parser.add_argument('--input', type=Path, default=DEFAULT_INPUT_FILE,
                      help='Path to input JSON file')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT_FILE,
                      help='Path to output filtered JSON file')
    parser.add_argument('--stats', type=Path, default=DEFAULT_STATS_FILE,
                      help='Path to output statistics JSON file')
    return parser.parse_args()

class ProjectProcessor:
    """
    Handles the processing and filtering of Kickstarter projects.
    
    This class contains methods to evaluate projects based on their state
    and determine whether they should be included in the filtered dataset.
    It provides special handling for canceled projects, calculating the
    percentage of remaining campaign time at cancellation.
    """
    
    @staticmethod
    def calculate_remaining_time_percentage(deadline: int, canceled_at: int, created_at: int) -> float:
        """
        Calculate the percentage of time remaining when a project was canceled.
        
        Args:
            deadline: Project deadline timestamp
            canceled_at: Cancellation timestamp
            created_at: Project creation timestamp
            
        Returns:
            float: Percentage of time remaining (0-100)
            
        Note:
            The calculation uses the formula:
            (time_until_deadline / total_duration) * 100
        """
        try:
            deadline_dt = datetime.fromtimestamp(deadline)
            canceled_dt = datetime.fromtimestamp(canceled_at)
            created_dt = datetime.fromtimestamp(created_at)
            
            total_duration = (deadline_dt - created_dt).total_seconds()
            time_until_deadline = (deadline_dt - canceled_dt).total_seconds()
            
            if total_duration > 0:
                return (time_until_deadline / total_duration) * 100
            return 0
            
        except Exception as e:
            logger.error(f"Error calculating time percentage: {e}")
            return 0

    @staticmethod
    def should_include_project(project: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Determine if a project should be included in the filtered dataset.
        
        The decision follows these rules:
        1. Exclude projects with states in EXCLUDED_STATES
        2. Include successful and failed projects as-is
        3. For canceled projects:
           - Convert to failed if ≤60% of campaign time remained at cancellation
           - Exclude if >60% of campaign time remained at cancellation
        
        Args:
            project: Project data dictionary
            
        Returns:
            Tuple containing:
            - bool: Whether to include the project
            - Optional[Dict]: Modified project data if included, None if excluded
            - str: Reason for the decision (for statistics)
        """
        try:
            state = project.get('data', {}).get('state', '').lower()
            
            if state in EXCLUDED_STATES:
                return False, None, state
                
            if state == 'canceled':
                project_data = project.get('data', {})
                deadline = project_data.get('deadline', 0)
                canceled_at = project_data.get('state_changed_at', 0)
                created_at = project_data.get('created_at', 0)
                
                if all([deadline, canceled_at, created_at]):
                    remaining_time = ProjectProcessor.calculate_remaining_time_percentage(
                        deadline, canceled_at, created_at
                    )
                    
                    if remaining_time <= CONVERSION_THRESHOLD:
                        project['data']['state'] = 'failed'
                        return True, project, f"canceled_converted_{remaining_time:.1f}%"
                    return False, None, f"canceled_excluded_{remaining_time:.1f}%"
                return False, None, "canceled_invalid_timestamps"
                
            if state in {'successful', 'failed'}:
                return True, project, state
                
            return False, None, f"unknown_state_{state}"
            
        except Exception as e:
            logger.error(f"Error processing project: {e}")
            return False, None, "error_processing"

def filter_projects(input_file: Path, output_file: Path, stats_file: Path) -> None:
    """
    Main function to filter and process Kickstarter projects.
    
    Reads projects from the input file, processes each one according to
    filtering rules, and saves the filtered results to the output file.
    Also collects and saves comprehensive statistics about the filtering process.
    
    Args:
        input_file: Path to input JSON file containing raw Kickstarter data
        output_file: Path to output filtered JSON file
        stats_file: Path to output statistics JSON file
    """
    stats = {
        'summary': {'total_processed': 0, 'included': 0, 'excluded': 0},
        'by_state': {},
        'canceled': {
            'total': 0,
            'converted_to_failed': 0,
            'excluded_early': 0,
            'invalid_timestamps': 0,
            'by_time_remaining': {}
        }
    }
    
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                stats['summary']['total_processed'] += 1
                
                try:
                    project = json.loads(line.strip())
                    state = project.get('data', {}).get('state', '').lower()
                    
                    stats['by_state'][state] = stats['by_state'].get(state, 0) + 1
                    
                    if state == 'canceled':
                        stats['canceled']['total'] += 1
                    
                    should_include, modified_project, reason = ProjectProcessor.should_include_project(project)
                    
                    if should_include:
                        json.dump(modified_project, outfile)
                        outfile.write('\n')
                        stats['summary']['included'] += 1
                        
                        if reason.startswith('canceled_converted'):
                            stats['canceled']['converted_to_failed'] += 1
                            time_remaining = float(reason.split('_')[2].rstrip('%'))
                            bucket = f"{time_remaining:.1f}%"
                            stats['canceled']['by_time_remaining'][bucket] = \
                                stats['canceled']['by_time_remaining'].get(bucket, 0) + 1
                    else:
                        stats['summary']['excluded'] += 1
                        if reason.startswith('canceled_excluded'):
                            stats['canceled']['excluded_early'] += 1
                            time_remaining = float(reason.split('_')[2].rstrip('%'))
                            bucket = f"{time_remaining:.1f}%"
                            stats['canceled']['by_time_remaining'][bucket] = \
                                stats['canceled']['by_time_remaining'].get(bucket, 0) + 1
                        elif reason == 'canceled_invalid_timestamps':
                            stats['canceled']['invalid_timestamps'] += 1
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding JSON: {e}")
                except Exception as e:
                    logger.error(f"Error processing line: {e}")
        
        # Sort statistics
        stats['by_state'] = dict(sorted(stats['by_state'].items()))
        stats['canceled']['by_time_remaining'] = dict(sorted(
            stats['canceled']['by_time_remaining'].items(),
            key=lambda x: float(x[0].rstrip('%'))
        ))
        
        # Save statistics
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info("\nFiltering completed!")
        logger.info(f"Total processed: {stats['summary']['total_processed']}")
        logger.info(f"Included: {stats['summary']['included']}")
        logger.info(f"Excluded: {stats['summary']['excluded']}")
        logger.info("\nCanceled projects summary:")
        logger.info(f"Total canceled: {stats['canceled']['total']}")
        logger.info(f"Converted to failed: {stats['canceled']['converted_to_failed']}")
        logger.info(f"Excluded (>60% remaining): {stats['canceled']['excluded_early']}")
        logger.info(f"Invalid timestamps: {stats['canceled']['invalid_timestamps']}")
        logger.info(f"\nDetailed statistics saved to: {stats_file}")
        
    except Exception as e:
        logger.error(f"Fatal error during filtering: {e}")

if __name__ == "__main__":
    args = parse_arguments()
    filter_projects(args.input, args.output, args.stats) 