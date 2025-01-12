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
from collections import defaultdict
from operator import itemgetter
from plot.trending_cat import create_growth_plot
from plot.funding_chart import create_funding_chart
from plot.country_chart import create_country_chart

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
    parser.add_argument('--sort', type=str, choices=['projects', 'funds'], default='projects',
                      help='Sort categories/subcategories by number of projects or funds raised (default: projects)')
    parser.add_argument('--no-growth-sort', action='store_true',
                      help='Sort by absolute numbers instead of growth rate (default: False)')
    return parser.parse_args()

def get_category_metrics(projects: List[Dict[str, Any]], start_time: int, end_time: int, is_subcategory: bool = False) -> List[Dict[str, Any]]:
    """Calculate metrics for each category or subcategory."""
    metrics_by_cat = defaultdict(lambda: {
        'total_projects': 0,
        'total_funds': 0,
        'successful_projects': 0
    })
    
    for p in projects:
        if start_time <= p['cal_deadline'] <= end_time:
            cat = p['subcategory'] if is_subcategory else p['category']
            metrics_by_cat[cat]['total_projects'] += 1
            metrics_by_cat[cat]['total_funds'] += p['pledged_usd']
            if p['state'] == 'successful':
                metrics_by_cat[cat]['successful_projects'] += 1
    
    return [{'category': k, **v} for k, v in metrics_by_cat.items()]

def get_funding_ranges():
    """Define funding goal ranges."""
    return [
        (0, 1000, '<$1k'),
        (1000, 10000, '$1k-$10k'),
        (10000, 100000, '$10k-$100k'),
        (100000, 1000000, '$100k-$1m'),
        (1000000, float('inf'), '>$1m')
    ]

def analyze_funding_distribution(projects):
    """Analyze the distribution of projects across funding goal ranges."""
    ranges = get_funding_ranges()
    distribution = {label: 0 for _, _, label in ranges}
    
    for project in projects:
        goal = project['goal_usd']
        for min_val, max_val, label in ranges:
            if min_val <= goal < max_val:
                distribution[label] += 1
                break
    
    return distribution

def display_funding_distribution(filtered_projects):
    """Pass funding goal distribution data to visualization module."""
    distribution = analyze_funding_distribution(filtered_projects)
    create_funding_chart(distribution)

def analyze_country_distribution(projects):
    """Analyze the distribution of projects across countries."""
    country_counts = {}
    for p in projects:
        country = p.get('country', 'Unknown')
        country_counts[country] = country_counts.get(country, 0) + 1
    
    # Sort by count and get top 6
    sorted_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:6]
    return dict(sorted_countries)

def display_country_distribution(filtered_projects):
    """Pass country distribution data to visualization module."""
    distribution = analyze_country_distribution(filtered_projects)
    create_country_chart(distribution)

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
    
    # Calculate category/subcategory metrics if time period is specified
    category_breakdown = None
    if start_time is not None and end_time is not None:
        is_subcategory = category != 'N/A'
        category_breakdown = get_category_metrics(category_filtered, start_time, end_time, is_subcategory)
    
    # Get funding distribution
    funding_dist = analyze_funding_distribution(filtered_projects)
    create_funding_chart(funding_dist)
    
    # Get country distribution
    country_dist = analyze_country_distribution(filtered_projects)
    create_country_chart(country_dist)
    
    return {
        'period': f"{start_date} - {end_date}",
        'total_projects': total_projects,
        'total_funds': total_funds,
        'successful_projects': successful_projects,
        'success_rate': success_rate,
        'category_breakdown': category_breakdown,
        'filtered_projects': filtered_projects  # Add filtered projects to return value
    }

def calculate_percentage_change(current: float, previous: float) -> float:
    """Calculate percentage change between two values."""
    if previous == 0:
        return 100.0 if current > 0 else 0.0  # Cap at 100% growth for new categories
    return ((current - previous) / previous) * 100

def format_growth(value: float) -> str:
    """Format growth percentage for display."""
    if value == float('inf'):
        return '+∞%'
    elif value == float('-inf'):
        return '-∞%'
    elif value > 0:
        return f'+{value:.1f}%'
    else:
        return f'{value:.1f}%'

def display_category_breakdown(recent_breakdown: List[Dict[str, Any]], previous_breakdown: List[Dict[str, Any]], 
                            sort_by: str, is_subcategory: bool = False, sort_by_growth: bool = True):
    """Display top 5 categories/subcategories with their metrics and growth."""
    # Create lookup for previous period metrics
    prev_lookup = {item['category']: item for item in previous_breakdown}
    
    # Calculate growth rates and create combined metrics
    combined_metrics = []
    for cat in recent_breakdown:
        name = cat['category']
        prev = prev_lookup.get(name, {'total_projects': 0, 'total_funds': 0, 'successful_projects': 0})
        sort_key = 'total_funds' if sort_by == 'funds' else 'total_projects'
        
        # Calculate growth rate
        growth = calculate_percentage_change(cat[sort_key], prev[sort_key])
        
        combined_metrics.append({
            **cat,
            'growth': growth,
            'success_rate': (cat['successful_projects'] / cat['total_projects'] * 100) if cat['total_projects'] > 0 else 0
        })
    
    # Sort based on growth or absolute numbers
    if sort_by_growth:
        sorted_cats = sorted(combined_metrics, key=lambda x: x['growth'], reverse=True)[:5]
    else:
        sort_key = 'total_funds' if sort_by == 'funds' else 'total_projects'
        sorted_cats = sorted(combined_metrics, key=lambda x: x[sort_key], reverse=True)[:5]
    
    cat_type = "Subcategories" if is_subcategory else "Categories"
    metric_type = "funds" if sort_by == "funds" else "projects"
    sort_type = "growth" if sort_by_growth else "number"
    print(f"\nTop 5 {cat_type} by {metric_type} {sort_type}:")
    print(f"{'Name':<20} {'Projects':<10} {'Funds ($M)':<12} {'Success Rate':<12} {'Growth %':<10}")
    print("-" * 65)
    
    for cat in sorted_cats:
        print(f"{cat['category'][:19]:<20} {cat['total_projects']:<10} {cat['total_funds']/1e6:,.1f}{'M':<8} "
              f"{cat['success_rate']:,.1f}%{'':>6} {format_growth(cat['growth']):<10}")
    
    # Create visualization of category growth
    sorted_cat_tuples = [(cat['category'], cat) for cat in sorted_cats]
    create_growth_plot(sorted_cat_tuples, sort_by)

def analyze_projects(input_file: Path, category: str = 'N/A', timeframe: str = '30d', sort_by: str = 'projects', sort_by_growth: bool = True) -> None:
    """
    Analyze projects and display metrics for recent and previous periods.
    
    Args:
        input_file: Path to input JSON file
        category: Category to analyze (N/A for all categories)
        timeframe: Time period to analyze (N/A for full database)
        sort_by: Sort categories by 'projects' or 'funds'
        sort_by_growth: Sort by growth rate instead of absolute numbers
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
            
            # Display funding distribution
            display_funding_distribution(metrics['filtered_projects'])
            
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
            
            # Display funding distribution for recent period
            display_funding_distribution(recent_metrics['filtered_projects'])
            
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
            
            # Display category/subcategory breakdown
            if recent_metrics['category_breakdown'] and previous_metrics['category_breakdown']:
                display_category_breakdown(
                    recent_metrics['category_breakdown'],
                    previous_metrics['category_breakdown'],
                    sort_by,
                    is_subcategory=(category != 'N/A'),
                    sort_by_growth=sort_by_growth
                )
        
    except Exception as e:
        logger.error(f"Error analyzing projects: {e}")

if __name__ == "__main__":
    args = parse_arguments()
    analyze_projects(args.input, args.category, args.timeframe, args.sort, not args.no_growth_sort) 