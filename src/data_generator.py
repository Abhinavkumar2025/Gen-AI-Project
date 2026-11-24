"""RentGuard AI - Synthetic Rental Application Dataset Generator

Generates realistic rental application data with standard financial correlations
and deliberately injected anomaly clusters for anomaly detection benchmarking.
"""

import os
import numpy as np
import pandas as pd


def generate_normal_applications(n_samples: int, seed: int = 42) -> pd.DataFrame:
    """Generate representative normal rental applications with realistic correlations."""
    np.random.seed(seed)
    
    # 1. Employment Status distribution
    employment_choices = ["Full-time", "Self-employed", "Part-time", "Retired", "Unemployed"]
    employment_probs = [0.72, 0.15, 0.09, 0.03, 0.01]
    employment_status = np.random.choice(employment_choices, size=n_samples, p=employment_probs)
    
    # 2. Monthly Income based on employment status
    income = np.zeros(n_samples)
    for i, status in enumerate(employment_status):
        if status == "Full-time":
            inc = np.random.lognormal(mean=8.5, sigma=0.45)  # median ~$4,900
        elif status == "Self-employed":
            inc = np.random.lognormal(mean=8.7, sigma=0.55)  # median ~$6,000, higher variance
        elif status == "Part-time":
            inc = np.random.lognormal(mean=7.9, sigma=0.35)  # median ~$2,700
        elif status == "Retired":
            inc = np.random.lognormal(mean=8.2, sigma=0.35)  # median ~$3,600
        else:  # Unemployed
            inc = np.random.lognormal(mean=7.2, sigma=0.30)  # median ~$1,350
        income[i] = max(1400.0, min(inc, 28000.0))
    
    # 3. Monthly Rent realistically bounded by rent-to-income ratio (typically 20% to 35%)
    rent_to_income_ratio = np.random.beta(a=4, b=10, size=n_samples) * 0.28 + 0.18  # 0.20 - 0.38
    monthly_rent = income * rent_to_income_ratio
    # Clip rent to standard realistic market range
    monthly_rent = np.clip(monthly_rent, 650.0, 6500.0)
    
    # 4. Credit Score (300-850) correlated with income and low default risk
    # Standard distribution peaked around 685
    base_credit = np.random.normal(loc=685, scale=55, size=n_samples)
    income_boost = np.clip((income - 5000) / 400, -35, 45)
    credit_score = np.clip(np.round(base_credit + income_boost), 550, 840).astype(int)
    
    # 5. Employment Duration (years)
    emp_duration = np.zeros(n_samples)
    for i, status in enumerate(employment_status):
        if status == "Retired":
            emp_duration[i] = np.random.uniform(20.0, 40.0)
        elif status == "Unemployed":
            emp_duration[i] = np.random.uniform(0.0, 0.8)
        else:
            # Lognormal distribution of job tenure, average ~4.2 years
            tenure = np.random.lognormal(mean=1.2, sigma=0.7)
            emp_duration[i] = np.clip(tenure, 0.2, 35.0)
    
    # 6. Previous Evictions: vast majority 0, very small fraction 1 in normal pool
    eviction_choices = [0, 1]
    eviction_probs = [0.985, 0.015]
    previous_evictions = np.random.choice(eviction_choices, size=n_samples, p=eviction_probs)
    
    # 7. Existing Loans: discrete distribution (0 to 5)
    existing_loans = np.random.poisson(lam=1.4, size=n_samples)
    existing_loans = np.clip(existing_loans, 0, 5)
    
    # 8. Rental History Duration (years)
    # Correlates with employment duration and age
    rental_history = emp_duration * np.random.uniform(0.8, 1.4, size=n_samples) + np.random.uniform(1.0, 4.0, size=n_samples)
    rental_history_duration = np.clip(rental_history, 0.5, 35.0)
    
    # 9. Previous Residences: counts typically 1 to 4 in a normal tenure
    previous_residences = np.clip(np.round(1 + rental_history_duration / np.random.uniform(2.5, 4.5, size=n_samples)), 1, 5).astype(int)
    
    df = pd.DataFrame({
        "monthly_income": np.round(income, 2),
        "monthly_rent": np.round(monthly_rent, 2),
        "credit_score": credit_score,
        "employment_duration": np.round(emp_duration, 1),
        "previous_evictions": previous_evictions,
        "existing_loans": existing_loans,
        "employment_status": employment_status,
        "rental_history_duration": np.round(rental_history_duration, 1),
        "previous_residences": previous_residences,
        "is_anomaly": 0,
        "anomaly_type": "None"
    })
    return df


def generate_anomalous_applications(n_samples: int, seed: int = 101) -> pd.DataFrame:
    """Generate deliberate anomalous rental applications representing distinct outlier typologies."""
    np.random.seed(seed)
    
    records = []
    anomaly_categories = [
        "Income_Rent_Inversion",
        "Credit_Eviction_Discordance",
        "Unemployed_Luxury_Rent",
        "Employment_Tenancy_Anachronism",
        "Extreme_Debt_Burden",
        "Fictitious_Staggered_Moves"
    ]
    
    for _ in range(n_samples):
        cat = np.random.choice(anomaly_categories)
        
        if cat == "Income_Rent_Inversion":
            # Rent exceeds or closely rivals income (impossible/unsustainable DTI)
            income = float(np.round(np.random.uniform(1400, 2400), 2))
            rent = float(np.round(np.random.uniform(2800, 4800), 2))
            credit = int(np.random.randint(480, 640))
            emp_dur = float(np.round(np.random.uniform(0.5, 3.0), 1))
            evictions = int(np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1]))
            loans = int(np.random.randint(2, 6))
            status = np.random.choice(["Part-time", "Full-time"])
            rent_hist = float(np.round(np.random.uniform(1.0, 5.0), 1))
            prev_res = int(np.random.randint(2, 5))
            
        elif cat == "Credit_Eviction_Discordance":
            # Paradoxically elite credit score (790-840) despite multiple recent evictions & high loans
            income = float(np.round(np.random.uniform(4500, 8500), 2))
            rent = float(np.round(income * np.random.uniform(0.25, 0.35), 2))
            credit = int(np.random.randint(785, 845))
            emp_dur = float(np.round(np.random.uniform(2.0, 7.0), 1))
            evictions = int(np.random.randint(2, 5))  # Highly unusual with 800+ credit
            loans = int(np.random.randint(5, 9))
            status = "Full-time"
            rent_hist = float(np.round(np.random.uniform(3.0, 8.0), 1))
            prev_res = int(np.random.randint(3, 6))
            
        elif cat == "Unemployed_Luxury_Rent":
            # Unemployed with negligible income applying for high-tier rental
            income = float(np.round(np.random.uniform(300, 1200), 2))
            rent = float(np.round(np.random.uniform(3200, 6000), 2))
            credit = int(np.random.randint(420, 580))
            emp_dur = 0.0
            evictions = int(np.random.choice([0, 1, 2], p=[0.5, 0.3, 0.2]))
            loans = int(np.random.randint(1, 5))
            status = "Unemployed"
            rent_hist = float(np.round(np.random.uniform(0.5, 3.0), 1))
            prev_res = int(np.random.randint(2, 5))
            
        elif cat == "Employment_Tenancy_Anachronism":
            # Implausible tenure-to-history ratio (e.g., 28 years employment with 0.4 yrs rental history and 6 moves)
            income = float(np.round(np.random.uniform(6000, 14000), 2))
            rent = float(np.round(np.random.uniform(1800, 3200), 2))
            credit = int(np.random.randint(620, 750))
            emp_dur = float(np.round(np.random.uniform(24.0, 35.0), 1))
            evictions = 0
            loans = int(np.random.randint(1, 3))
            status = "Full-time"
            rent_hist = float(np.round(np.random.uniform(0.2, 0.8), 1))  # Incompatible with 30 yrs employment
            prev_res = int(np.random.randint(6, 9))
            
        elif cat == "Extreme_Debt_Burden":
            # Severe loan stacking (8 to 14 open loans) with depressed credit and low employment
            income = float(np.round(np.random.uniform(2200, 4200), 2))
            rent = float(np.round(np.random.uniform(1400, 2600), 2))
            credit = int(np.random.randint(380, 520))
            emp_dur = float(np.round(np.random.uniform(0.2, 1.5), 1))
            evictions = int(np.random.randint(1, 4))
            loans = int(np.random.randint(8, 14))  # Outlier debt
            status = np.random.choice(["Full-time", "Part-time"])
            rent_hist = float(np.round(np.random.uniform(1.0, 4.0), 1))
            prev_res = int(np.random.randint(3, 7))
            
        else:  # Fictitious_Staggered_Moves
            # Unusually high turnover rate: 8-10 previous residences within 1.5 years rental history
            income = float(np.round(np.random.uniform(3000, 6500), 2))
            rent = float(np.round(np.random.uniform(1200, 2200), 2))
            credit = int(np.random.randint(530, 680))
            emp_dur = float(np.round(np.random.uniform(1.0, 4.0), 1))
            evictions = int(np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1]))
            loans = int(np.random.randint(1, 4))
            status = "Full-time"
            rent_hist = float(np.round(np.random.uniform(1.0, 2.0), 1))
            prev_res = int(np.random.randint(7, 10))  # Impossible move density
            
        records.append({
            "monthly_income": income,
            "monthly_rent": rent,
            "credit_score": credit,
            "employment_duration": emp_dur,
            "previous_evictions": evictions,
            "existing_loans": loans,
            "employment_status": status,
            "rental_history_duration": rent_hist,
            "previous_residences": prev_res,
            "is_anomaly": 1,
            "anomaly_type": cat
        })
        
    return pd.DataFrame(records)


def create_rental_dataset(
    total_samples: int = 8000,
    anomaly_rate: float = 0.08,
    output_path: str = "dataset/rental_applications.csv",
    seed: int = 42
) -> pd.DataFrame:
    """
    Generate synthetic dataset, format applicant IDs, and save to disk.
    
    Returns:
        Complete shuffled DataFrame including metadata.
    """
    n_anomalies = int(total_samples * anomaly_rate)
    n_normals = total_samples - n_anomalies
    
    df_normal = generate_normal_applications(n_normals, seed=seed)
    df_anomaly = generate_anomalous_applications(n_anomalies, seed=seed + 100)
    
    # Concatenate and shuffle
    df = pd.concat([df_normal, df_anomaly], ignore_index=True)
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    
    # Assign standard Applicant IDs
    df.insert(0, "applicant_id", [f"APP-{10000 + i}" for i in range(len(df))])
    
    # Ensure target directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[Dataset Generator] Successfully generated {len(df)} records ({n_normals} normal, {n_anomalies} anomalies).")
    print(f"[Dataset Generator] Saved to {output_path}")
    return df


if __name__ == "__main__":
    create_rental_dataset()
