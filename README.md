# CrowdInsight: Kickstarter Campaign Success Predictor (Data Preprocessing)

![Kickstarter Analytics](https://img.shields.io/badge/Kickstarter-Analytics-brightgreen)
![Data Science](https://img.shields.io/badge/Data-Science-blue)
![NLP](https://img.shields.io/badge/NLP-Embeddings-orange)

## Overview

CrowdInsight is a comprehensive data analysis project focused on predicting Kickstarter campaign success with explainable AI techniques. This repository contains the data preprocessing pipeline that transforms raw Kickstarter data into structured features suitable for machine learning models.

**Related Projects:**
- 🤖 [CrowdInsight-Model](https://github.com/angusf777/CrowdInsight-Model) - ML models for campaign success prediction
- 🗃️ [Kickstarter-Scraper](https://github.com/lkh2/Kickstarter-Scraper) - Scraper for detailed campaign descriptions and content

## Data Sources

This preprocessing pipeline works with data from two primary sources:

1. **[Webrobots.io](https://webrobots.io/kickstarter-datasets/)** - Structured Kickstarter metadata scraped periodically
2. **Campaign Content Data** - Detailed campaign descriptions, risks, and media scraped using methods from [lkh2/Kickstarter-Scraper](https://github.com/lkh2/Kickstarter-Scraper)

## Preprocessing Pipeline

The repository implements a multi-stage pipeline that transforms raw data into model-ready features:

### 1. Data Cleaning & Filtering (`Tools/`)
- **check_duplicates.py** - Removes duplicate campaign entries
- **filter_kickstarter.py** - Filters campaigns based on state and applies special handling for canceled projects
- **make_WebDatabase.py** - Creates a normalized web-friendly database with standardized fields

### 2. Feature Generation (`Processor.py`)
The core processor transforms campaign data into ML-ready features using advanced NLP techniques:

#### Text Processing
- Campaign descriptions → Longformer embeddings (768-dimensional vectors)
- Risk statements and blurbs → MiniLM embeddings (384-dimensional vectors)
- Categories/subcategories → GloVe embeddings (100-dimensional vectors)
- Country information → GloVe embeddings (100-dimensional vectors)

#### Numerical Features
- Funding goals (log-transformed)
- Campaign duration
- Image and video counts
- Previous campaign metrics
- Success rate indicators

### 3. Analysis Tools
- **row1+2_analysis.py** - Temporal and categorical analysis of projects
- **backer_analysis.py** - Analyzes backer funding patterns
- **Plot visualizations** - Distribution charts for funding goals, countries, and backer metrics

## Setup and Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/angusf777/CrowdInsight.git
   cd CrowdInsight
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the setup notebook:**
   ```bash
   jupyter notebook setup.ipynb
   ```
   This notebook guides you through the entire preprocessing pipeline from raw data to model-ready features.

4. **Run specific analysis tools:**
   ```bash
   # Analyze projects from the last 30 days
   python Tools/row1+2_analysis.py --timeframe 30d
   
   # Analyze technology category projects
   python Tools/row1+2_analysis.py --category technology
   
   # Analyze backer patterns
   python Tools/backer_analysis.py
   ```

## Embedding Models

Our pipeline uses state-of-the-art NLP models to capture semantic meaning from campaign text:

### Longformer
Used for processing long campaign descriptions (up to 4096 tokens)
```
@article{Beltagy2020Longformer,
  title={Longformer: The Long-Document Transformer},
  author={Iz Beltagy and Matthew E. Peters and Arman Cohan},
  journal={arXiv:2004.05150},
  year={2020},
}
```

### MiniLM (Sentence-Transformers)
Used for processing shorter texts like risks and blurbs
```
@article{wang2020minilm,
  title   = {MiniLM: Deep Self-Attention Distillation for Task-Agnostic Compression of Pre-Trained Transformers},
  author  = {Wenhui Wang and Furu Wei and Li Dong and Hangbo Bao and Nan Yang and Ming Zhou},
  journal = {arXiv preprint arXiv:2002.10957},
  year    = {2020},
}

@inproceedings{reimers2019sentencebert,
  title     = {Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks},
  author    = {Nils Reimers and Iryna Gurevych},
  booktitle = {Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing},
  pages     = {3980--3990},
  year      = {2019},
}
```

### GloVe
Used for embedding categorical data like countries and subcategories
```
@inproceedings{pennington2014glove,
  title     = {GloVe: Global Vectors for Word Representation},
  author    = {Jeffrey Pennington and Richard Socher and Christopher D. Manning},
  booktitle = {Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing},
  pages     = {1532--1543},
  year      = {2014},
  doi       = {10.3115/v1/D14-1162}
}
```

## Project Structure

```
CrowdInsight/
├── Data/                   # Processed data files
├── Tools/                  # Analysis and data processing scripts
│   ├── check_duplicates.py # Remove duplicate entries
│   ├── filter_kickstarter.py # Filter campaigns by state
│   ├── make_WebDatabase.py # Create web-friendly database
│   ├── row1+2_analysis.py  # Temporal/categorical analysis
│   ├── backer_analysis.py  # Backer funding patterns
│   └── plot/               # Visualization modules
├── Processor.py            # Main feature extraction pipeline
├── plot_canceled_distribution.py # Visualize canceled projects
├── setup.ipynb             # End-to-end preprocessing workflow
└── requirements.txt        # Project dependencies
```

## Authors

- **Fung Angus**
- **Qian Yongkun Jonathan**

*April 2025*

## License

MIT License 