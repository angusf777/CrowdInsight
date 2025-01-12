"""Analyze Kickstarter project data for backer funding patterns and top funded campaigns."""

import json
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default paths and constants
INPUT_FILE = "Data/website_database.json"
END_DATE = datetime(2024, 12, 12).timestamp()
TIME_PERIODS = {
    '7d': 7,
    '30d': 30,
    '90d': 90,
    '180d': 180,
    '1y': 365,
    '2y': 730,
    'N/A': None
}

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Analyze Kickstarter project data.')
    parser.add_argument('--timeframe', type=str, choices=list(TIME_PERIODS.keys()), 
                      default='30d', help='Timeframe for analysis (default: 30d)')
    parser.add_argument('--category', type=str, help='Category to analyze (optional)')
    return parser.parse_args()

def format_date(timestamp: float) -> str:
    """Format timestamp as dd/mm/yyyy."""
    return datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y')

def analyze_backer_funding(projects: List[Dict]) -> Tuple[List[str], List[float]]:
    """Calculate average funding per backer for each category."""
    funding_data: Dict[str, Dict[str, float]] = {}
    
    for p in projects:
        cat = p['category'].title()
        backers = p['backers_count']
        if backers > 0:  # Only consider projects with backers
            if cat not in funding_data:
                funding_data[cat] = {'total_funds': 0, 'total_backers': 0}
            funding_data[cat]['total_funds'] += p['pledged_usd']
            funding_data[cat]['total_backers'] += backers
    
    # Calculate averages and sort by funding per backer
    averages = [(cat, data['total_funds'] / data['total_backers']) 
                for cat, data in funding_data.items()]
    averages.sort(key=lambda x: x[1], reverse=True)
    
    # Split into separate lists
    categories, funding = zip(*averages) if averages else ([], [])
    return list(categories), list(funding)

def find_top_funded_projects(projects: List[Dict], category: Optional[str] = None, top_n: int = 5) -> List[Dict]:
    """Find the top funded projects overall or within a specific category."""
    if category:
        projects = [p for p in projects if p['category'].lower() == category.lower()]
    
    # Track unique project IDs to avoid duplicates
    seen_ids = set()
    unique_projects = []
    
    # Sort projects by pledged amount in descending order
    sorted_projects = sorted(projects, key=lambda x: float(x['pledged_usd']), reverse=True)
    
    # Get top N unique projects
    for project in sorted_projects:
        if project['id'] not in seen_ids:
            seen_ids.add(project['id'])
            unique_projects.append(project)
            if len(unique_projects) == top_n:
                break
    
    return unique_projects

def display_backer_metrics(categories: List[str], averages: List[float]):
    """Display average funding per backer for each category."""
    print("\nAverage Funding per Backer by Category:")
    for cat, avg in zip(categories, averages):
        print(f"{cat}: ${avg:.2f}")

def display_top_projects(projects: List[Dict]) -> None:
    """Display details of top funded projects."""
    print("\nTop 5 Funded Projects:")
    print("-" * 23)
    for i, project in enumerate(projects, 1):
        pledged = float(project['pledged_usd'])
        backers = int(project['backers_count'])
        avg_pledge = pledged / backers if backers > 0 else 0
        
        print(f"{i}. {project['name']}")
        print(f"   Category: {project['category']}")
        print(f"   Total Pledged: ${pledged:,.2f}")
        print(f"   Backers: {backers:,}")
        print(f"   Average Pledge: ${avg_pledge:.2f}")
        print(f"   URL: {project['url']}")
        print()

def analyze_projects(args: argparse.Namespace):
    """Analyze projects based on command line arguments."""
    try:
        # Load project data
        with open(INPUT_FILE, 'r') as f:
            projects = json.load(f)
        
        # Filter projects by timeframe
        if args.timeframe != 'N/A':
            days = TIME_PERIODS[args.timeframe]
            start_time = END_DATE - (days * 24 * 60 * 60)
            projects = [p for p in projects if start_time <= p['cal_deadline'] <= END_DATE]
        
        # Filter by category if specified
        if args.category:
            category_projects = [p for p in projects if p['category'].lower() == args.category.lower()]
            if not category_projects:
                logger.error(f"No projects found for category: {args.category}")
                return
            projects = category_projects
        
        # Calculate average funding per backer
        categories, averages = analyze_backer_funding(projects)
        display_backer_metrics(categories, averages)
        
        # Create backer funding visualization
        from plot.backer_funding import create_backer_funding_chart
        create_backer_funding_chart(categories, averages)
        
        # Find and display top funded projects
        top_projects = find_top_funded_projects(projects, args.category)
        display_top_projects(top_projects)
        
    except Exception as e:
        logger.error(f"Error analyzing projects: {e}")
        raise

if __name__ == "__main__":
    try:
        args = parse_arguments()
        analyze_projects(args)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise 