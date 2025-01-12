"""
Analyze Kickstarter project data for different time periods.

This module performs temporal analysis of Kickstarter projects,
calculating key metrics for specified time periods and their changes.
"""

import json
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Tuple, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_INPUT_FILE = Path("Data/website_database.json")

# Fixed end date (12/12/2024)
END_DATE = datetime(2024, 12, 12).timestamp()

# Time periods in days
TIME_PERIODS = {
    'N/A': None,  # For full database analysis
    '7d': 7,
    '30d': 30,
    '90d': 90,
    '180d': 180,
    '1y': 365,
    '2y': 730
}

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Analyze Kickstarter project data.')
    parser.add_argument('--input', type=Path, default=DEFAULT_INPUT_FILE,
                      help='Path to input JSON file')
    parser.add_argument('--category', type=str, default='N/A',
                      help='Category to analyze (default: N/A for all categories)')
    parser.add_argument('--timeframe', type=str, choices=list(TIME_PERIODS.keys()), default='30d',
                      help='Time period to analyze (default: 30d, use N/A for full database)')
    return parser.parse_args()

def calculate_metrics(projects: List[Dict[str, Any]], start_time: int = None, end_time: int = None, category: str = 'N/A') -> Dict[str, Any]:
    """
    Calculate metrics for a specific time period.
    
    Args:
        projects: List of project data
        start_time: Start timestamp (optional)
        end_time: End timestamp (optional)
        category: Category to filter by (N/A for all categories)
        
    Returns:
        Dict containing calculated metrics
    """
    # Filter by category first
    category_filtered = [p for p in projects if category == 'N/A' or p['category'] == category]
    
    # If timeframe is specified, filter by deadline
    if start_time is not None and end_time is not None:
        filtered_projects = [
            p for p in category_filtered
            if start_time <= p['cal_deadline'] <= end_time
        ]
    else:
        filtered_projects = category_filtered
        # Find the actual date range in the data
        if filtered_projects:
            try:
                earliest_launch = min(p['cal_launched_at'] for p in filtered_projects)
                latest_deadline = max(p['cal_deadline'] for p in filtered_projects)
                logger.info(f"Earliest launch timestamp: {earliest_launch}")
                logger.info(f"Latest deadline timestamp: {latest_deadline}")
                
                # Verify timestamps are valid
                if earliest_launch > 0:  # Avoid Unix epoch
                    start_time = earliest_launch
                else:
                    logger.warning("Invalid earliest launch date, using first valid timestamp")
                    start_time = min(p['cal_launched_at'] for p in filtered_projects if p['cal_launched_at'] > 0)
                
                end_time = latest_deadline
            except Exception as e:
                logger.error(f"Error calculating date range: {e}")
                raise
    
    total_projects = len(filtered_projects)
    total_funds = sum(p['pledged_usd'] for p in filtered_projects)
    successful_projects = sum(1 for p in filtered_projects if p['state'] == 'successful')
    success_rate = (successful_projects / total_projects * 100) if total_projects > 0 else 0
    
    start_date = datetime.fromtimestamp(start_time).strftime('%d/%m/%Y')
    end_date = datetime.fromtimestamp(end_time).strftime('%d/%m/%Y')
    
    return {
        'period': f"{start_date} - {end_date}",
        'total_projects': total_projects,
        'total_funds': total_funds,
        'successful_projects': successful_projects,
        'success_rate': success_rate
    }

def calculate_percentage_change(recent: float, previous: float) -> float:
    """Calculate percentage change between two values."""
    if previous == 0:
        return float('inf') if recent > 0 else 0
    return ((recent - previous) / previous) * 100

def analyze_projects(input_file: Path, category: str = 'N/A', timeframe: str = '30d') -> None:
    """
    Analyze projects and display metrics for recent and previous periods.
    
    Args:
        input_file: Path to input JSON file
        category: Category to analyze (N/A for all categories)
        timeframe: Time period to analyze (N/A for full database)
    """
    try:
        # Load project data
        with open(input_file, 'r') as f:
            projects = json.load(f)
        
        if timeframe == 'N/A':
            # Analyze full database
            metrics = calculate_metrics(projects, category=category)
            
            # Display results
            print(f"\nAnalysis for {category if category != 'N/A' else 'All Categories'}")
            print("Full database analysis")
            print(f"\nFull Period:", metrics['period'])
            print(f"Total Projects: {metrics['total_projects']:,}")
            print(f"Total Funds Raised: ${metrics['total_funds']:,.2f}")
            print(f"Successful Projects: {metrics['successful_projects']:,}")
            print(f"Success Rate: {metrics['success_rate']:.1f}%")
        else:
            # Calculate time ranges based on fixed end date
            period_days = TIME_PERIODS[timeframe]
            recent_start = END_DATE - (period_days * 24 * 3600)
            previous_start = recent_start - (period_days * 24 * 3600)
            
            # Calculate metrics for both periods
            recent_metrics = calculate_metrics(projects, recent_start, END_DATE, category)
            previous_metrics = calculate_metrics(projects, previous_start, recent_start, category)
            
            # Calculate percentage changes
            changes = {
                'total_projects': calculate_percentage_change(
                    recent_metrics['total_projects'],
                    previous_metrics['total_projects']
                ),
                'total_funds': calculate_percentage_change(
                    recent_metrics['total_funds'],
                    previous_metrics['total_funds']
                ),
                'successful_projects': calculate_percentage_change(
                    recent_metrics['successful_projects'],
                    previous_metrics['successful_projects']
                ),
                'success_rate': calculate_percentage_change(
                    recent_metrics['success_rate'],
                    previous_metrics['success_rate']
                )
            }
            
            # Display results
            print(f"\nAnalysis for {category if category != 'N/A' else 'All Categories'}")
            print(f"Time period: {timeframe}")
            print("\nRecent Period:", recent_metrics['period'])
            print(f"Total Projects: {recent_metrics['total_projects']:,}")
            print(f"Total Funds Raised: ${recent_metrics['total_funds']:,.2f}")
            print(f"Successful Projects: {recent_metrics['successful_projects']:,}")
            print(f"Success Rate: {recent_metrics['success_rate']:.1f}%")
            
            print("\nPrevious Period:", previous_metrics['period'])
            print(f"Total Projects: {previous_metrics['total_projects']:,}")
            print(f"Total Funds Raised: ${previous_metrics['total_funds']:,.2f}")
            print(f"Successful Projects: {previous_metrics['successful_projects']:,}")
            print(f"Success Rate: {previous_metrics['success_rate']:.1f}%")
            
            print("\nPercentage Changes:")
            print(f"Total Projects: {changes['total_projects']:+.1f}%")
            print(f"Total Funds Raised: {changes['total_funds']:+.1f}%")
            print(f"Successful Projects: {changes['successful_projects']:+.1f}%")
            print(f"Success Rate: {changes['success_rate']:+.1f}%")
        
    except Exception as e:
        logger.error(f"Error analyzing projects: {e}")

if __name__ == "__main__":
    args = parse_arguments()
    analyze_projects(args.input, args.category, args.timeframe) 