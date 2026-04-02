
```markdown
# 🚀 Campaign Intelligence Optimization System

🔗 **Live Demo:** https://your-app.streamlit.app  
📊 AI-powered lead scoring & campaign optimization platform

---

## 📌 Overview

This project builds an end-to-end **campaign optimization system** that identifies high-conversion leads using data, machine learning, and business logic.

It combines:

- 🗄 SQL-based filtering  
- 🤖 Machine Learning (Logistic Regression)  
- 🎯 ML-based lead scoring (probability-driven)  
- 📊 Interactive SaaS dashboard (Streamlit)  

Using **41,188 telemarketing campaign records**, the system demonstrates how intelligent prioritization dramatically improves marketing efficiency.

---

## 🎯 Key Results

| Metric | Baseline | Optimized |
|--------|----------|-----------|
| Conversion Rate | 11.27% | **64.60%** |
| Efficiency Improvement | — | **+473%** |
| Model Accuracy | — | **~91%** |
| Model Precision | — | **~66%** |
| Precision (High-Score Leads) | — | **~75%** |
| Lead Reduction | — | **96.67%** |

---

## 🧠 How the System Works

### 1. 🧹 Data Cleaning & Preparation

A structured cleaning pipeline ensures reliable analysis:

- Converted `"unknown"` values to NULL  
- Removed non-actionable records (e.g., `duration = 0`)  
- Standardized categorical variables  
- Validated campaign, `pdays`, and `previous` features  
- Eliminated noisy or inconsistent data  

✅ Result: improved model stability and reliable downstream analytics

---

### 2. 🤖 Machine Learning Model

A **Logistic Regression model** predicts conversion likelihood:

- Target: `y` (yes/no)  
- One-hot encoding for categorical features  
- Standardization for numerical stability  

**Performance:**
- Accuracy: ~91%  
- Precision: ~66%  
- Recall: ~40%  

---

### 3. 🎯 ML-Based Lead Scoring

Instead of static rules, each lead is assigned:

**ML Score = Probability of Conversion (0–100)**

---

### 4. 📊 SaaS Dashboard

An interactive Streamlit dashboard allows users to:

- Filter leads by ML score, contact type, and campaign intensity  
- View conversion trends and insights  
- Identify high-performing segments  
- Export prioritized lead lists  
- Run scenario-based predictions  

---

## 💡 Business Impact

This system demonstrates:

- 🎯 High-intent lead prioritization  
- 💰 Reduced marketing cost  
- ⚡ Improved campaign efficiency  
- 📉 Trade-off between reach vs conversion  
- 📊 Data-driven decision-making  

---

## 🛠 Tech Stack

- Python  
- Pandas / NumPy  
- Scikit-learn  
- SQLAlchemy  
- SQLite / PostgreSQL  
- Streamlit  

---

## 🚀 How to Run Locally

```bash
pip install -r requirements.txt
python src/pipeline.py
streamlit run src/dashboard.py

```

```
