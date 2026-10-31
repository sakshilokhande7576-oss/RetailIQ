
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# RetailIQ - Retail Intelligence Dashboard
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = PROJECT_DIR / "reports"

st.set_page_config(
    page_title="RetailIQ | Retail Intelligence",
    page_icon="📊",
    layout="wide",
)

st.title("RetailIQ")
st.subheader("Retail Intelligence & Customer Analytics")
st.caption("E-commerce analytics | Olist dataset | Local dashboard")

# Load exported analysis data
@st.cache_data
def load_data():
    monthly = pd.read_csv(REPORTS_DIR / "monthly_sales_summary.csv")
    categories = pd.read_csv(REPORTS_DIR / "category_sales_summary.csv")
    rfm = pd.read_csv(REPORTS_DIR / "customer_rfm_segments.csv")
    sales = pd.read_csv(PROJECT_DIR / "data" / "processed" / "sales_analysis.csv")
    return monthly, categories, rfm, sales

try:
    monthly, categories, rfm, sales = load_data()
except FileNotFoundError as error:
    st.error(f"Required project file not found: {error.filename}")
    st.info("Check that the processed and report CSV files exist.")
    st.stop()

# Normalize data types
monthly["item_revenue"] = pd.to_numeric(monthly["item_revenue"], errors="coerce")
categories["item_revenue"] = pd.to_numeric(categories["item_revenue"], errors="coerce")
categories["units_sold"] = pd.to_numeric(categories["units_sold"], errors="coerce")
sales["items_revenue"] = pd.to_numeric(sales["items_revenue"], errors="coerce")
rfm["monetary"] = pd.to_numeric(rfm["monetary"], errors="coerce")

# Sidebar filters
st.sidebar.header("Dashboard Filters")

if "order_status" in sales.columns:
    status_options = sorted(sales["order_status"].dropna().unique().tolist())
    selected_statuses = st.sidebar.multiselect(
        "Order status",
        options=status_options,
        default=["delivered"] if "delivered" in status_options else status_options,
    )
    filtered_sales = sales[sales["order_status"].isin(selected_statuses)].copy()
else:
    filtered_sales = sales.copy()

segment_options = sorted(rfm["segment"].dropna().unique().tolist())
selected_segments = st.sidebar.multiselect(
    "Customer segments",
    options=segment_options,
    default=segment_options,
)
filtered_rfm = rfm[rfm["segment"].isin(selected_segments)].copy()

# KPI calculations
order_count = filtered_sales["order_id"].nunique()
item_revenue = filtered_sales["items_revenue"].sum()
average_order_value = (
    filtered_sales.dropna(subset=["items_revenue"])
    .groupby("order_id")["items_revenue"]
    .first()
    .mean()
)

customer_count = filtered_rfm["customer_unique_id"].nunique()

st.markdown("### Business Overview")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Orders", f"{order_count:,}")
k2.metric("Item Revenue", f"R$ {item_revenue:,.0f}")
k3.metric("Avg. Item Value / Order", f"R$ {average_order_value:,.2f}" if pd.notna(average_order_value) else "N/A")
k4.metric("Customers in Selected Segments", f"{customer_count:,}")

st.caption(
    "Item revenue excludes shipping and is not profit. "
    "Order KPIs follow the selected order-status filter."
)

# Monthly sales trend
st.markdown("### Monthly Delivered Sales")
monthly_plot = monthly.copy()
monthly_plot["purchase_month"] = monthly_plot["purchase_month"].astype(str)

fig_monthly = px.line(
    monthly_plot,
    x="purchase_month",
    y="item_revenue",
    markers=True,
    title="Monthly Item Revenue",
    labels={
        "purchase_month": "Purchase Month",
        "item_revenue": "Item Revenue (R$)",
    },
)
fig_monthly.update_layout(hovermode="x unified")
st.plotly_chart(fig_monthly, use_container_width=True)

# Product category performance
st.markdown("### Product Category Performance")
top_n = st.slider("Number of product categories", 5, 20, 10)

category_plot = (
    categories.sort_values("item_revenue", ascending=False)
    .head(top_n)
    .sort_values("item_revenue", ascending=True)
)

fig_categories = px.bar(
    category_plot,
    x="item_revenue",
    y="product_category_name_english",
    orientation="h",
    title=f"Top {top_n} Categories by Delivered Item Revenue",
    labels={
        "item_revenue": "Item Revenue (R$)",
        "product_category_name_english": "Product Category",
    },
    hover_data=["units_sold", "unique_orders"],
)
st.plotly_chart(fig_categories, use_container_width=True)

# Customer segmentation
st.markdown("### Customer Segmentation (RFM)")
if not filtered_rfm.empty:
    segment_summary = (
        filtered_rfm.groupby("segment", observed=True)
        .agg(
            customers=("customer_unique_id", "nunique"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
            total_monetary=("monetary", "sum"),
        )
        .reset_index()
        .sort_values("customers", ascending=False)
    )

    left, right = st.columns(2)

    with left:
        fig_segments = px.bar(
            segment_summary,
            x="segment",
            y="customers",
            title="Customers by Segment",
            labels={"segment": "Segment", "customers": "Customers"},
        )
        st.plotly_chart(fig_segments, use_container_width=True)

    with right:
        fig_segment_revenue = px.bar(
            segment_summary,
            x="segment",
            y="total_monetary",
            title="Total Item Spend by Segment",
            labels={"segment": "Segment", "total_monetary": "Item Revenue (R$)"},
        )
        st.plotly_chart(fig_segment_revenue, use_container_width=True)

    st.dataframe(
        segment_summary.round(2),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.warning("No customers match the selected segment filters.")

# Data explorer
with st.expander("Explore summary data"):
    st.markdown("**Monthly sales data**")
    st.dataframe(monthly, use_container_width=True, hide_index=True)

    st.markdown("**Product category data**")
    st.dataframe(categories, use_container_width=True, hide_index=True)

    st.markdown("**Customer RFM data (first 100 rows)**")
    st.dataframe(filtered_rfm.head(100), use_container_width=True, hide_index=True)

st.divider()
st.caption("RetailIQ | Portfolio analytics project | Runs locally on your computer")
