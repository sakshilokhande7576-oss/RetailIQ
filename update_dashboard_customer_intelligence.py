
from pathlib import Path
import shutil

base = Path(__file__).resolve().parent
dashboard = base / "dashboard_app.py"
backup = base / "dashboard_app_before_customer_upgrade.py"

if not dashboard.exists():
    raise FileNotFoundError("dashboard_app.py not found.")

if backup.exists():
    raise FileExistsError(
        "Safety backup already exists. No files were changed."
    )

content = dashboard.read_text(encoding="utf-8")

start_marker = 'elif page == "Customer & RFM Intelligence":'
end_marker = "# ---------------- BUSINESS INSIGHTS"

if start_marker not in content or end_marker not in content:
    raise ValueError(
        "Customer section markers not found. Dashboard was not changed."
    )

start = content.index(start_marker)
end = content.index(end_marker, start)

new_section = '''
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
        st.plotly_chart(style_chart(fig), use_container_width=True)

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
        st.plotly_chart(style_chart(fig), use_container_width=True)

    st.dataframe(rfm, use_container_width=True, hide_index=True)

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
        st.plotly_chart(style_chart(fig), use_container_width=True)

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
        st.plotly_chart(style_chart(fig), use_container_width=True)

    st.markdown("#### Inactivity Risk Details")
    st.dataframe(churn, use_container_width=True, hide_index=True)

    st.info(
        "This analysis uses historical delivered-order data with a snapshot "
        "date of 2018-08-29. Inactivity groups are historical risk indicators, "
        "not verified present-day churn predictions or predictive customer lifetime value."
    )
'''

# Create a safety backup before making any dashboard change.
shutil.copy2(dashboard, backup)

updated = content[:start] + new_section + "\n\n" + content[end:]

dashboard.write_text(updated, encoding="utf-8")

print("SUCCESS: Customer Intelligence dashboard section updated.")
print("Backup saved as:", backup.name)
print("Next: run the Streamlit dashboard and verify the page.")
