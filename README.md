# RetailIQ – E-Commerce Sales & Customer Intelligence Dashboard

An end-to-end E-Commerce Analytics and Business Intelligence project built using Python, Pandas, Plotly, and Streamlit.

RetailIQ transforms raw e-commerce transaction data into meaningful business insights through sales analytics, product performance analysis, customer segmentation, and inactivity risk analysis.

## Project Overview

RetailIQ is an interactive analytics dashboard developed using the Brazilian E-Commerce Public Dataset by Olist.

The project helps understand:

- Sales and revenue performance
- Monthly sales trends
- Product and category performance
- Customer purchasing behaviour
- Repeat customer rate
- RFM-based customer segmentation
- Customer inactivity risk
- Business recommendations based on historical data

## Technology Stack

- **Programming:** Python
- **Data Analysis:** Pandas, NumPy
- **Dashboard:** Streamlit
- **Visualization:** Plotly
- **Development Environment:** Jupyter Notebook, VS Code
- **Data Format:** CSV

## Dashboard Modules

### 1. Executive Command Center

Provides an overview of business performance through key performance indicators (KPIs).

### 2. Sales & Revenue Intelligence

Analyzes delivered orders, item revenue, average revenue per order, and monthly sales trends.

### 3. Product & Category Intelligence

Identifies top-performing product categories based on revenue, units sold, and order volume.

### 4. Customer & RFM Intelligence

Analyzes customer purchasing behaviour using Recency, Frequency, and Monetary (RFM) segmentation.

Includes customer inactivity groups:

- Active (0–30 days)
- At Risk (31–90 days)
- High Risk (91–180 days)
- Dormant (181+ days)

### 5. Business Insights & Recommendations

Presents data-driven findings and recommendations related to sales growth, product performance, and customer retention.

## Key Project Metrics

| Metric | Result |
|---|---:|
| Delivered Orders | 96,478 |
| Unique Customers | 93,358 |
| Delivered Item Revenue | R$13,221,498.11 |
| Average Item Revenue per Order | R$137.04 |
| Repeat Customers | 2,801 |
| Repeat Customer Rate | 3.00% |
| Product Categories Displayed | 10 |
| Monthly Sales Periods | 23 |

## Customer Intelligence

The customer intelligence engine generates:

- Customer-level metrics
- RFM segment summaries
- Inactivity risk summaries
- Customer intelligence summary
- Data validation report

The analysis uses customer unique identifiers and delivered-order history.

**Important:** Inactivity risk is a historical inactivity indicator based on the dataset snapshot, not a verified present-day churn prediction. Customer lifetime value is not presented as a predictive model.

## Project Structure

```text
RetailIQ/
│
├── app.py
├── dashboard_app.py
├── customer_intelligence.py
├── update_dashboard_customer_intelligence.py
├── RetailIQAnalysis.ipynb
│
├── data/
│   ├── raw/
│   └── processed/
│
├── scripts/
│   ├── clean_orders.py
│   ├── clean_products.py
│   └── data_audit.py
│
└── reports/
    ├── business_insights_report.csv
    ├── category_sales_summary.csv
    ├── column_quality_report.csv
    ├── customer_purchase_summary.csv
    ├── customer_rfm_segments.csv
    ├── dashboard_customer_segments.csv
    ├── dashboard_kpis.csv
    ├── dashboard_monthly_sales.csv
    ├── dashboard_top_categories.csv
    ├── dataset_summary.csv
    ├── monthly_sales_summary.csv
    │
    └── customer_intelligence/
        ├── customer_metrics.csv
        ├── customer_rfm_segments.csv
        ├── churn_risk_summary.csv
        ├── customer_intelligence_summary.csv
        └── validation_report.csv
```

## How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/sakshilokhande7576-oss/RetailIQ.git
cd RetailIQ
```

### 2. Install dependencies

```bash
pip install pandas numpy plotly streamlit
```

### 3. Launch the dashboard

```bash
streamlit run dashboard_app.py
```

The dashboard will open in your browser, usually at:

```text
http://localhost:8501
```

## Data Source

Brazilian E-Commerce Public Dataset by Olist.

The dataset contains historical Brazilian e-commerce orders, customers, products, and transaction information.

## Validation & Testing

The project includes:

- Python compilation checks
- Customer-level data validation
- RFM customer count reconciliation
- Inactivity risk customer count reconciliation
- Revenue reconciliation
- Dashboard KPI cross-checks
- Monthly sales total validation

## Limitations

- The analysis is based on historical data.
- Customer inactivity groups are descriptive indicators.
- The dashboard does not claim to predict future customer churn.
- Results depend on the available dataset and its historical coverage.

## Future Enhancements

- Predictive customer churn modelling
- Advanced sales forecasting
- Customer lifetime value modelling
- More interactive business filters
- Automated data quality monitoring

## 📸 Dashboard Screenshots

### 1. Executive Command Center

<img width="1920" height="1080" alt="Screenshot 2026-10-31 152733" src="https://github.com/user-attachments/assets/ae5bb38b-e711-4ad7-9ba1-37e23503cdf0" />


### 2. Sales & Revenue Intelligence

<img width="1920" height="1080" alt="Screenshot 2026-10-31 152948" src="https://github.com/user-attachments/assets/3163cac4-8117-4b73-a16d-f877f1b0adb2" />


### 3. Product & Category Intelligence

<img width="1920" height="1080" alt="Screenshot 2026-10-31 153053" src="https://github.com/user-attachments/assets/da003151-69a7-4002-938c-7560863095b9" />



### 4. Customer & RFM Intelligence

<img width="1920" height="1080" alt="Screenshot 2026-10-31 153136" src="https://github.com/user-attachments/assets/21b0009f-d030-4886-8efc-c329dbd7a79e" />


### 5. Business Insights & Recommendations

<img width="1920" height="1080" alt="Screenshot 2026-10-31 153210" src="https://github.com/user-attachments/assets/cf3741b5-42a2-46aa-88c3-593865dca589" /> 




## Author

**Sakshi Lokhande**

GitHub: https://github.com/sakshilokhande7576-oss

LinkedIn: https://www.linkedin.com/in/sakshi-lokhande-29b77825b

---

*RetailIQ – Turning E-Commerce Data into Business Intelligence.*
