# CrowdInsight

A data analysis project focused on Kickstarter campaigns, providing insights into crowdfunding success factors and trends.

## Project Structure

- `Data/`: Contains processed Kickstarter data files
- `Tools/`: Python scripts for data processing and analysis
  - `filter_kickstarter.py`: Filters and processes raw Kickstarter data
  - `make_WebDatabase.py`: Generates web-friendly database from processed data
- `setup.ipynb`: Jupyter notebook for project setup and initial data processing

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

## License

MIT License 