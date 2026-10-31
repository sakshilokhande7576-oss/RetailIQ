from pathlib import Path
import gc
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "raw"
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

summary = []
column_details = []

files = sorted(DATA_DIR.glob("*.csv"))

if not files:
    raise FileNotFoundError(f"No CSV files found in {DATA_DIR}")

for file in files:
    print(f"Auditing: {file.name}")
    df = pd.read_csv(file, low_memory=False)

    rows, cols = df.shape
    duplicate_rows = int(df.duplicated().sum())
    missing_total = int(df.isna().sum().sum())

    summary.append({
        "file": file.name,
        "rows": rows,
        "columns": cols,
        "duplicate_rows": duplicate_rows,
        "missing_cells": missing_total,
        "missing_percent": round(missing_total / (rows * cols) * 100, 2)
            if rows * cols else 0
    })

    missing = df.isna().sum()
    for col in df.columns:
        column_details.append({
            "file": file.name,
            "column": col,
            "data_type": str(df[col].dtype),
            "missing_count": int(missing[col]),
            "missing_percent": round(missing[col] / rows * 100, 2)
                if rows else 0
        })

    del df
    gc.collect()

summary_df = pd.DataFrame(summary)
details_df = pd.DataFrame(column_details)

summary_df.to_csv(REPORT_DIR / "dataset_summary.csv", index=False)
details_df.to_csv(REPORT_DIR / "column_quality_report.csv", index=False)

print("\n=== DATASET SUMMARY ===")
print(summary_df.to_string(index=False))
print(f"\nTotal CSV files: {len(files)}")
print(f"Reports saved in: {REPORT_DIR}")
print("1. dataset_summary.csv")
print("2. column_quality_report.csv")
