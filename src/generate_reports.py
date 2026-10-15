from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
PROCESSED = ROOT / "data" / "processed"

files = [
    ("Customers reviewed", PROCESSED / "customers_reviewed.csv"),
    ("Sales cleaned", PROCESSED / "sales_cleaned.csv"),
    ("Data quality checks", REPORTS / "data_quality_report.csv"),
    ("Sales exceptions", REPORTS / "sales_exceptions.csv"),
]

rows = []
for label, path in files:
    if not path.exists():
        print(f"WARNING: Missing file: {path}")
        continue

    df = pd.read_csv(path)
    missing = int(df.isna().sum().sum())

    if label == "Sales cleaned" and "quality_issue" in df.columns:
        missing -= int(df["quality_issue"].isna().sum())

    rows.append({
        "Dataset": label,
        "Rows": len(df),
        "Columns": len(df.columns),
        "Missing values (excluding blank issue labels)": missing,
    })

summary = pd.DataFrame(rows)
summary.to_csv(REPORTS / "mis_summary.csv", index=False)
print(summary.to_string(index=False))
print("\nMIS summary updated.")
