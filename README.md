# CrowdInsight

A data analysis project focused on Kickstarter campaigns, providing insights into crowdfunding success factors and trends.

## Project Structure

- `Data/`: Contains processed Kickstarter data files
- `Tools/`: Python scripts for data processing and analysis
  - `filter_kickstarter.py`: Filters and processes raw Kickstarter data
  - `make_WebDatabase.py`: Generates web-friendly database from processed data
  - `row1+2_analysis.py`: Performs temporal and categorical analysis of Kickstarter projects

## Setup

1. Clone the repository:
```bash
git clone https://github.com/angusf777/CrowdInsight.git
cd CrowdInsight
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the setup notebook:
```bash
jupyter notebook setup.ipynb
```

## Data Processing Pipeline

1. The setup notebook downloads and extracts the latest Kickstarter dataset
2. `filter_kickstarter.py` processes and filters the raw data
3. `make_WebDatabase.py` creates a web-friendly database for analysis

## Analysis Tools

### Temporal and Categorical Analysis (row1+2_analysis.py)

Analyze Kickstarter projects over different time periods with detailed category/subcategory breakdowns. The script provides comprehensive metrics including total projects, funds raised, success rates, and their changes over time.

Usage:
```bash
# Default analysis (30-day period, all categories, sorted by number of projects)
python Tools/row1+2_analysis.py

# Analyze specific time periods (7d, 30d, 90d, 180d, 1y, 2y, or N/A for full database)
python Tools/row1+2_analysis.py --timeframe 180d

# Analyze specific category with subcategory breakdown
python Tools/row1+2_analysis.py --timeframe 90d --category technology

# Sort by funds raised instead of project count
python Tools/row1+2_analysis.py --sort funds

# Analyze entire database
python Tools/row1+2_analysis.py --timeframe N/A
```

Options:
- `--timeframe`: Time period to analyze (default: 30d)
  - Available periods: 7d, 30d, 90d, 180d, 1y, 2y, N/A (full database)
- `--category`: Category to analyze (default: N/A for all categories)
- `--sort`: Sort categories/subcategories by 'projects' or 'funds' (default: projects)
- `--input`: Custom input file path (default: Data/website_database.json)

Output includes:
1. Period Overview:
   - Total number of projects
   - Total funds raised
   - Number of successful projects
   - Success rate
   - Percentage changes between periods (except for full database analysis)

2. Category/Subcategory Analysis:
   - Top 5 categories (or subcategories if category specified)
   - For each category/subcategory:
     - Number of projects
     - Funds raised (in millions)
     - Success rate
     - Growth percentage compared to previous period

### Backer Analysis (backer_analysis.py)

Analyze backer funding patterns and identify top funded campaigns. This tool provides insights into average funding per backer across categories and highlights the most successful projects.

Usage:
```bash
# Default analysis (30-day period, all categories)
python Tools/backer_analysis.py

# Analyze specific time periods
python Tools/backer_analysis.py --timeframe 90d

# Analyze specific category
python Tools/backer_analysis.py --timeframe 30d --category games
```

Options:
- `--timeframe`: Time period to analyze (default: 30d)
  - Available periods: 7d, 30d, 90d, 180d, 1y, 2y, N/A (full database)
- `--category`: Category to analyze (optional)

Output includes:
1. Average Funding per Backer:
   - Breakdown by category
   - Sorted by average pledge amount

2. Top 5 Funded Projects:
   - Project name and category
   - Total amount pledged
   - Number of backers
   - Average pledge per backer
   - Project URL

## License

MIT License 