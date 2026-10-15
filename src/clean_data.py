from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"

PROCESSED.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

customers = pd.read_csv(RAW / "customers.csv")
sales = pd.read_csv(RAW / "sales.csv")

checks = []

def record_check(name, count, status):
    checks.append({
        "check": name,
        "affected_records": int(count),
        "status": status
    })

# Check customer data
missing_customer_ids = customers["customer_id"].isna().sum()
duplicate_customer_ids = customers["customer_id"].duplicated().sum()
missing_customer_names = customers["customer_name"].isna().sum()
missing_cities = customers["city"].isna().sum()

record_check("Missing customer IDs", missing_customer_ids, "PASS" if missing_customer_ids == 0 else "FAIL")
record_check("Duplicate customer IDs", duplicate_customer_ids, "PASS" if duplicate_customer_ids == 0 else "FAIL")
record_check("Missing customer names", missing_customer_names, "REVIEW" if missing_customer_names else "PASS")
record_check("Missing customer cities", missing_cities, "REVIEW" if missing_cities else "PASS")

# Check sales data
duplicate_transactions = sales["transaction_id"].duplicated().sum()
missing_quantities = sales["quantity"].isna().sum()
negative_sales = (sales["sales_amount"] < 0).sum()
unknown_customers = (~sales["customer_id"].isin(customers["customer_id"])).sum()

record_check("Duplicate transaction IDs", duplicate_transactions, "REVIEW" if duplicate_transactions else "PASS")
record_check("Missing quantities", missing_quantities, "REVIEW" if missing_quantities else "PASS")
record_check("Negative sales amounts", negative_sales, "FAIL" if negative_sales else "PASS")
record_check("Unknown customer IDs", unknown_customers, "FAIL" if unknown_customers else "PASS")

# Remove duplicate transaction IDs, keeping the first occurrence
clean_sales = sales.drop_duplicates(subset=["transaction_id"], keep="first").copy()

# Replace invalid negative sales amounts with missing values for review
clean_sales.loc[clean_sales["sales_amount"] < 0, "sales_amount"] = pd.NA

# Recalculate sales only when quantity and unit price are available
valid_amount = (
    clean_sales["quantity"].notna()
    & clean_sales["unit_price"].notna()
    & (clean_sales["quantity"] >= 0)
    & (clean_sales["unit_price"] >= 0)
)
missing_amount = clean_sales["sales_amount"].isna() & valid_amount
clean_sales.loc[missing_amount, "sales_amount"] = (
    clean_sales.loc[missing_amount, "quantity"]
    * clean_sales.loc[missing_amount, "unit_price"]
)

# Flag rows with unresolved issues instead of silently deleting them
clean_sales["quality_issue"] = ""
clean_sales.loc[clean_sales["quantity"].isna(), "quality_issue"] += "Missing quantity; "
clean_sales.loc[clean_sales["sales_amount"].isna(), "quality_issue"] += "Missing/invalid sales amount; "
clean_sales.loc[
    ~clean_sales["customer_id"].isin(customers["customer_id"]),
    "quality_issue"
] += "Unknown customer; "

# Keep all customer records, including those needing review
customers.to_csv(PROCESSED / "customers_reviewed.csv", index=False)
clean_sales.to_csv(PROCESSED / "sales_cleaned.csv", index=False)

quality_report = pd.DataFrame(checks)
quality_report.to_csv(REPORTS / "data_quality_report.csv", index=False)

exceptions = clean_sales[clean_sales["quality_issue"] != ""]
exceptions.to_csv(REPORTS / "sales_exceptions.csv", index=False)

print("Data quality checks completed!")
print(f"Original sales rows: {len(sales):,}")
print(f"Sales rows after duplicate removal: {len(clean_sales):,}")
print(f"Quality checks recorded: {len(quality_report)}")
print(f"Sales rows flagged for review: {len(exceptions):,}")
print(f"Quality report: {REPORTS / 'data_quality_report.csv'}")
print(f"Exception report: {REPORTS / 'sales_exceptions.csv'}")
