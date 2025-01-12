"""
Generate a web-friendly database from Kickstarter project data.

This module processes Kickstarter project data and creates a cleaned,
web-friendly database with relevant project information and statistics.
"""

import json
import logging
import argparse
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default file paths
DEFAULT_INPUT_FILE = Path("/Users/Angusf777/Desktop/FYP OFFICIAL/Data/Kickstarter_2024-12-12T03_20_04_455Z.json")
DEFAULT_OUTPUT_FILE = Path("/Users/Angusf777/Desktop/FYP OFFICIAL/Data/website_database.json")
DEFAULT_STATS_FILE = Path("/Users/Angusf777/Desktop/FYP OFFICIAL/Data/web_processing_stats.json")

# States to exclude from processing
EXCLUDED_STATES = {'submitted', 'live', 'started'}

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate web-friendly database from Kickstarter data.')
    parser.add_argument('--input', type=Path, default=DEFAULT_INPUT_FILE,
                      help='Path to input JSON file')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT_FILE,
                      help='Path to output web database JSON file')
    parser.add_argument('--stats', type=Path, default=DEFAULT_STATS_FILE,
                      help='Path to output statistics JSON file')
    return parser.parse_args()

class ProjectFormatter:
    """Handles the formatting and processing of individual project records."""
    
    @staticmethod
    def format_date(timestamp: int) -> str:
        """
        Convert Unix timestamp to dd/mm/yyyy format.
        
        Args:
            timestamp: Unix timestamp to convert
            
        Returns:
            str: Formatted date string
        """
        try:
            return datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y')
        except (TypeError, ValueError) as e:
            logger.warning(f"Error formatting date from timestamp {timestamp}: {e}")
            return ""

    @staticmethod
    def calculate_duration(launched: int, deadline: int) -> int:
        """
        Calculate campaign duration in days.
        
        Args:
            launched: Campaign launch timestamp
            deadline: Campaign deadline timestamp
            
        Returns:
            int: Duration in days
        """
        try:
            return (datetime.fromtimestamp(deadline) - datetime.fromtimestamp(launched)).days
        except (TypeError, ValueError) as e:
            logger.warning(f"Error calculating duration: {e}")
            return 0

    @staticmethod
    def process_project(data: Dict[str, Any], stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single project record.
        
        Args:
            data: Raw project data dictionary
            stats: Statistics dictionary to update
            
        Returns:
            Dict[str, Any]: Processed project data
        """
        try:
            # Check if project state is in excluded states
            state = data.get("state", "").lower()
            stats['by_state'][state] = stats['by_state'].get(state, 0) + 1
            
            if state in EXCLUDED_STATES:
                stats['excluded_by_state'][state] = stats['excluded_by_state'].get(state, 0) + 1
                return {}
                
            # Calculate USD values using static_usd_rate
            usd_rate = data.get("static_usd_rate", 1)
            goal_usd = data.get("goal", 0) * usd_rate
            pledged_usd = data.get("pledged", 0) * usd_rate
            backers_count = data.get("backers_count", 0)
            
            # Calculate pledge per backer
            pledge_per_backer = round(pledged_usd / backers_count, 2) if backers_count else 0
            
            # Get category information
            category = data.get("category", {})
            category_slug = category.get("slug", "")
            parent_category = category_slug.split('/')[0] if category_slug else "unknown"
            
            # Get location information
            location = data.get("location", {})
            
            # Update category stats
            stats['by_category'][parent_category] = stats['by_category'].get(parent_category, 0) + 1
            
            return {
                "id": data.get("id"),
                "state": state,
                "name": data.get("name"),
                "blurb": data.get("blurb"),
                "category": parent_category,
                "subcategory": category_slug,
                "country": location.get("expanded_country"),
                "location": location.get("name"),
                "goal_usd": goal_usd,
                "pledged_usd": pledged_usd,
                "backers_count": backers_count,
                "currency": data.get("currency"),
                "cal_launched_at": data.get("launched_at"),
                "cal_deadline": data.get("deadline"),
                "launched_at": ProjectFormatter.format_date(data.get("launched_at")),
                "deadline": ProjectFormatter.format_date(data.get("deadline")),
                "campaign_duration": ProjectFormatter.calculate_duration(
                    data.get("launched_at", 0), 
                    data.get("deadline", 0)
                ),
                "percent_funded": data.get("percent_funded", 0),
                "pledge_per_backer": pledge_per_backer,
                "is_staff_pick": data.get("staff_pick", False),
                "links": {
                    "project": data.get("urls", {}).get("web", {}).get("project"),
                    "creator": data.get("creator", {}).get("urls", {}).get("web", {}).get("user")
                }
            }
        except Exception as e:
            logger.error(f"Error processing project: {e}")
            stats['errors']['processing'] = stats['errors'].get('processing', 0) + 1
            return {}

def process_database(input_file: Path, output_file: Path, stats_file: Path) -> None:
    """
    Main function to process Kickstarter data and create web database.
    Reads from input file, processes projects, and saves to output file.
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to output web database JSON file
        stats_file: Path to output statistics JSON file
    """
    processed_records: List[Dict[str, Any]] = []
    stats = {
        'summary': {'total_processed': 0, 'included': 0, 'excluded': 0},
        'by_state': defaultdict(int),
        'excluded_by_state': defaultdict(int),
        'by_category': defaultdict(int),
        'errors': defaultdict(int)
    }
    
    logger.info("Starting to process Kickstarter data...")
    
    try:
        with open(input_file, "r") as file:
            for line in file:
                stats['summary']['total_processed'] += 1
                try:
                    record = json.loads(line.strip())
                    project_data = ProjectFormatter.process_project(record.get("data", {}), stats)
                    
                    if project_data:
                        processed_records.append(project_data)
                        stats['summary']['included'] += 1
                        
                        if stats['summary']['included'] % 1000 == 0:
                            logger.info(f"Processed {stats['summary']['included']} records successfully...")
                    else:
                        stats['summary']['excluded'] += 1
                            
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding JSON at line {stats['summary']['total_processed']}: {e}")
                    stats['errors']['json_decode'] = stats['errors'].get('json_decode', 0) + 1
                except Exception as e:
                    logger.error(f"Unexpected error processing line {stats['summary']['total_processed']}: {e}")
                    stats['errors']['unexpected'] = stats['errors'].get('unexpected', 0) + 1
        
        # Convert defaultdict to regular dict for JSON serialization
        stats = {k: dict(v) if isinstance(v, defaultdict) else v for k, v in stats.items()}
        
        # Save the processed records
        with open(output_file, "w") as outfile:
            json.dump(processed_records, outfile, indent=2)
            
        # Save statistics
        with open(stats_file, "w") as statsfile:
            json.dump(stats, statsfile, indent=2)
        
        # Log completion statistics
        logger.info("\nProcessing completed!")
        logger.info(f"Total records processed: {stats['summary']['total_processed']}")
        logger.info(f"Successfully included records: {stats['summary']['included']}")
        logger.info(f"Excluded records: {stats['summary']['excluded']}")
        logger.info("\nExcluded by state:")
        for state, count in stats['excluded_by_state'].items():
            logger.info(f"  {state}: {count}")
        logger.info("\nTotal by state:")
        for state, count in stats['by_state'].items():
            logger.info(f"  {state}: {count}")
        logger.info("\nBy category:")
        for category, count in stats['by_category'].items():
            logger.info(f"  {category}: {count}")
        if stats['errors']:
            logger.info("\nErrors encountered:")
            for error_type, count in stats['errors'].items():
                logger.info(f"  {error_type}: {count}")
        logger.info(f"\nProcessed data saved to: {output_file}")
        logger.info(f"Statistics saved to: {stats_file}")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    args = parse_arguments()
    process_database(args.input, args.output, args.stats)
