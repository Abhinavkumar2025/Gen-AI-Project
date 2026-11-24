"""RentGuard AI - Reports & Data Export Center
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from src.database import get_all_applications_df

st.set_page_config(page_title="Reports | RentGuard AI", page_icon="📁", layout="wide")

st.title("📁 Underwriting Reports & Audit Export")
st.caption("Generate customized compliance audit trails, export underwriting analysis reports in CSV format, and review portfolio statistics.")

# Export Configuration Controls
with st.container(border=True):
    st.subheader("Report Export Configuration")
    c1, c2 = st.columns(2)
    
    with c1:
        cat_selection = st.multiselect(
            "Filter by Anomaly Tier",
            options=["Low anomaly", "Medium anomaly", "High anomaly"],
            default=["Low anomaly", "Medium anomaly", "High anomaly"]
        )
        
    with c2:
        status_selection = st.multiselect(
            "Filter by Review Status",
            options=["Pending", "Under Review", "Verified", "Flagged for Clarification"],
            default=["Pending", "Under Review", "Verified", "Flagged for Clarification"]
        )

# Fetch data
df_all = get_all_applications_df()

if not df_all.empty:
    # Filter locally
    mask = df_all["anomaly_category"].isin(cat_selection) & df_all["review_status"].isin(status_selection)
    df_filtered = df_all[mask].copy()
    
    # Portfolio Metrics Banner
    st.markdown("#### Filtered Portfolio Summary")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Records in Report", len(df_filtered))
    with m2:
        avg_inc = df_filtered["monthly_income"].mean() if not df_filtered.empty else 0
        st.metric("Mean Monthly Income", f"${avg_inc:,.2f}")
    with m3:
        avg_rent = df_filtered["monthly_rent"].mean() if not df_filtered.empty else 0
        st.metric("Mean Target Rent", f"${avg_rent:,.2f}")
    with m4:
        avg_err = df_filtered["reconstruction_error"].mean() if not df_filtered.empty else 0
        st.metric("Mean Reconstruction MSE", f"{avg_err:.4f}")
        
    st.markdown("---")
    
    # Report Preview
    st.subheader("Report Data Preview")
    
    export_cols = [
        "application_id", "applicant_id", "full_name",
        "monthly_income", "monthly_rent", "credit_score",
        "employment_duration", "previous_evictions", "existing_loans",
        "employment_status", "rental_history_duration", "previous_residences",
        "reconstruction_error", "anomaly_category", "review_recommendation",
        "review_status", "reviewer_name", "reviewer_notes",
        "last_review_date", "submission_date"
    ]
    
    df_export = df_filtered[[c for c in export_cols if c in df_filtered.columns]].copy()
    st.dataframe(df_export.head(15), use_container_width=True, hide_index=True)
    
    # Generate CSV Data
    csv_bytes = df_export.to_csv(index=False).encode("utf-8")
    filename = f"RentGuard_Audit_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    st.download_button(
        label="📥 Download Underwriting Report (CSV)",
        data=csv_bytes,
        file_name=filename,
        mime="text/csv",
        type="primary",
        use_container_width=True
    )
else:
    st.info("No applications present in the database to generate reports.")
