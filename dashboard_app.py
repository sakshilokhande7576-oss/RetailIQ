from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# RETAILIQ | PREMIUM BUSINESS INTELLIGENCE PLATFORM
# --------------------------------------------------

PROJECT = Path(__file__).resolve().parent
REPORTS = PROJECT / "reports"

st.set_page_config(
    page_title="RetailIQ | Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- PREMIUM THEME -------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background: linear-gradient(135deg, #080d1b 0%, #10172b 55%, #111329 100%);
    color: #eef2ff;
}
[data-testid="stSidebar"] {
    background: #0b1020;
    border-right: 1px solid #27314d;
}
[data-testid="stSidebar"] * { color: #dce5ff !important; }
.hero {
    background: linear-gradient(110deg, #171f3d, #282052, #123b4b);
    padding: 30px 34px; border-radius: 18px;
    border: 1px solid #39466c; margin-bottom: 25px;
}
.hero h1 { color: #fff; font-size: 36px; font-weight: 800; margin: 0; }
.hero p { color: #b9c7e8; margin-top: 8px; font-size: 14px; }
.section-title {
    color: #e8edff; font-size: 21px; font-weight: 700;
    margin: 18px 0 12px 0;
}
.kpi-card {
    background: linear-gradient(145deg, #192440, #151c32);
    border: 1px solid #344263; border-radius: 15px;
    padding: 19px; min-height: 115px;
}
.kpi-label {
    color: #aab8d6; font-size: 12px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 1px;
}
.kpi-value { color: #fff; font-size: 25px; font-weight: 800; margin-top: 12px; }
.kpi-accent { color: #35d6c0; font-size: 11px; margin-top: 5px; }
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #192440, #151c32);
    border: 1px solid #344263; border-radius: 14px; padding: 17px;
}
div[data-testid="stMetricLabel"] { color: #aab8d6; }
div[data-testid="stMetricValue"] { color: #fff; }
hr { border-color: #293653; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------------- DATA LOADING --------------------

@st.cache_data
def load_data():
    files = {
        "kpis": "dashboard_kpis.csv",
        "monthly": "dashboard_monthly_sales.csv",
        "categories": "dashboard_top_categories.csv",
        "segments": "dashboard_customer_segments.csv",
        "insights": "business_insights_report.csv",
    }
    data = {}
    for key, filename in files.items():
        path = REPORTS / filename
        if not path.exists():
            if key == "insights":
                data[key] = pd.DataFrame(columns=["Area", "Finding", "Recommendation"])
                continue
            raise FileNotFoundError(f"Missing report file: {path}")
        data[key] = pd.read_csv(path)
    return data

try:
    data = load_data()
except Exception as error:
    st.error(f"Unable to load dashboard data: {error}")
    st.stop()

kpis = data["kpis"].copy()
monthly = data["monthly"].copy()
categories = data["categories"].copy()
segments = data["segments"].copy()
insights = data["insights"].copy()

# ---------------- DATA PREPARATION -----------------

required_columns = {
    "kpis": {"KPI", "Value"},
    "monthly": {"purchase_month", "delivered_orders", "item_revenue"},
    "categories": {"product_category_name_english", "units_sold", "item_revenue", "unique_orders"},
    "segments": {"segment", "customers", "total_item_revenue"},
}
frames = {"kpis": kpis, "monthly": monthly, "categories": categories, "segments": segments}

for key, required in required_columns.items():
    missing = required - set(frames[key].columns)
    if missing:
        st.error(f"{key} report is missing columns: {', '.join(sorted(missing))}")
        st.stop()

for frame, columns in [
    (monthly, ["delivered_orders", "item_revenue"]),
    (categories, ["units_sold", "item_revenue", "unique_orders"]),
    (segments, ["customers", "total_item_revenue"]),
]:
    for column in columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0)

monthly["purchase_month"] = monthly["purchase_month"].astype(str)
monthly = monthly.sort_values("purchase_month").reset_index(drop=True)
categories["product_category_name_english"] = categories["product_category_name_english"].fillna("Unknown")
segments["segment"] = segments["segment"].fillna("Unknown")

if not insights.empty:
    for column in ["Area", "Finding", "Recommendation"]:
        if column in insights.columns:
            insights[column] = insights[column].fillna("")

def get_kpi(name):
    row = kpis.loc[kpis["KPI"] == name, "Value"]
    if row.empty:
        return 0.0
    value = pd.to_numeric(row.iloc[0], errors="coerce")
    return 0.0 if pd.isna(value) else float(value)

def money(value):
    return f"R$ {value:,.2f}"

def style_chart(fig, height=350):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dce5ff", family="Inter"),
        title_font=dict(size=16, color="#ffffff"),
        margin=dict(l=15, r=15, t=55, b=15),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#cbd5ef")),
        xaxis=dict(gridcolor="#273653", zerolinecolor="#273653"),
        yaxis=dict(gridcolor="#273653", zerolinecolor="#273653"),
    )
    return fig

# ---------------- SIDEBAR --------------------------

st.sidebar.markdown("## 📊 RetailIQ")
st.sidebar.caption("RETAIL INTELLIGENCE PLATFORM")
st.sidebar.divider()

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Executive Command Center",
        "Sales & Revenue Intelligence",
        "Product & Category Intelligence",
        "Customer & RFM Intelligence",
        "Business Insights"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("**DATA SOURCE**")
st.sidebar.caption("Olist Brazilian E-Commerce Dataset")
st.sidebar.caption("Local Analytics Environment")
st.sidebar.divider()
st.sidebar.caption("Python • Pandas • Streamlit • Plotly")

# ---------------- HEADER ---------------------------

st.markdown("""
<div class="hero">
    <h1>RETAILIQ</h1>
    <p>Enterprise E-Commerce Analytics & Business Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

# ---------------- EXECUTIVE COMMAND CENTER ---------

if page == "Executive Command Center":
    st.markdown('<div class="section-title">Executive Command Center</div>', unsafe_allow_html=True)

    metrics = [
        ("DELIVERED ORDERS", f"{get_kpi('Delivered Orders'):,.0f}"),
        ("ITEM REVENUE", money(get_kpi("Delivered Item Revenue (R$)"))),
        ("AVG REVENUE / ORDER", money(get_kpi("Average Item Revenue per Order (R$)"))),
        ("UNIQUE CUSTOMERS", f"{get_kpi('Unique Customers'):,.0f}"),
    ]
    cols = st.columns(4)
    for col, (label, value) in zip(cols, metrics):
        with col:
            st.markdown(
                f"""<div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-accent">● Olist dataset metric</div>
                </div>""",
                unsafe_allow_html=True
            )

    st.markdown('<div class="section-title">Revenue Performance Overview</div>', unsafe_allow_html=True)
    fig = px.area(
        monthly, x="purchase_month", y="item_revenue", markers=True,
        labels={"purchase_month": "Purchase Month", "item_revenue": "Revenue (R$)"}
    )
    fig.update_traces(line_color="#8b7cff", fillcolor="rgba(139,124,255,0.20)")
    st.plotly_chart(style_chart(fig, 390), width="stretch")

    left, right = st.columns(2)
    with left:
        st.markdown("#### Top Revenue Categories")
        top = categories.nlargest(5, "item_revenue").sort_values("item_revenue")
        fig = px.bar(
            top, x="item_revenue", y="product_category_name_english",
            orientation="h",
            labels={"item_revenue": "Revenue (R$)", "product_category_name_english": "Category"}
        )
        fig.update_traces(marker_color="#35d6c0")
        st.plotly_chart(style_chart(fig, 350), width="stretch")
    with right:
        st.markdown("#### Customer Segment Distribution")
        fig = px.pie(segments, names="segment", values="customers", hole=0.62)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(style_chart(fig, 350), width="stretch")

# ---------------- SALES INTELLIGENCE ----------------

elif page == "Sales & Revenue Intelligence":
    st.markdown('<div class="section-title">Sales & Revenue Intelligence</div>', unsafe_allow_html=True)

    start_month = st.selectbox("Select starting month", ["All months"] + monthly["purchase_month"].tolist())
    filtered = monthly.copy()
    if start_month != "All months":
        filtered = filtered[filtered["purchase_month"] >= start_month]

    total_revenue = filtered["item_revenue"].sum()
    total_orders = filtered["delivered_orders"].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Selected Period Revenue", money(total_revenue))
    c2.metric("Delivered Orders", f"{total_orders:,.0f}")
    c3.metric("Average Revenue / Order", money(total_revenue / total_orders if total_orders else 0))

    left, right = st.columns(2)
    with left:
        fig = px.line(
            filtered, x="purchase_month", y="item_revenue", markers=True,
            labels={"item_revenue": "Revenue (R$)", "purchase_month": "Month"}
        )
        fig.update_traces(line_color="#8b7cff", line_width=3)
        st.plotly_chart(style_chart(fig), width="stretch")
    with right:
        fig = px.bar(
            filtered, x="purchase_month", y="delivered_orders",
            labels={"delivered_orders": "Delivered Orders", "purchase_month": "Month"}
        )
        fig.update_traces(marker_color="#35d6c0")
        st.plotly_chart(style_chart(fig), width="stretch")
    st.markdown("#### Monthly Sales Data")
    st.dataframe(filtered, width="stretch", hide_index=True)

# ---------------- CATEGORY INTELLIGENCE ------------

elif page == "Product & Category Intelligence":
    st.markdown('<div class="section-title">Product & Category Intelligence</div>', unsafe_allow_html=True)

    top_n = st.slider("Number of categories to analyse", 5, 10, 10)
    metric = st.selectbox(
        "Rank categories by", ["item_revenue", "units_sold", "unique_orders"],
        format_func=lambda x: {
            "item_revenue": "Revenue", "units_sold": "Units Sold", "unique_orders": "Unique Orders"
        }[x]
    )
    top = categories.nlargest(top_n, metric).copy()
    c1, c2, c3 = st.columns(3)
    c1.metric("Categories Displayed", len(top))
    c2.metric("Revenue in Selection", money(top["item_revenue"].sum()))
    c3.metric("Units Sold", f"{top['units_sold'].sum():,.0f}")

    fig = px.bar(
        top.sort_values(metric), x=metric, y="product_category_name_english",
        orientation="h", color="item_revenue", hover_data=["units_sold", "unique_orders"],
        labels={
            "product_category_name_english": "Category", "item_revenue": "Revenue (R$)",
            "units_sold": "Units Sold", "unique_orders": "Unique Orders"
        }
    )
    st.plotly_chart(style_chart(fig, 480), width="stretch")
    st.markdown("#### Category Performance Dataset")
    st.dataframe(top, width="stretch", hide_index=True)

# ---------------- CUSTOMER INTELLIGENCE --------------


elif page == "Customer & RFM Intelligence":
    st.markdown(
        '<div class="section-title">Customer & RFM Intelligence</div>',
        unsafe_allow_html=True
    )

    report_dir = Path("reports") / "customer_intelligence"

    rfm = pd.read_csv(report_dir / "customer_rfm_segments.csv")
    churn = pd.read_csv(report_dir / "churn_risk_summary.csv")
    summary_df = pd.read_csv(report_dir / "customer_intelligence_summary.csv")

    summary = dict(zip(summary_df["Metric"], summary_df["Value"]))

    total_customers = int(float(summary["Unique customers analyzed"]))
    repeat_rate = float(summary["Repeat customer rate (%)"])
    total_revenue = float(summary["Total observed item revenue (R$)"])
    inactive_90 = int(float(summary["Customers inactive more than 90 days"]))

    st.markdown("#### Customer Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Unique Customers", f"{total_customers:,}")
    c2.metric("Repeat Customer Rate", f"{repeat_rate:.2f}%")
    c3.metric("Observed Revenue", f"R$ {total_revenue:,.2f}")
    c4.metric("Inactive > 90 Days", f"{inactive_90:,}")

    st.divider()
    st.markdown("#### RFM Segment Performance")

    left, right = st.columns(2)

    with left:
        fig = px.pie(
            rfm,
            names="rfm_segment",
            values="customers",
            hole=0.55,
            title="Customer Distribution by RFM Segment"
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(style_chart(fig), width="stretch")

    with right:
        fig = px.bar(
            rfm.sort_values("total_observed_revenue"),
            x="total_observed_revenue",
            y="rfm_segment",
            orientation="h",
            title="Revenue by RFM Segment",
            labels={
                "total_observed_revenue": "Observed Revenue (R$)",
                "rfm_segment": "RFM Segment"
            }
        )
        fig.update_traces(marker_color="#8b7cff")
        st.plotly_chart(style_chart(fig), width="stretch")

    st.dataframe(rfm, width="stretch", hide_index=True)

    st.divider()
    st.markdown("#### Customer Inactivity Risk")

    left, right = st.columns(2)

    with left:
        fig = px.pie(
            churn,
            names="inactivity_risk",
            values="customers",
            hole=0.55,
            title="Customers by Inactivity Group"
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(style_chart(fig), width="stretch")

    with right:
        fig = px.bar(
            churn.sort_values("customers"),
            x="customers",
            y="inactivity_risk",
            orientation="h",
            title="Customer Count by Inactivity Risk",
            labels={
                "customers": "Number of Customers",
                "inactivity_risk": "Inactivity Group"
            }
        )
        fig.update_traces(marker_color="#20c9b5")
        st.plotly_chart(style_chart(fig), width="stretch")

    st.markdown("#### Inactivity Risk Details")
    st.dataframe(churn, width="stretch", hide_index=True)

    st.info(
        "This analysis uses historical delivered-order data with a snapshot "
        "date of 2018-08-29. Inactivity groups are historical risk indicators, "
        "not verified present-day churn predictions or predictive customer lifetime value."
    )


# ---------------- BUSINESS INSIGHTS -----------------

elif page == "Business Insights":
    st.markdown('<div class="section-title">Business Insights & Recommendations</div>', unsafe_allow_html=True)
    st.caption("Findings and recommendations loaded from the project's prepared business insights report.")

    # Key indicators based on the existing prepared reports
    repeat_customers = get_kpi("Repeat Customers")
    unique_customers = get_kpi("Unique Customers")
    repeat_rate = repeat_customers / unique_customers * 100 if unique_customers else 0

    top_category = categories.nlargest(1, "item_revenue")
    top_units = categories.nlargest(1, "units_sold")
    top_segment = segments.nlargest(1, "total_item_revenue")

    a, b, c = st.columns(3)
    a.metric("Repeat Customer Rate", f"{repeat_rate:.2f}%")
    if not top_category.empty:
        a_name = top_category.iloc[0]["product_category_name_english"]
        a_value = top_category.iloc[0]["item_revenue"]
        b.metric("Top Revenue Category", str(a_name).replace("_", " ").title())
        b.caption(money(a_value))
    if not top_units.empty:
        u_name = top_units.iloc[0]["product_category_name_english"]
        u_value = top_units.iloc[0]["units_sold"]
        c.metric("Top Units Sold Category", str(u_name).replace("_", " ").title())
        c.caption(f"{u_value:,.0f} units")

    st.markdown("### Reported Business Findings")
    if not insights.empty and {"Area", "Finding", "Recommendation"}.issubset(insights.columns):
        for _, row in insights.iterrows():
            area = str(row["Area"]).strip() or "Business Insight"
            finding = str(row["Finding"]).strip()
            recommendation = str(row["Recommendation"]).strip()
            with st.container(border=True):
                st.markdown(f"**{area}**")
                if finding:
                    st.markdown(f"**Finding:** {finding}")
                if recommendation:
                    st.markdown(f"**Recommended action:** {recommendation}")
    else:
        st.warning(
            "The business insights report is missing or does not contain the expected "
            "Area, Finding and Recommendation columns."
        )

    # Explain unusually large percentage movements rather than presenting them as stable trends.
    growth_rows = insights[
        insights["Area"].astype(str).str.contains("growth|decline", case=False, na=False)
    ] if not insights.empty and "Area" in insights.columns else pd.DataFrame()

    if not growth_rows.empty:
        st.markdown("### Monthly Growth Interpretation")
        st.warning(
            "The prepared report flags unusually large monthly growth/decline percentages. "
            "These can be exaggerated when the comparison month has a very small revenue "
            "baseline or incomplete early-period activity. Treat these as investigation "
            "signals, not as evidence of a sustained growth rate. Check the underlying "
            "monthly revenue and delivered-order counts before making business decisions."
        )
        st.dataframe(
            growth_rows[["Area", "Finding", "Recommendation"]],
            width="stretch",
            hide_index=True
        )

    st.markdown("### Management Focus Areas")
    st.markdown("""
    - **Retention:** investigate repeat-purchase barriers and test measurable retention campaigns.
    - **Inventory planning:** compare category unit demand with item revenue before adjusting stock.
    - **Revenue monitoring:** review revenue together with delivered-order volume month by month.
    - **Commercial analysis:** investigate promotions, product mix and operational changes before attributing a revenue movement to a single cause.
    """)
    st.caption(
        "The findings above are read from business_insights_report.csv. "
        "Recommendations are analytical actions to investigate, not causal conclusions."
    )

# ---------------- FOOTER ----------------------------

st.divider()
st.markdown(
    "<center style='color:#8291b5;font-size:12px;'>"
    "RETAILIQ | ENTERPRISE BUSINESS INTELLIGENCE | "
    "Built with Python • Pandas • Streamlit • Plotly"
    "</center>",
    unsafe_allow_html=True
)
