import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from sklearn.metrics import roc_auc_score, precision_score, recall_score

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Campaign Intelligence Dashboard",
    layout="wide"
)

st.title("Campaign Intelligence Platform")

# ==================================================
# DATABASE CONNECTION
# ==================================================
engine = create_engine(
    "postgresql://admin:admin@postgres:5432/bankdb"
)

# ==================================================
# LOAD RAW DATA
# ==================================================
try:
    df = pd.read_sql("SELECT * FROM bank_marketing;", engine)
except Exception:
    st.error("Table 'bank_marketing' not found. Run ETL pipeline first.")
    st.stop()

df["target"] = df["y"].apply(lambda x: 1 if x == "yes" else 0)

# ==================================================
# LOAD SCORED DATA
# ==================================================
try:
    df_scored = pd.read_sql("SELECT * FROM bank_scored;", engine)
except Exception:
    st.warning("Table 'bank_scored' not found. Run scoring pipeline to enable full analysis.")
    st.stop()

df_scored["target"] = df_scored["y"].apply(lambda x: 1 if x == "yes" else 0)

# ==================================================
# SIDEBAR CONTROLS
# ==================================================
st.sidebar.header("Campaign Controls")

view_option = st.sidebar.radio(
    "Dataset View",
    ("Raw Data", "Cleaned Data")
)

threshold = st.sidebar.slider(
    "Lead Score Threshold",
    0, 100, 70
)

cost_per_call = st.sidebar.number_input(
    "Cost per Call ($)",
    value=5
)

revenue_per_conversion = st.sidebar.number_input(
    "Revenue per Conversion ($)",
    value=250
)

# ==================================================
# EXECUTIVE OVERVIEW
# ==================================================
st.subheader("Executive Overview")

total_leads = len(df_scored)
overall_conversion = df_scored["target"].mean()
avg_score = df_scored["lead_score"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Leads", f"{total_leads:,}")
col2.metric("Overall Conversion Rate", f"{overall_conversion:.2%}")
col3.metric("Average Lead Score", f"{avg_score:.0f}")

st.divider()

# ==================================================
# DATA CLEANING IMPACT
# ==================================================
st.subheader("Data Cleaning Impact")

total_records = len(df)

categorical_cols = [
    "job", "marital", "education", "default",
    "housing", "loan", "contact", "poutcome"
]

unknown_count = sum(
    (df[col] == "unknown").sum()
    for col in categorical_cols if col in df.columns
)

df_cleaned = df[df["duration"] > 0]
removed_records = total_records - len(df_cleaned)

col4, col5, col6 = st.columns(3)
col4.metric("Total Records", total_records)
col5.metric("Records Removed (duration = 0)", removed_records)
col6.metric("Unknown Categorical Values", unknown_count)

st.divider()

# ==================================================
# RAW VS CLEANED COMPARISON
# ==================================================
st.subheader("Raw vs Cleaned Comparison")

active_df = df if view_option == "Raw Data" else df_cleaned
baseline = active_df["target"].mean()

col7, col8 = st.columns(2)
col7.metric("Conversion Rate", f"{baseline:.2%}")
col8.metric("Active Dataset Size", len(active_df))

st.divider()

# ==================================================
# LEAD SCORE ANALYSIS
# ==================================================
st.subheader("Lead Score Analysis")

high_segment = df_scored[df_scored["lead_score"] >= threshold]
conversion_rate = (
    high_segment["target"].mean()
    if len(high_segment) > 0 else 0
)

col9, col10 = st.columns(2)
col9.metric("Leads Above Threshold", len(high_segment))
col10.metric("Conversion Rate (Selected Segment)", f"{conversion_rate:.2%}")

# Score Distribution
fig = px.histogram(
    df_scored,
    x="lead_score",
    nbins=20,
    title="Lead Score Distribution"
)

st.plotly_chart(fig, use_container_width=True)

# Segment Comparison
df_scored["score_category"] = pd.cut(
    df_scored["lead_score"],
    bins=[-1, 39, 69, 100],
    labels=["Low", "Medium", "High"]
)

segment = (
    df_scored
    .groupby("score_category")["target"]
    .mean()
    .reset_index()
)

fig2 = px.bar(
    segment,
    x="score_category",
    y="target",
    title="Conversion Rate by Score Segment"
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ==================================================
# CAMPAIGN IMPACT SIMULATION
# ==================================================
st.subheader("Campaign Profit Simulation")

calls_made = len(high_segment)
conversions = high_segment["target"].sum()

estimated_revenue = conversions * revenue_per_conversion
estimated_cost = calls_made * cost_per_call
estimated_profit = estimated_revenue - estimated_cost

col11, col12, col13 = st.columns(3)
col11.metric("Calls Made", f"{calls_made:,}")
col12.metric("Estimated Revenue", f"${estimated_revenue:,.0f}")
col13.metric("Estimated Profit", f"${estimated_profit:,.0f}")

st.divider()
# ==================================================
# MODEL PERFORMANCE METRICS
# ==================================================
st.subheader("Model Performance Metrics")

try:
    auc = roc_auc_score(df_scored["target"], df_scored["lead_score"])
    precision = precision_score(
        df_scored["target"],
        df_scored["lead_score"] >= threshold
    )
    recall = recall_score(
        df_scored["target"],
        df_scored["lead_score"] >= threshold
    )

    col14, col15, col16 = st.columns(3)
    col14.metric("AUC Score", f"{auc:.2f}")
    col15.metric("Precision", f"{precision:.2f}")
    col16.metric("Recall", f"{recall:.2f}")

except Exception:
    st.info("Model metrics unavailable.")

# ==================================================
# TARGET LEADS ABOVE THRESHOLD
# ==================================================
st.divider()
st.subheader("Targeted Leads (Above Threshold)")

if len(high_segment) > 0:
    sorted_segment = high_segment.sort_values(
        "lead_score",
        ascending=False
    )

    st.dataframe(sorted_segment, use_container_width=True)

    csv = sorted_segment.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Targeted Leads CSV",
        data=csv,
        file_name="targeted_leads.csv",
        mime="text/csv"
    )
else:
    st.info("No leads meet the selected threshold.")
