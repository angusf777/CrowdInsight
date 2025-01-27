"""
Analyze unique subcategories and countries in the filtered Kickstarter dataset.

This script reads the filtered Kickstarter data and provides statistics about
the distribution of projects across different categories and countries.
"""

import json
import logging
from pathlib import Path
from collections import defaultdict
from typing import Dict, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CategoryAnalyzer:
    """Analyzes categories and countries in Kickstarter projects."""
    
    def __init__(self):
        self.categories: Dict[str, int] = defaultdict(int)  # category -> count
        self.countries: Set[str] = set()
        self.country_counts: Dict[str, int] = defaultdict(int)
        self.total_projects = 0
    
    def process_project(self, project: Dict) -> None:
        """Process a single project and update statistics."""
        try:
            data = project.get('data', {})
            
            # Get category information
            category = data.get('category', {})
            category_name = category.get('name', 'Unknown')
            
            # Get country information
            country = data.get('country', 'Unknown')
            
            # Update statistics
            self.categories[category_name] += 1
            self.countries.add(country)
            self.country_counts[country] += 1
            self.total_projects += 1
            
        except Exception as e:
            logger.error(f"Error processing project: {e}")
    
    def print_statistics(self) -> None:
        """Print detailed statistics about categories and countries."""
        print("\nKickstarter Project Analysis")
        print("=" * 50)
        print(f"\nTotal Projects Analyzed: {self.total_projects:,}")
        
        # Print category statistics
        print("\nCategory Statistics:")
        print("-" * 30)
        print(f"Total Categories: {len(self.categories)}")
        print("\nCategories by Project Count:")
        sorted_categories = sorted(self.categories.items(), key=lambda x: x[1], reverse=True)
        for category, count in sorted_categories:
            percentage = (count / self.total_projects) * 100
            print(f"  {category}: {count:,} projects ({percentage:.1f}%)")
        
        # Print country statistics
        print("\nCountry Statistics:")
        print("-" * 30)
        print(f"Total Countries: {len(self.countries)}")
        print("\nTop 10 Countries by Project Count:")
        top_countries = sorted(self.country_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for country, count in top_countries:
            percentage = (count / self.total_projects) * 100
            print(f"  {country}: {count:,} projects ({percentage:.1f}%)")

def analyze_kickstarter_data(input_file: Path) -> None:
    """
    Analyze the Kickstarter data for categories and countries.
    
    Args:
        input_file: Path to the filtered Kickstarter JSON file
    """
    analyzer = CategoryAnalyzer()
    
    try:
        logger.info(f"Reading data from {input_file}")
        with open(input_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    project = json.loads(line.strip())
                    analyzer.process_project(project)
                    
                    if line_num % 10000 == 0:
                        logger.info(f"Processed {line_num:,} projects...")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding JSON at line {line_num}: {e}")
                    continue
        
        # Print final statistics
        analyzer.print_statistics()
        logger.info("Analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error analyzing data: {e}")
        raise

if __name__ == "__main__":
    input_file = Path("Data/Kickstarter_filtered.json")
    
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
    else:
        analyze_kickstarter_data(input_file) 