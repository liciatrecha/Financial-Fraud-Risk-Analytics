# Financial Fraud & Risk Analytics

A portfolio project investigating credit-card transaction patterns using Python, pandas, visualisation, and SQL.

## Project objective
Explore a labelled credit-card transaction dataset, measure the class imbalance, compare transaction amounts, examine time patterns, and evaluate a simple risk-flagging baseline. The goal is to demonstrate analytical workflow and communicate limitations—not to claim that the model can reliably prevent real-world fraud.

## Dataset
Use the public **Credit Card Fraud Detection** dataset from the ULB Machine Learning Group, hosted on Kaggle:
https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

1. Download `creditcard.csv` (your downloaded copy may be named `creditcard-2.csv`).
2. Put the CSV in this project's `data/` folder.
3. Do **not** commit the dataset to GitHub. It is large, and the repository should contain code and documentation rather than a copy of the raw data.
4. Install dependencies and run the analysis below.

The dataset contains anonymised PCA-derived features (`V1`–`V28`), `Time`, `Amount`, and `Class` (1 = labelled fraud, 0 = not labelled fraud). `Class` is the target label. This is an old, highly imbalanced benchmark dataset and is not representative of every modern payment system.

## How to run the project

Open Terminal in this project folder and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/analyze_fraud.py --input data/creditcard-2.csv --output reports
```

If your file is called `creditcard.csv`, use that filename in the command instead.

The script creates:
- `reports/summary.json` — headline metrics
- `reports/transactions_by_class.csv` — count and amount summary by class
- `reports/amount_distribution.png` — amount distribution chart
- `reports/hourly_pattern.png` — approximate time-pattern chart
- `reports/risk_thresholds.csv` — precision/recall at several simple amount thresholds
- `reports/analysis_report.md` — generated findings and limitations

## SQL
`sql/analysis_queries.sql` contains SQLite queries for class counts, amount summaries, hourly patterns, and threshold-based screening. The CSV must first be imported into a SQLite table named `transactions`. The SQL is provided as a transparent companion to the Python analysis.

