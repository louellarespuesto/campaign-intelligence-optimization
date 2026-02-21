import pandas as pd
from sqlalchemy import create_engine, text

# Connect to PostgreSQL (Docker service name)
engine = create_engine("postgresql://admin:admin@postgres:5432/bankdb")

with engine.begin() as conn:
    
    # Baseline conversion rate
    baseline_query = """
    SELECT 
        COUNT(*) FILTER (WHERE y = 'yes') * 1.0 / COUNT(*) AS conversion_rate
    FROM bank_marketing;
    """
    baseline = conn.execute(text(baseline_query)).scalar()
    print(f"Baseline Conversion Rate: {baseline:.4f}")

    # Create filtered table
    conn.execute(text("DROP TABLE IF EXISTS bank_filtered;"))

    filter_query = """
    CREATE TABLE bank_filtered AS
    SELECT *
    FROM bank_marketing
    WHERE duration > 0
    AND campaign <= 5
    AND credit_default IS DISTINCT FROM 'yes'
    AND contact = 'cellular'
    AND (poutcome = 'success' OR previous > 0)
    AND pdays < 999;
    """
    conn.execute(text(filter_query))

    # Filtered conversion rate
    filtered_query = """
    SELECT 
        COUNT(*) FILTER (WHERE y = 'yes') * 1.0 / COUNT(*) AS conversion_rate
    FROM bank_filtered;
    """
    filtered = conn.execute(text(filtered_query)).scalar()
    print(f"Filtered Conversion Rate: {filtered:.4f}")

    improvement = ((filtered - baseline) / baseline) * 100
    print(f"Efficiency Improvement: {improvement:.2f}%")

    # Create scoring table
    conn.execute(text("DROP TABLE IF EXISTS bank_scored;"))

    scoring_query = """
    CREATE TABLE bank_scored AS
    SELECT *,
        (
            CASE WHEN poutcome = 'success' THEN 30 ELSE 0 END +
            CASE WHEN previous > 0 THEN 15 ELSE 0 END +
            CASE WHEN contact = 'cellular' THEN 15 ELSE 0 END +
            CASE WHEN campaign <= 3 THEN 15 ELSE 0 END +
            CASE WHEN pdays < 30 THEN 10 ELSE 0 END +
            CASE WHEN credit_default IS DISTINCT FROM 'yes' THEN 15 ELSE 0 END
        ) AS lead_score
    FROM bank_marketing;
    """
    conn.execute(text(scoring_query))

    # Score performance analysis
    score_analysis = """
    SELECT 
        CASE 
            WHEN lead_score >= 70 THEN 'High'
            WHEN lead_score >= 40 THEN 'Medium'
            ELSE 'Low'
        END AS score_category,
        COUNT(*) AS total_leads,
        COUNT(*) FILTER (WHERE y = 'yes') * 1.0 / COUNT(*) AS conversion_rate
    FROM bank_scored
    GROUP BY score_category
    ORDER BY conversion_rate DESC;
    """

    result = conn.execute(text(score_analysis)).fetchall()

    print("\nLead Score Performance:")
    for row in result:
        print(row)

    # Lead counts
    count_original = conn.execute(
        text("SELECT COUNT(*) FROM bank_marketing;")
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
# MACHINE LEARNING SECTION
# ==========================

print("\nRunning Logistic Regression Model...")

df = pd.read_sql("SELECT * FROM bank_scored;", engine)

df["target"] = df["y"].apply(lambda x: 1 if x == "yes" else 0)

X = df.drop(columns=["y", "target"])
y = df["target"]

X = pd.get_dummies(X, drop_first=True)

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.preprocessing import StandardScaler

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Scale numeric features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = LogisticRegression(max_iter=2000, solver="liblinear")
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)

print(f"Model Accuracy: {accuracy:.4f}")
print(f"Model Precision: {precision:.4f}")
print(f"Model Recall: {recall:.4f}")

# Evaluate high-score leads
high_score_df = df[df["lead_score"] >= 70]

X_high = pd.get_dummies(
    high_score_df.drop(columns=["y", "target"]),
    drop_first=True
)

X_high = X_high.reindex(columns=X.columns, fill_value=0)
X_high = scaler.transform(X_high)

y_high = high_score_df["target"]

y_high_pred = model.predict(X_high)

high_precision = precision_score(y_high, y_high_pred)

print(f"\nPrecision on High-Score Leads: {high_precision:.4f}")