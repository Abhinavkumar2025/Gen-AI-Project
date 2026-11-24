"""RentGuard AI - All Applications Review Center

Comprehensive search, filter, inspection drawer, and underwriting review audit workflow.
"""

import streamlit as st
import pandas as pd
import json

from src.database import get_all_applications_df, get_application_details, update_review_status

st.set_page_config(page_title="All Applications | RentGuard AI", page_icon="📋", layout="wide")

st.title("📋 Rental Applications Registry")
st.caption("Search, filter, inspect feature residuals, and document underwriter review decisions.")

# Filter Bar
with st.container(border=True):
    f_col1, f_col2, f_col3 = st.columns([1, 1, 2])
    with f_col1:
        cat_filter = st.selectbox("Anomaly Tier Filter", ["All", "High anomaly", "Medium anomaly", "Low anomaly"])
    with f_col2:
        status_filter = st.selectbox("Review Status Filter", ["All", "Pending", "Under Review", "Verified", "Flagged for Clarification"])
    with f_col3:
        search_query = st.text_input("Search Registry", placeholder="Search by Applicant ID (e.g. APP-10023) or Full Name...")

df_apps = get_all_applications_df(
    category_filter=cat_filter,
    status_filter=status_filter,
    search_query=search_query
)

st.markdown(f"**Showing {len(df_apps)} matching records**")

if not df_apps.empty:
    # Summary Table
    table_cols = [
        "application_id", "applicant_id", "full_name",
        "monthly_income", "monthly_rent", "credit_score",
        "employment_status", "reconstruction_error", "anomaly_category",
        "review_status", "submission_date"
    ]
    df_display = df_apps[table_cols].copy()
    df_display["monthly_income"] = df_display["monthly_income"].apply(lambda x: f"${x:,.2f}")
    df_display["monthly_rent"] = df_display["monthly_rent"].apply(lambda x: f"${x:,.2f}")
    df_display["reconstruction_error"] = df_display["reconstruction_error"].apply(lambda x: f"{x:.4f}")
    
    df_display.rename(columns={
        "application_id": "App ID",
        "applicant_id": "Applicant ID",
        "full_name": "Full Name",
        "monthly_income": "Income",
        "monthly_rent": "Target Rent",
        "credit_score": "Credit",
        "employment_status": "Employment",
        "reconstruction_error": "Reconstruction MSE",
        "anomaly_category": "Anomaly Tier",
        "review_status": "Status",
        "submission_date": "Submitted"
    }, inplace=True)
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Application Detail & Underwriting Review Drawer
    st.subheader("🔍 Application Inspector & Underwriting Actions")
    
    app_ids = df_apps["application_id"].tolist()
    app_id_labels = [f"#{row.application_id} - {row.applicant_id} ({row.full_name}) | {row.anomaly_category}" for _, row in df_apps.iterrows()]
    
    selected_idx = st.selectbox("Select Application to Inspect & Review", range(len(app_ids)), format_func=lambda i: app_id_labels[i])
    selected_app_id = app_ids[selected_idx]
    
    app_details = get_application_details(selected_app_id)
    
    if app_details:
        d_col1, d_col2 = st.columns([1, 1])
        
        with d_col1:
            st.markdown(f"#### Profile: **{app_details.get('full_name')}** (`{app_details.get('applicant_id')}`)")
            st.caption(f"Submitted on: {app_details.get('created_at')} | Contact: {app_details.get('email')}")
            
            # Key Parameters Grid
            p1, p2 = st.columns(2)
            with p1:
                st.write(f"**Monthly Income:** ${app_details.get('monthly_income', 0):,.2f}")
                st.write(f"**Target Monthly Rent:** ${app_details.get('monthly_rent', 0):,.2f}")
                rent_ratio = (app_details.get('monthly_rent', 0) / app_details.get('monthly_income', 1)) * 100
                st.write(f"**Rent-to-Income:** `{rent_ratio:.1f}%`")
                st.write(f"**Credit Bureau Score:** {app_details.get('credit_score')}")
                st.write(f"**Existing Loans:** {app_details.get('existing_loans')}")
            with p2:
                st.write(f"**Employment Status:** {app_details.get('employment_status')}")
                st.write(f"**Employment Duration:** {app_details.get('employment_duration')} years")
                st.write(f"**Prior Evictions:** {app_details.get('previous_evictions')}")
                st.write(f"**Rental History:** {app_details.get('rental_history_duration')} years")
                st.write(f"**Previous Residences:** {app_details.get('previous_residences')}")
                
            st.markdown("##### Anomaly Engine Assessment")
            category = app_details.get("anomaly_category", "Low anomaly")
            badge_color = "#10B981" if category == "Low anomaly" else "#F59E0B" if category == "Medium anomaly" else "#EF4444"
            st.markdown(f"""
            <div style="padding: 10px 14px; border-radius: 8px; background: #F8FAFC; border-left: 4px solid {badge_color};">
                <strong>{category}</strong> &mdash; Reconstruction Error: <code>{app_details.get('reconstruction_error', 0):.4f}</code><br>
                <span style="font-size: 0.88rem; color: #475569;">{app_details.get('review_recommendation', '')}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if app_details.get("top_contributing_features"):
                st.write("**Top Discrepant Feature Residuals:**")
                contrib_items = list(app_details["top_contributing_features"].items())[:4]
                for feat, pct in contrib_items:
                    st.progress(min(pct / 100.0, 1.0), text=f"{feat}: {pct:.1f}% contribution")
                    
        with d_col2:
            st.markdown("#### ✍️ Underwriter Audit & Decision Log")
            
            # Review History Timeline
            history_logs = app_details.get("review_history", [])
            with st.expander("📜 Historical Review Log", expanded=True):
                if history_logs:
                    for item in reversed(history_logs):
                        st.markdown(f"""
                        <div style="font-size: 0.85rem; padding: 6px 0; border-bottom: 1px solid #E2E8F0;">
                            <strong>{item.get('status')}</strong> &bull; <em>{item.get('reviewer_name')}</em> ({item.get('updated_at')})<br>
                            <span style="color: #64748B;">{item.get('reviewer_notes')}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No historical review actions recorded.")
                    
            # Update Review Form
            with st.form("update_review_status_form"):
                st.write("**Update Review Status:**")
                new_status = st.selectbox(
                    "New Status",
                    ["Pending", "Under Review", "Verified", "Flagged for Clarification"]
                )
                reviewer_name = st.text_input("Reviewer Name / ID", value="Lead Underwriter")
                reviewer_notes = st.text_area(
                    "Reviewer Notes & Verification Audit",
                    placeholder="E.g., Bank statements verified; 3-month paystubs match stated monthly income. Approved."
                )
                commit_btn = st.form_submit_button("💾 Save Review Decision", type="primary", use_container_width=True)
                
                if commit_btn:
                    if not reviewer_notes.strip():
                        st.warning("Please provide descriptive reviewer notes explaining your decision.")
                    else:
                        update_review_status(
                            application_id=selected_app_id,
                            status=new_status,
                            reviewer_name=reviewer_name.strip(),
                            notes=reviewer_notes.strip()
                        )
                        st.success("Review status updated successfully!")
                        st.rerun()

else:
    st.info("No applications found matching the selected filter criteria.")
