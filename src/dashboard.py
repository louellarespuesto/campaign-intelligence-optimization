import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(page_title="Lead Optimization SaaS", layout="wide")

# ==========================
# LOAD DATA
# ==========================

engine = create_engine("sqlite:///bank.db")
df = pd.read_sql("SELECT * FROM bank_scored", engine)

# Feature engineering
df["converted"] = df["y"].apply(lambda x: 1 if x == "yes" else 0)

# ==========================
# SIDEBAR FILTERS
# ==========================

st.sidebar.title("🎯 Client Filters")

contact = st.sidebar.multiselect(
    "Contact Type",
    options=df["contact"].unique(),
    default=df["contact"].unique()
)

score = st.sidebar.slider("Minimum ML Score", 0, 100, 0)

campaign = st.sidebar.slider(
    "Max Campaign Contacts",
    int(df["campaign"].min()),
    int(df["campaign"].max()),
    int(df["campaign"].max())
)

# Apply filters
filtered_df = df[
    (df["contact"].isin(contact)) &
    (df["ml_score"] >= score) &
    (df["campaign"] <= campaign)
]

# Sort by best leads
filtered_df = filtered_df.sort_values(by="ml_score", ascending=False)

# ==========================
# HEADER
# ==========================

st.title("🚀 Lead Campaign Optimization SaaS Dashboard")
st.caption("AI-powered lead prioritization & conversion analytics")

# ==========================
# KPI SECTION
# ==========================

total = len(filtered_df)
conversion = filtered_df["converted"].mean()
high_score = (filtered_df["ml_score"] >= 70).mean()

col1, col2, col3 = st.columns(3)

col1.metric("📊 Total Leads", total)
col2.metric("🎯 Conversion Rate", f"{conversion:.2%}")
col3.metric("🔥 High-Quality Leads", f"{high_score:.2%}")

# ==========================
# INSIGHTS
# ==========================

st.subheader("💡 Key Insights")

if conversion > 0.5:
    st.success("High conversion segment detected — prioritize this group.")
elif conversion > 0.2:
    st.warning("Moderate conversion — optimize targeting.")
else:
    st.error("Low conversion — reconsider campaign strategy.")

# ==========================
# CHARTS
# ==========================

st.subheader("📈 Conversion by ML Score")

df["score_category"] = pd.cut(
    df["ml_score"],
    bins=[0, 40, 70, 100],
    labels=["Low", "Medium", "High"]
)

conversion_chart = df.groupby("score_category")["converted"].mean()

st.bar_chart(conversion_chart)

# ==========================
# CAMPAIGN EFFECT
# ==========================

st.subheader("📊 Campaign Contact Impact")

campaign_chart = df.groupby("campaign")["converted"].mean()

st.line_chart(campaign_chart)

# ==========================
# TOP LEADS SECTION
# ==========================

st.subheader("🏆 Top 100 High-Quality Leads")

top_leads = filtered_df.head(100)

st.dataframe(top_leads)

# ==========================
# DOWNLOAD FEATURE
# ==========================

st.download_button(
    "⬇️ Download Filtered Leads",
    filtered_df.to_csv(index=False),
    file_name="filtered_leads.csv"
)

# ==========================
# PREDICTION TOOL (INFO MODE)
# ==========================

st.subheader("🤖 Lead Prediction Tool")

st.info("This demo uses ML scoring in the backend.")

if "prediction_results" not in st.session_state:
    st.session_state.prediction_results = []

with st.form("prediction_form"):
    campaign_input = st.slider("Campaign Contacts", 1, 10, 3)
    previous_input = st.slider("Previous Contacts", 0, 10, 0)
    poutcome_input = st.selectbox("Previous Outcome", ["success", "failure", "unknown"])

    submitted = st.form_submit_button("Estimate Lead Quality")

    if submitted:
        score = 0
        if poutcome_input == "success":
            score += 30
        if previous_input > 0:
            score += 15
        if campaign_input <= 3:
            score += 15

        # Determine category
        if score >= 70:
            category = "High"
        elif score >= 40:
            category = "Medium"
        else:
            category = "Low"

        # Save result
        st.session_state.prediction_results.append({
            "Campaign": campaign_input,
            "Previous": previous_input,
            "Outcome": poutcome_input,
            "Score": score,
            "Category": category
        })

# ==========================
# DISPLAY TABLE
# ==========================

st.subheader("📊 Prediction Results")

# Ensure session state exists
if "prediction_results" not in st.session_state:
    st.session_state.prediction_results = []

if st.session_state.prediction_results:
    results_df = pd.DataFrame(st.session_state.prediction_results)
    st.dataframe(results_df)

    # Download option (optional but nice)
    st.download_button(
        "⬇️ Download Results",
        results_df.to_csv(index=False),
        file_name="prediction_results.csv"
    )

    # Clear button
    if st.button("🗑 Clear Results"):
        st.session_state.prediction_results = []
        st.rerun()

else:
    st.info("No predictions yet. Submit a prediction above.")