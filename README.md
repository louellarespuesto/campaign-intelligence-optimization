# Campaign Intelligence Optimization System

## 📌 Overview

This project develops a hybrid campaign optimization framework combining:

- SQL-based filtering
- Rule-based lead scoring
- Logistic regression modeling
- Performance validation across segments

Using 41,188 telemarketing campaign records, the system demonstrates how intelligent prioritization improves marketing efficiency.

---

## 🧹 Data Cleaning & Preparation

A structured data cleaning process was implemented before any filtering or modeling to ensure analytical reliability.

### Cleaning Steps Performed

- Converted "unknown" categorical values to NULL for proper handling
- Removed non-actionable records (e.g., duration = 0)
- Validated credit default and contact status fields
- Standardized categorical variables
- Verified numerical integrity of campaign, pdays, and previous features
- Eliminated inconsistent and noisy records

### Impact of Cleaning

- Reduced noise in categorical variables
- Improved model convergence stability
- Prevented bias from invalid or non-contacted records
- Ensured reproducibility of SQL-based transformations

This cleaning layer served as the foundation for subsequent filtering, scoring, and machine learning optimization.

---


## 📊 Key Results

| Metric | Baseline | Optimized |
|--------|----------|-----------|
| Conversion Rate | 11.27% | 64.60% (Filtered Segment) |
| High Score Conversion | 64.16% |
| Model Precision | 66.67% |
| Precision on High Score Leads | 75.04% |
| Lead Reduction (Aggressive Filter) | 96.67% |

---

## 🔍 Lead Segmentation Performance

- **High Score Leads (3.6%)** → 64% conversion
- **Medium Score Leads (51%)** → 12.6% conversion
- **Low Score Leads (45%)** → 5.4% conversion

---

## 🤖 Machine Learning

Logistic Regression model:

- Accuracy: ~91%
- Precision: ~66%
- Recall: ~40%
- Precision improves to 75% within high-score segment

---

## 🧠 Business Impact

Demonstrates:

- Trade-off between reach and efficiency
- High-intent lead prioritization
- Hybrid rule-based + ML validation
- Campaign resource optimization

---

## 🛠 Tech Stack

- Python
- PostgreSQL
- SQLAlchemy
- Scikit-learn
- Docker
- DBeaver

---

## 🚀 How to Run

```bash
docker compose up --build
docker exec -it bank_app bash
python3 src/pipeline.py