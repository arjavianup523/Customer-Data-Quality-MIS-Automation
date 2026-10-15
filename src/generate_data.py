from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(42)

# Generate 1,000 synthetic customer records
n_customers = 1000

customers = pd.DataFrame({
    "customer_id": range(1001, 1001 + n_customers),
    "customer_name": [f"Customer_{i}" for i in range(1, n_customers + 1)],
    "city": rng.choice(
        ["Mumbai", "Pune", "Bengaluru", "Delhi", "Hyderabad"],
        n_customers
    ),
    "signup_date": rng.choice(
        pd.date_range("2025-01-01", "2026-09-30"),
        n_customers
    ),
    "customer_type": rng.choice(
        ["Retail", "Business"], n_customers
    ),
})

# Generate 3,000 synthetic sales records
n_sales = 3000

sales = pd.DataFrame({
    "transaction_id": range(5001, 5001 + n_sales),
    "customer_id": rng.choice(customers["customer_id"], n_sales),
    "transaction_date": rng.choice(
        pd.date_range("2026-01-01", "2026-10-01"),
        n_sales
    ),
    "product": rng.choice(
        ["Laptop", "Phone", "Tablet", "Monitor", "Keyboard"],
        n_sales
    ),
    "quantity": rng.integers(1, 6, n_sales),
    "unit_price": rng.choice(
        [500, 1000, 2500, 5000, 10000], n_sales
    ),
})

sales["sales_amount"] = sales["quantity"] * sales["unit_price"]

# Introduce intentional data-quality issues for testing
customers.loc[[5, 25, 80], "city"] = None
customers.loc[[12, 45], "customer_name"] = None

sales.loc[[10, 50, 100], "quantity"] = np.nan
sales.loc[[20, 70], "sales_amount"] = -500

# Add two duplicate transactions
sales = pd.concat(
    [sales, sales.iloc[[10, 50]]],
    ignore_index=True
)

customers.to_csv(RAW / "customers.csv", index=False)
sales.to_csv(RAW / "sales.csv", index=False)

print("Synthetic business data generated successfully!")
print(f"Customers: {len(customers):,}")
print(f"Sales records: {len(sales):,}")
print(f"Raw data folder: {RAW}")
