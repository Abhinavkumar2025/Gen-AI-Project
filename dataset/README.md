# RentGuard AI - Rental Application Dataset Documentation

## 1. Overview
This dataset contains fictional synthetic rental applications modeled to mirror standard residential tenancy evaluation processes. It was generated using controlled probabilistic distributions and domain-derived heuristics representing financial correlations (e.g. debt-to-income bounds, credit-risk clustering, and employment-tenancy ratios).

## 2. Feature Schema

| Feature Name | Data Type | Permitted Values / Range | Description |
| :--- | :--- | :--- | :--- |
| `applicant_id` | String | Format: `APP-XXXXX` | Unique applicant identifier |
| `monthly_income` | Float | $1,400.00 – $28,000.00 | Gross monthly income |
| `monthly_rent` | Float | $650.00 – $6,500.00 | Monthly target rent requested |
| `credit_score` | Integer | 300 – 850 | Standard credit bureau score |
| `employment_duration` | Float | 0.0 – 35.0 (years) | Continuous tenure at current or primary job |
| `previous_evictions` | Integer | 0 – 5 | Count of court-ordered tenancy evictions |
| `existing_loans` | Integer | 0 – 14 | Number of active installment or revolving loan obligations |
| `employment_status` | String | Full-time, Self-employed, Part-time, Retired, Unemployed | Applicant's current work classification |
| `rental_history_duration` | Float | 0.2 – 35.0 (years) | Verifiable duration of independent rental history |
| `previous_residences` | Integer | 1 – 10 | Count of distinct residential addresses in rental history |
| `is_anomaly` *(Benchmark only)* | Integer | 0 (Normal) or 1 (Anomalous) | Ground-truth label strictly reserved for testing & validation |
| `anomaly_type` *(Benchmark only)* | String | Categorical string | Typology of the injected statistical outlier |

> **Critical Notice**: The columns `is_anomaly` and `anomaly_type` are ground-truth labels used exclusively to benchmark and evaluate model performance (e.g., ROC-AUC, PR-AUC). **They are strictly excluded from the unsupervised Autoencoder training pipeline.**

---

## 3. Deliberately Injected Anomaly Typologies
In the synthetic dataset, approximately 8% of applications contain controlled anomalies:
1. **Income-Rent Inversion**: Unreasonable rent-to-income ratio (e.g., $1,800 income for a $4,200/mo unit).
2. **Credit-Eviction Discordance**: High credit scores (800+) paired with multiple recent evictions and high loan counts.
3. **Unemployed Luxury Rent**: Applicants with zero or near-zero income applying for premium properties.
4. **Employment-Tenancy Anachronisms**: Discrepancies between reported work tenure and rental duration (e.g., 30 years employment with 0.3 years rental history and 7 moves).
5. **Extreme Debt Burden**: Severe loan stacking (8–14 active loans) and depressed credit ratings.
6. **Fictitious Staggered Moves**: Excessive residential moves (8–10) compressed into a short rental window (e.g., under 18 months).

---

## 4. Assumptions & Limitations of Synthetic Data

### Assumptions:
1. **Stationary Distribution**: Real-world macroeconomic factors (e.g., regional inflation, housing market pinches, wage spikes) are treated as stationary.
2. **Feature Independence Bounds**: The generator models pairwise and conditional interactions (e.g., income and rent ratio), but real-world financial records have non-linear complexities not captured here.
3. **Equitable Representation**: Synthetic records are drawn from generic mathematical distributions without protected demographic attributes.

### Limitations:
1. **Synthetic vs. Real-World Accuracy**: Strong detection metrics (e.g., ROC-AUC > 0.95) on this synthetic dataset reflect the Autoencoder's ability to identify the mathematical patterns injected into this data. **This does not guarantee equivalent detection rates on real-world rental fraud or idiosyncratic human applications.**
2. **Never a Fraud Determinator**: Statistical reconstruction error measures how atypical an application is compared to the baseline normal training distribution. A high reconstruction error does NOT equate to fraudulent intent; it may represent non-traditional career paths, expats, or family guarantors.
3. **Human Review Requirement**: All high-reconstruction applications must undergo verified manual scrutiny by licensed leasing staff before any leasing decisions are rendered.
