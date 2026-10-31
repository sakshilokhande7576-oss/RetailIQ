"""
RetailIQ - Customer Intelligence Engine
Builds historical customer-level RFM, observed lifetime revenue, and inactivity-risk reports.

Inputs:
  data/processed/orders_cleaned.csv
  data/processed/sales_analysis.csv
  data/raw/olist_customers_dataset.csv

Outputs:
  reports/customer_intelligence/customer_metrics.csv
  reports/customer_intelligence/customer_rfm_segments.csv
  reports/customer_intelligence/churn_risk_summary.csv
  reports/customer_intelligence/customer_intelligence_summary.csv
  reports/customer_intelligence/validation_report.csv

Important:
- Uses customer_unique_id, not customer_id, to identify people across orders.
- Uses delivered orders only.
- Churn risk is a historical inactivity proxy as of the last delivered purchase date
  in this dataset, not a statement about customers today.
- Customer lifetime revenue is observed revenue in the available dataset, not
  a predicted lifetime value.
"""

from pathlib import Path
import sys
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent
ORDERS_PATH = ROOT / "data" / "processed" / "orders_cleaned.csv"
SALES_PATH = ROOT / "data" / "processed" / "sales_analysis.csv"
CUSTOMERS_PATH = ROOT / "data" / "raw" / "olist_customers_dataset.csv"
OUTPUT_DIR = ROOT / "reports" / "customer_intelligence"


def require_columns(df, required, file_name):
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"{file_name} is missing required columns: {missing}")


def assign_quantile_score(series, ascending=True):
    """Return a stable 1-5 score even when values contain many ties."""
    ranked = series.rank(method="average", ascending=ascending)
    if ranked.nunique() <= 1:
        return pd.Series(3, index=series.index, dtype="int64")
    scores = pd.qcut(ranked, q=5, labels=False, duplicates="drop")
    return scores.astype("int64") + 1


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for path in (ORDERS_PATH, SALES_PATH, CUSTOMERS_PATH):
        if not path.exists():
            raise FileNotFoundError(f"Required input file not found: {path}")

    print("RetailIQ Customer Intelligence Engine")
    print("-" * 42)
    print("Loading source datasets...")

    orders = pd.read_csv(ORDERS_PATH)
    sales = pd.read_csv(SALES_PATH)
    customers = pd.read_csv(CUSTOMERS_PATH)

    require_columns(
        orders,
        ["order_id", "customer_id", "order_status", "order_purchase_timestamp"],
        ORDERS_PATH.name,
    )
    require_columns(sales, ["order_id", "items_revenue"], SALES_PATH.name)
    require_columns(
        customers, ["customer_id", "customer_unique_id"], CUSTOMERS_PATH.name
    )

    # Keep only the fields needed and avoid accidental duplicate columns.
    customer_map = customers[["customer_id", "customer_unique_id"]].drop_duplicates()
    sales_values = sales[["order_id", "items_revenue"]].drop_duplicates("order_id")

    data = (
        orders.merge(customer_map, on="customer_id", how="left", validate="many_to_one")
        .merge(sales_values, on="order_id", how="left", validate="one_to_one")
    )

    data["order_purchase_timestamp"] = pd.to_datetime(
        data["order_purchase_timestamp"], errors="coerce"
    )
    data["items_revenue"] = pd.to_numeric(data["items_revenue"], errors="coerce")
    data = data[
        (data["order_status"].astype(str).str.lower() == "delivered")
        & data["customer_unique_id"].notna()
        & data["order_purchase_timestamp"].notna()
        & data["items_revenue"].notna()
    ].copy()

    if data.empty:
        raise ValueError("No valid delivered orders remained after data preparation.")

    # Use the final delivered purchase date as the historical observation snapshot.
    snapshot_date = data["order_purchase_timestamp"].max().normalize()

    customer = (
        data.groupby("customer_unique_id", as_index=False)
        .agg(
            frequency=("order_id", "nunique"),
            observed_lifetime_revenue=("items_revenue", "sum"),
            first_purchase=("order_purchase_timestamp", "min"),
            last_purchase=("order_purchase_timestamp", "max"),
            delivered_order_count=("order_id", "nunique"),
        )
    )

    customer["recency_days"] = (
        snapshot_date - customer["last_purchase"].dt.normalize()
    ).dt.days
    customer["customer_age_days"] = (
        customer["last_purchase"].dt.normalize()
        - customer["first_purchase"].dt.normalize()
    ).dt.days
    customer["average_revenue_per_order"] = (
        customer["observed_lifetime_revenue"] / customer["frequency"]
    )

    # Historical inactivity proxy. These labels are relative to snapshot_date.
    customer["inactivity_risk"] = pd.cut(
        customer["recency_days"],
        bins=[-1, 30, 90, 180, np.inf],
        labels=["Active (0-30 days)", "At Risk (31-90 days)",
                "High Risk (91-180 days)", "Dormant (181+ days)"],
        right=True,
    ).astype("string")

    # RFM scoring: lower recency is better; higher frequency/monetary is better.
    customer["R_score"] = assign_quantile_score(
        customer["recency_days"], ascending=False
    )
    customer["F_score"] = assign_quantile_score(
        customer["frequency"], ascending=True
    )
    customer["M_score"] = assign_quantile_score(
        customer["observed_lifetime_revenue"], ascending=True
    )
    customer["RFM_score"] = (
        customer["R_score"].astype(str)
        + customer["F_score"].astype(str)
        + customer["M_score"].astype(str)
    )

    def rfm_label(row):
        r, f, m = row["R_score"], row["F_score"], row["M_score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        if r >= 3 and f >= 3:
            return "Loyal / Active"
        if r >= 4 and f <= 2:
            return "Recent Customers"
        if r <= 2 and f >= 3:
            return "At Risk - Previously Frequent"
        if r <= 2 and m >= 4:
            return "High Value - Needs Attention"
        if r <= 2:
            return "Hibernating"
        return "Potential Loyalists"

    customer["rfm_segment"] = customer.apply(rfm_label, axis=1)

    # Export detailed customer-level metrics.
    customer.to_csv(
        OUTPUT_DIR / "customer_metrics.csv", index=False, encoding="utf-8-sig"
    )

    rfm_summary = (
        customer.groupby("rfm_segment", observed=False)
        .agg(
            customers=("customer_unique_id", "nunique"),
            total_observed_revenue=("observed_lifetime_revenue", "sum"),
            avg_recency_days=("recency_days", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_customer_revenue=("observed_lifetime_revenue", "mean"),
        )
        .reset_index()
        .sort_values("customers", ascending=False)
    )
    rfm_summary.to_csv(
        OUTPUT_DIR / "customer_rfm_segments.csv", index=False, encoding="utf-8-sig"
    )

    churn_summary = (
        customer.groupby("inactivity_risk", observed=False)
        .agg(
            customers=("customer_unique_id", "nunique"),
            observed_revenue=("observed_lifetime_revenue", "sum"),
            avg_recency_days=("recency_days", "mean"),
            avg_frequency=("frequency", "mean"),
        )
        .reset_index()
    )
    churn_summary["customer_share_pct"] = (
        churn_summary["customers"] / len(customer) * 100
    ).round(2)
    churn_summary.to_csv(
        OUTPUT_DIR / "churn_risk_summary.csv", index=False, encoding="utf-8-sig"
    )

    summary_rows = [
        ("Historical snapshot date", snapshot_date.strftime("%Y-%m-%d")),
        ("Delivered orders analyzed", int(data["order_id"].nunique())),
        ("Unique customers analyzed", int(customer["customer_unique_id"].nunique())),
        ("Repeat customers (2+ delivered orders)", int((customer["frequency"] >= 2).sum())),
        ("Repeat customer rate (%)", round((customer["frequency"] >= 2).mean() * 100, 2)),
        ("Average observed customer revenue (R$)", round(customer["observed_lifetime_revenue"].mean(), 2)),
        ("Median delivered orders per customer", float(customer["frequency"].median())),
        ("Customers inactive more than 90 days", int((customer["recency_days"] > 90).sum())),
        ("Customers inactive more than 180 days", int((customer["recency_days"] > 180).sum())),
        ("Total observed item revenue (R$)", round(customer["observed_lifetime_revenue"].sum(), 2)),
        ("Definition", "Historical inactivity proxy; not verified present-day churn or predictive CLV."),
    ]
    pd.DataFrame(summary_rows, columns=["Metric", "Value"]).to_csv(
        OUTPUT_DIR / "customer_intelligence_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )

    validation = [
        ("Source delivered rows", int((orders["order_status"].astype(str).str.lower() == "delivered").sum())),
        ("Analyzed delivered orders", int(data["order_id"].nunique())),
        ("Unique customer identities", int(customer["customer_unique_id"].nunique())),
        ("Rows in customer metrics", int(len(customer))),
        ("Missing customer_unique_id after join", int(data["customer_unique_id"].isna().sum())),
        ("Missing revenue after join (before filtering)", int(sales_values["items_revenue"].isna().sum())),
        ("Negative observed customer revenue", int((customer["observed_lifetime_revenue"] < 0).sum())),
        ("Duplicate customer rows in output", int(customer["customer_unique_id"].duplicated().sum())),
    ]
    pd.DataFrame(validation, columns=["Check", "Value"]).to_csv(
        OUTPUT_DIR / "validation_report.csv", index=False, encoding="utf-8-sig"
    )

    print("\nCustomer Intelligence Engine completed successfully.")
    print(f"Historical snapshot: {snapshot_date.date()}")
    print(f"Delivered orders analyzed: {data['order_id'].nunique():,}")
    print(f"Unique customers: {len(customer):,}")
    print(f"Repeat customers: {(customer['frequency'] >= 2).sum():,}")
    print(f"Repeat customer rate: {(customer['frequency'] >= 2).mean() * 100:.2f}%")
    print("\nGenerated reports:")
    for filename in [
        "customer_metrics.csv",
        "customer_rfm_segments.csv",
        "churn_risk_summary.csv",
        "customer_intelligence_summary.csv",
        "validation_report.csv",
    ]:
        print(f" - {OUTPUT_DIR / filename}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        raise
