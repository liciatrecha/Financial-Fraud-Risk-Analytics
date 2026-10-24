#!/usr/bin/env python3
"""Exploratory credit-card fraud analytics. Outputs reproducible summaries and charts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


REQUIRED = {"Time", "Amount", "Class"}


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find dataset: {path}\n"
            "Place the CSV in the data/ folder and pass its path with --input."
        )
    df = pd.read_csv(path)
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["Time"] = pd.to_numeric(df["Time"], errors="coerce")
    df["Class"] = pd.to_numeric(df["Class"], errors="coerce")
    df = df.dropna(subset=["Amount", "Time", "Class"]).copy()
    df = df[df["Class"].isin([0, 1])].copy()
    df["Class"] = df["Class"].astype(int)
    return df


def safe_float(value):
    if pd.isna(value) or not np.isfinite(value):
        return None
    return float(value)


def evaluate_thresholds(df: pd.DataFrame) -> pd.DataFrame:
    """Evaluate amount-only rules; these are illustrative baselines, not fraud models."""
    rows = []
    for threshold in [50, 100, 250, 500, 1000]:
        flagged = df["Amount"] >= threshold
        tp = int(((flagged) & (df["Class"] == 1)).sum())
        fp = int(((flagged) & (df["Class"] == 0)).sum())
        fn = int(((~flagged) & (df["Class"] == 1)).sum())
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        rows.append({
            "amount_threshold": threshold,
            "flagged_transactions": int(flagged.sum()),
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": precision,
            "recall": recall,
        })
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="data/creditcard.csv", help="Path to dataset CSV")
    parser.add_argument("--output", default="reports", help="Directory for reports and charts")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser()
    out = Path(args.output).expanduser()
    out.mkdir(parents=True, exist_ok=True)

    df = load_data(input_path)
    total = int(len(df))
    fraud_count = int((df["Class"] == 1).sum())
    nonfraud_count = int((df["Class"] == 0).sum())
    fraud_rate = fraud_count / total if total else 0.0

    by_class = df.groupby("Class").agg(
        transaction_count=("Class", "size"),
        mean_amount=("Amount", "mean"),
        median_amount=("Amount", "median"),
        total_amount=("Amount", "sum"),
    ).reset_index()
    by_class.to_csv(out / "transactions_by_class.csv", index=False)

    thresholds = evaluate_thresholds(df)
    thresholds.to_csv(out / "risk_thresholds.csv", index=False)

    # Transaction amount distribution: clip only for readable visualisation.
    fig, ax = plt.subplots(figsize=(9, 5))
    max_plot = float(df["Amount"].quantile(0.99))
    for label, name in [(0, "Class 0 (not labelled fraud)"), (1, "Class 1 (labelled fraud)")]:
        vals = df.loc[df["Class"] == label, "Amount"]
        vals = vals[vals <= max_plot]
        if not vals.empty:
            ax.hist(vals, bins=50, alpha=0.65, label=name)
    ax.set_title("Transaction amounts (values at or below 99th percentile)")
    ax.set_xlabel("Transaction amount")
    ax.set_ylabel("Number of transactions")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "amount_distribution.png", dpi=160)
    plt.close(fig)

    # Dataset Time is seconds elapsed from the first transaction, not clock time.
    df["elapsed_hour"] = (df["Time"] // 3600).astype(int)
    hourly = df.groupby(["elapsed_hour", "Class"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(9, 5))
    if 0 in hourly.columns:
        ax.plot(hourly.index, hourly[0], label="Class 0")
    if 1 in hourly.columns:
        ax.plot(hourly.index, hourly[1], label="Class 1")
    ax.set_title("Transaction counts by elapsed-hour bucket")
    ax.set_xlabel("Elapsed hour bucket (dataset-relative; not time of day)")
    ax.set_ylabel("Transaction count")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "hourly_pattern.png", dpi=160)
    plt.close(fig)

    summary = {
        "dataset_rows_analysed": total,
        "labelled_fraud_transactions": fraud_count,
        "class_0_transactions": nonfraud_count,
        "labelled_fraud_rate_percent": round(fraud_rate * 100, 6),
        "overall_median_amount": safe_float(df["Amount"].median()),
        "overall_mean_amount": safe_float(df["Amount"].mean()),
        "labelled_fraud_median_amount": safe_float(df.loc[df["Class"] == 1, "Amount"].median()),
        "class_0_median_amount": safe_float(df.loc[df["Class"] == 0, "Amount"].median()),
        "amount_99th_percentile_for_chart": safe_float(df["Amount"].quantile(0.99)),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    top = thresholds.sort_values("amount_threshold")
    report = f"""# Financial Fraud & Risk Analytics — Generated Findings

## Dataset overview
- Rows analysed: **{total:,}**
- Transactions labelled as fraud: **{fraud_count:,}**
- Class 0 transactions: **{nonfraud_count:,}**
- Labelled fraud rate: **{fraud_rate * 100:.6f}%**
- Overall median transaction amount: **{df['Amount'].median():.2f}**
- Median amount for labelled fraud: **{df.loc[df['Class'] == 1, 'Amount'].median():.2f}**
- Median amount for class 0: **{df.loc[df['Class'] == 0, 'Amount'].median():.2f}**

## Interpretation
The label distribution shows whether the dataset is imbalanced. In a highly imbalanced dataset, accuracy alone is misleading: a system can label almost everything as class 0 and still achieve high accuracy while missing fraud.

The amount-threshold table evaluates a deliberately simple baseline that flags transactions at or above a given amount. Review `risk_thresholds.csv` to compare precision and recall. This is **not** a recommended production fraud rule: fraud is not defined solely by transaction amount, and the benchmark's features and collection period limit real-world generalisation.

## Files generated
- `transactions_by_class.csv`
- `risk_thresholds.csv`
- `amount_distribution.png`
- `hourly_pattern.png`
- `summary.json`

## Limitations and responsible use
- `Class = 1` means labelled fraud in this benchmark; it is not a universal definition of suspicious activity.
- `V1`–`V28` are anonymised features, so their business meaning is not directly interpretable.
- The `Time` feature is elapsed seconds from the dataset's first transaction. It is not a clock time or date.
- Threshold metrics are measured on the same dataset used for exploration and should not be presented as out-of-sample model performance.
- This is a learning project using a public benchmark, not a deployed bank system. Any real-world use would require stronger validation, privacy controls, fairness review, human oversight, and monitoring.
"""
    (out / "analysis_report.md").write_text(report, encoding="utf-8")
    print(f"Analysis complete. Reports saved to: {out.resolve()}")
    print(f"Rows analysed: {total:,} | labelled fraud: {fraud_count:,} ({fraud_rate*100:.6f}%)")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
