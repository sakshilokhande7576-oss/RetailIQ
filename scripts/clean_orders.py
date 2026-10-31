from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

orders = pd.read_csv(RAW / "olist_orders_dataset.csv")

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

# Convert date fields to datetime; missing values remain missing.
for column in date_columns:
    orders[column] = pd.to_datetime(orders[column], errors="coerce")

# Save an independent processed copy; do not modify raw data.
output = PROCESSED / "orders_cleaned.csv"
orders.to_csv(output, index=False, date_format="%Y-%m-%d %H:%M:%S")

print("ORDERS CLEANING COMPLETE")
print("Rows:", len(orders))
print("Duplicate order IDs:", int(orders["order_id"].duplicated().sum()))
print("\nDate columns and missing counts:")
print(orders[date_columns].isna().sum().to_string())
print("\nOrder status counts:")
print(orders["order_status"].value_counts().to_string())
print("\nSaved to:", output)
