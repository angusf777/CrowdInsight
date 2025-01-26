"""
Check for duplicate projects in the Kickstarter dataset and remove duplicates.

This module analyzes the Kickstarter data to identify and remove duplicate projects,
saving both the deduplicated dataset and statistics about the duplicates found.
"""

import json
import logging
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_INPUT_FILE = Path("/Users/Angusf777/Desktop/FYP OFFICIAL/Data/Kickstarter_2024-12-12T03_20_04_455Z.json")
DEFAULT_OUTPUT_FILE = Path("/Users/Angusf777/Desktop/FYP OFFICIAL/Data/Kickstarter_removed_duplicates.json")
DEFAULT_STATS_FILE = Path("/Users/Angusf777/Desktop/FYP OFFICIAL/Data/duplicate_stats.json")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Remove duplicate projects from Kickstarter data.')
    parser.add_argument('--input', type=Path, default=DEFAULT_INPUT_FILE,
                      help='Path to input JSON file')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT_FILE,
                      help='Path to output deduplicated JSON file')
    parser.add_argument('--stats', type=Path, default=DEFAULT_STATS_FILE,
                      help='Path to output statistics JSON file')
    return parser.parse_args()

class DuplicateProcessor:
    """Handles the processing and removal of duplicate projects in Kickstarter data."""
    
    def __init__(self):
        self.id_map: Dict[str, List[Dict]] = defaultdict(list)
        self.name_map: Dict[str, List[Dict]] = defaultdict(list)
        self.url_map: Dict[str, List[Dict]] = defaultdict(list)
        self.creator_map: Dict[str, List[Dict]] = defaultdict(list)
        self.seen_ids: Set[str] = set()
        self.duplicate_stats = {
            'total_projects': 0,
            'duplicates_removed': 0,
            'unique_projects': 0,
            'by_category': defaultdict(int),
            'by_state': defaultdict(int),
            'duplicate_groups': []
        }
    
    def process_project(self, project: Dict) -> bool:
        """
        Process a project and determine if it's a duplicate.
        Returns True if project should be kept, False if it's a duplicate.
        """
        project_id = project.get('data', {}).get('id')
        if not project_id:
            return True  # Keep projects without IDs
            
        if project_id in self.seen_ids:
            self.duplicate_stats['duplicates_removed'] += 1
            return False
            
        self.seen_ids.add(project_id)
        self._update_maps(project)
        return True
    
    def _update_maps(self, project: Dict) -> None:
        """Update tracking maps with project information."""
        data = project.get('data', {})
        project_id = data.get('id')
        project_name = data.get('name', '').lower()
        project_url = data.get('urls', {}).get('web', {}).get('project', '').lower()
        creator_id = data.get('creator', {}).get('id')
        state = data.get('state')
        
        if project_id:
            self.id_map[project_id].append(project)
        if project_name:
            self.name_map[project_name].append(project)
        if project_url:
            self.url_map[project_url].append(project)
        if creator_id:
            self.creator_map[creator_id].append(project)
        if state:
            self.duplicate_stats['by_state'][state] += 1
    
    def _extract_project_info(self, project: Dict) -> Dict:
        """Extract relevant project information for reporting."""
        data = project.get('data', {})
        return {
            'id': data.get('id'),
            'name': data.get('name'),
            'state': data.get('state'),
            'creator_id': data.get('creator', {}).get('id'),
            'url': data.get('urls', {}).get('web', {}).get('project'),
            'launched_at': data.get('launched_at'),
            'deadline': data.get('deadline')
        }
    
    def finalize_stats(self) -> Dict:
        """Finalize and return statistics about duplicates."""
        # Process duplicate groups
        for project_id, projects in self.id_map.items():
            if len(projects) > 1:
                self.duplicate_stats['duplicate_groups'].append({
                    'project_id': project_id,
                    'occurrences': len(projects),
                    'projects': [self._extract_project_info(p) for p in projects]
                })
                self.duplicate_stats['by_category']['exact_duplicates'] += 1
        
        # Calculate final statistics
        self.duplicate_stats['unique_projects'] = len(self.seen_ids)
        self.duplicate_stats['analysis_timestamp'] = datetime.now().isoformat()
        
        # Convert defaultdict to regular dict for JSON serialization
        self.duplicate_stats['by_category'] = dict(self.duplicate_stats['by_category'])
        self.duplicate_stats['by_state'] = dict(self.duplicate_stats['by_state'])
        
        return self.duplicate_stats

def remove_duplicates(input_file: Path, output_file: Path, stats_file: Path) -> None:
    """
    Main function to remove duplicates from Kickstarter data and save statistics.
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to output deduplicated JSON file
        stats_file: Path to output statistics JSON file
    """
    processor = DuplicateProcessor()
    
    try:
        logger.info("Starting duplicate removal process...")
        
        # Process input file and write deduplicated data
        with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
            for line in f_in:
                processor.duplicate_stats['total_projects'] += 1
                try:
                    project = json.loads(line.strip())
                    if processor.process_project(project):
                        f_out.write(json.dumps(project) + '\n')
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding JSON at line {processor.duplicate_stats['total_projects']}: {e}")
                except Exception as e:
                    logger.error(f"Error processing project at line {processor.duplicate_stats['total_projects']}: {e}")
        
        # Finalize and save statistics
        stats = processor.finalize_stats()
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        # Display summary
        print(f"\nDuplicate Removal Summary:")
        print("-" * 25)
        print(f"Total projects processed: {stats['total_projects']:,}")
        print(f"Duplicates removed: {stats['duplicates_removed']:,}")
        print(f"Unique projects remaining: {stats['unique_projects']:,}")
        print(f"\nDeduplicated data saved to: {output_file}")
        print(f"Statistics saved to: {stats_file}")
        
        logger.info("Duplicate removal completed!")
        
    except Exception as e:
        logger.error(f"Fatal error during processing: {e}")
        raise

if __name__ == "__main__":
    args = parse_arguments()
    remove_duplicates(args.input, args.output, args.stats) 