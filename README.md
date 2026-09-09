# Global Geopolitical Event Prediction: Analyzing Impact on Dollar Exchange Rates

## Project Overview
An end-to-end NLP and analytical pipeline to investigate whether global geopolitical news significantly influences and helps predict fluctuations in the US Dollar (USD) exchange rate.

## Repository Structure
```
├── data/
│   ├── raw/                  # Raw scraped news data + JISDOR exchange rate CSV
│   └── processed/            # Cleaned, aligned final dataset
├── src/
│   ├── scraper_news.py       # News data scraper
│   ├── preprocessing.py      # Text cleaning & preprocessing pipeline
│   └── data_alignment.py     # Temporal alignment of news and exchange rates
├── requirements.txt
└── README.md
```

## Task 1: Data Acquisition & Strategic Preprocessing

### Data Sources
- **News Data**: GDELT Project (global geopolitical event database)
- **Exchange Rate Data**: Bank Indonesia JISDOR (USD/IDR daily rate, Sep 2021 – Sep 2026)

### Pipeline Steps
1. **Scraping** — Collect 5 years of geopolitical news articles from GDELT
2. **Filtering** — Remove irrelevant/noisy articles, retain geopolitically relevant content
3. **Preprocessing** — Clean text (lowercasing, HTML removal, tokenization, stopword removal, lemmatization)
4. **Alignment** — Map news to trading days (weekend/holiday news → next business day's JISDOR rate)

## Setup
```bash
pip install -r requirements.txt
python -m nltk.downloader punkt stopwords wordnet
```

## Usage
```bash
# 1. Scrape news data
python src/scraper_news.py

# 2. Run preprocessing on raw news data
python src/preprocessing.py

# 3. Align news with JISDOR exchange rate data
python src/data_alignment.py
```

## Team Members
- [Member 1]
- [Member 2]
- [Member 3]
