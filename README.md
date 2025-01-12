# CrowdInsight

A data analysis project focused on Kickstarter campaigns, providing insights into crowdfunding success factors and trends.

## Project Structure

- `Data/`: Contains processed Kickstarter data files
- `Tools/`: Python scripts for data processing and analysis
  - `filter_kickstarter.py`: Filters and processes raw Kickstarter data
  - `make_WebDatabase.py`: Generates web-friendly database from processed data
  - `analysis.py`: Performs temporal analysis of Kickstarter projects

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

### Temporal Analysis (analysis.py)

Analyze Kickstarter projects over different time periods. The script provides metrics such as total projects, funds raised, success rates, and their changes over time.

Usage:
```bash
# Default analysis (30-day period, all categories)
python Tools/analysis.py

# Analyze specific time periods (7d, 30d, 90d, 180d, 1y, 2y, or N/A for full database)
python Tools/analysis.py --timeframe 180d

# Analyze specific category
python Tools/analysis.py --timeframe 90d --category technology

# Analyze entire database
python Tools/analysis.py --timeframe N/A
```

Options:
- `--timeframe`: Time period to analyze (default: 30d)
  - Available periods: 7d, 30d, 90d, 180d, 1y, 2y, N/A (full database)
- `--category`: Category to analyze (default: N/A for all categories)
- `--input`: Custom input file path (default: Data/website_database.json)

Output includes:
- Total number of projects
- Total funds raised
- Number of successful projects
- Success rate
- Percentage changes between periods (except for full database analysis)

## License

MIT License 