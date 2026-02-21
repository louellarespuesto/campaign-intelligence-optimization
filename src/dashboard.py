import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

st.set_page_config(page_title="Campaign Intelligence Dashboard", layout="wide")

st.title("📊 Campaign Intelligence Dashboard")

engine = create_engine("postgresql://admin:admin@postgres:5432/bankdb")

# Load full dataset
df = pd.read_sql("SELECT * FROM bank_marketing;", engine)

df["target"] = df["y"].apply(lambda x: 1 if x == "yes" else 0)

# ==========================
# DATA CLEANING SECTION
# ==========================

st.header("🧹 Data Cleaning Impact")

total_records = len(df)

# Count unknown values in categorical columns
categorical_cols = ["job", "marital", "education", "default",
                    "housing", "loan", "contact", "poutcome"]

unknown_count = 0
for col in categorical_cols:
    unknown_count += (df[col] == "unknown").sum()

# Cleaned dataset (example rule)
df_cleaned = df[df["duration"] > 0]

removed_records = total_records - len(df_cleaned)
cleaning_rate = (removed_records / total_records) * 100

col1, col2, col3 = st.columns(3)
col1.metric("Total Records", total_records)
col2.metric("Records Removed (duration=0)", removed_records)
col3.metric("Unknown Categorical Values", unknown_count)

st.markdown("---")

# ==========================
# RAW vs CLEANED TOGGLE
# ==========================

st.header("📈 Raw vs Cleaned Comparison")

view_option = st.radio(
    "Select Dataset View",
    ("Raw Data", "Cleaned Data")
)

if view_option == "Raw Data":
    active_df = df
else:
    active_df = df_cleaned

baseline = active_df["target"].mean()

col4, col5 = st.columns(2)
col4.metric("Conversion Rate", f"{baseline:.2%}")
col5.metric("Active Dataset Size", len(active_df))

# ==========================
# SCORE ANALYSIS (Cleaned)
# ==========================

st.header("🎯 Lead Score Analysis (Cleaned Data)")

# Load scored table
df_scored = pd.read_sql("SELECT * FROM bank_scored;", engine)
df_scored["target"] = df_scored["y"].apply(lambda x: 1 if x == "yes" else 0)

threshold = st.slider("Select Lead Score Threshold", 0, 100, 70)

high_segment = df_scored[df_scored["lead_score"] >= threshold]

conversion_rate = high_segment["target"].mean() if len(high_segment) > 0 else 0

col6, col7 = st.columns(2)
col6.metric("Leads Above Threshold", len(high_segment))
col7.metric("Conversion Above Threshold", f"{conversion_rate:.2%}")

# Score distribution
fig = px.histogram(df_scored, x="lead_score", nbins=20)
st.plotly_chart(fig, use_container_width=True)

# Segment comparison
df_scored["score_category"] = pd.cut(
    df_scored["lead_score"],
    bins=[-1, 39, 69, 100],
    labels=["Low", "Medium", "High"]
)

segment = df_scored.groupby("score_category")["target"].mean().reset_index()

fig2 = px.bar(segment, x="score_category", y="target")
st.plotly_chart(fig2, use_container_width=True)