import pandas as pd
from sqlalchemy import create_engine, text

# ==========================
# DATABASE SETUP
# ==========================

engine = create_engine("sqlite:///bank.db")

# Load dataset
df = pd.read_csv("data/bank-additional-full.csv")

# Clean column names
df.columns = df.columns.str.strip().str.replace('"', '').str.lower()

print("Columns:", df.columns.tolist())

# ==========================
# MACHINE LEARNING
# ==========================

print("\nRunning Logistic Regression Model...")

# Target encoding
df["target"] = df["y"].apply(lambda x: 1 if x == "yes" else 0)

# Features
X = df.drop(columns=["y", "target"])
y = df["target"]

# One-hot encoding
X = pd.get_dummies(X, drop_first=True)

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Scaling
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Model
model = LogisticRegression(max_iter=2000, solver="liblinear")
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)

print(f"Model Accuracy: {accuracy:.4f}")
print(f"Model Precision: {precision:.4f}")
print(f"Model Recall: {recall:.4f}")

# ==========================
# ML-BASED SCORING
# ==========================

print("\nGenerating ML-based lead scores...")

# Transform full dataset
X_full = scaler.transform(X)

# Predict probability
proba = model.predict_proba(X_full)[:, 1]

# Add ML score (0–100)
df["ml_score"] = (proba * 100).round(2)

# Save to database
df.to_sql("bank_scored", engine, if_exists="replace", index=False)

print("ML-based scoring saved to database")

# ==========================
# SQL ANALYTICS
# ==========================

with engine.begin() as conn:

    # Baseline conversion rate
    baseline_query = """
    SELECT 
        SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS conversion_rate
    FROM bank_scored;
    """
    baseline = conn.execute(text(baseline_query)).scalar()
    print(f"\nBaseline Conversion Rate: {baseline:.4f}")

    # Drop filtered table
    conn.execute(text("DROP TABLE IF EXISTS bank_filtered;"))

    # Create filtered table
    filter_query = """
    CREATE TABLE bank_filtered AS
    SELECT *
    FROM bank_scored
    WHERE duration > 0
    AND campaign <= 5
    AND "default" != 'yes'
    AND contact = 'cellular'
    AND (poutcome = 'success' OR previous > 0)
    AND pdays < 999;
    """
    conn.execute(text(filter_query))

    # Filtered conversion rate
    filtered_query = """
    SELECT 
        SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS conversion_rate
    FROM bank_filtered;
    """
    filtered = conn.execute(text(filtered_query)).scalar()
    print(f"Filtered Conversion Rate: {filtered:.4f}")

    # Improvement
    improvement = ((filtered - baseline) / baseline) * 100
    print(f"Efficiency Improvement: {improvement:.2f}%")

    # ==========================
    # ML SCORE PERFORMANCE
    # ==========================

    score_analysis = """
    SELECT 
        CASE 
            WHEN ml_score >= 70 THEN 'High'
            WHEN ml_score >= 40 THEN 'Medium'
            ELSE 'Low'
        END AS score_category,
        COUNT(*) AS total_leads,
        SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS conversion_rate
    FROM bank_scored
    GROUP BY score_category
    ORDER BY conversion_rate DESC;
    """

    result = conn.execute(text(score_analysis)).fetchall()

    print("\nML Score Performance:")
    for row in result:
        print(row)

    # Lead counts
    count_original = conn.execute(
        text("SELECT COUNT(*) FROM bank_scored;")
    ).scalar()

    count_filtered = conn.execute(
        text("SELECT COUNT(*) FROM bank_filtered;")
    ).scalar()

    print(f"\nOriginal Lead Count: {count_original}")
    print(f"Filtered Lead Count: {count_filtered}")
    print(
        f"Lead Reduction: {((count_original - count_filtered) / count_original) * 100:.2f}%"
    )

# ==========================
# HIGH-SCORE EVALUATION
# ==========================

high_score_df = df[df["ml_score"] >= 70]

X_high = pd.get_dummies(
    high_score_df.drop(columns=["y", "target"]),
    drop_first=True
)

# Align columns
X_high = X_high.reindex(columns=X.columns, fill_value=0)
X_high = scaler.transform(X_high)

y_high = high_score_df["target"]

y_high_pred = model.predict(X_high)

high_precision = precision_score(y_high, y_high_pred)

print(f"\nPrecision on High-Score Leads: {high_precision:.4f}")