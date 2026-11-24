"""RentGuard AI - Submit Rental Application & Real-Time Underwriting
"""

import uuid
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.database import save_application_record
from src.anomaly_detection import AnomalyDetector
from src.explanation import explain_anomaly

st.set_page_config(page_title="Submit Application | RentGuard AI", page_icon="📝", layout="wide")

st.title("📝 Submit Rental Application")
st.caption("Ingest applicant data for real-time deep learning autoencoder evaluation, feature attribution, and underwriting checklist generation.")

# Initialize presets in session state if not present
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "applicant_id": f"APP-{uuid.uuid4().hex[:6].upper()}",
        "full_name": "Sarah Jenkins",
        "email": "sarah.j@example.com",
        "monthly_income": 6200.0,
        "monthly_rent": 1650.0,
        "credit_score": 725,
        "employment_duration": 4.5,
        "previous_evictions": 0,
        "existing_loans": 1,
        "employment_status": "Full-time",
        "rental_history_duration": 5.0,
        "previous_residences": 2
    }


def load_preset(preset_type: str):
    new_id = f"APP-{uuid.uuid4().hex[:6].upper()}"
    if preset_type == "normal":
        st.session_state.form_data = {
            "applicant_id": new_id,
            "full_name": "David Miller",
            "email": "david.m@example.com",
            "monthly_income": 6500.0,
            "monthly_rent": 1750.0,
            "credit_score": 730,
            "employment_duration": 5.2,
            "previous_evictions": 0,
            "existing_loans": 1,
            "employment_status": "Full-time",
            "rental_history_duration": 6.0,
            "previous_residences": 2
        }
    elif preset_type == "rent_inversion":
        st.session_state.form_data = {
            "applicant_id": new_id,
            "full_name": "Marcus Vance",
            "email": "m.vance@example.com",
            "monthly_income": 1900.0,
            "monthly_rent": 3600.0,
            "credit_score": 590,
            "employment_duration": 1.0,
            "previous_evictions": 0,
            "existing_loans": 4,
            "employment_status": "Part-time",
            "rental_history_duration": 2.5,
            "previous_residences": 3
        }
    elif preset_type == "credit_discordance":
        st.session_state.form_data = {
            "applicant_id": new_id,
            "full_name": "Elena Rostova",
            "email": "elena.r@example.com",
            "monthly_income": 7800.0,
            "monthly_rent": 2200.0,
            "credit_score": 820,
            "employment_duration": 4.0,
            "previous_evictions": 3,
            "existing_loans": 7,
            "employment_status": "Full-time",
            "rental_history_duration": 5.0,
            "previous_residences": 4
        }
    elif preset_type == "unemployed_luxury":
        st.session_state.form_data = {
            "applicant_id": new_id,
            "full_name": "Julian Hayes",
            "email": "j.hayes@example.com",
            "monthly_income": 600.0,
            "monthly_rent": 4200.0,
            "credit_score": 490,
            "employment_duration": 0.0,
            "previous_evictions": 1,
            "existing_loans": 3,
            "employment_status": "Unemployed",
            "rental_history_duration": 1.2,
            "previous_residences": 3
        }
    elif preset_type == "tenure_mismatch":
        st.session_state.form_data = {
            "applicant_id": new_id,
            "full_name": "Robert Chen",
            "email": "r.chen@example.com",
            "monthly_income": 9500.0,
            "monthly_rent": 2400.0,
            "credit_score": 670,
            "employment_duration": 29.0,
            "previous_evictions": 0,
            "existing_loans": 2,
            "employment_status": "Full-time",
            "rental_history_duration": 0.5,
            "previous_residences": 8
        }


# Quick Presets Bar
st.write("**Quick-Load Test Profiles:**")
p1, p2, p3, p4, p5 = st.columns(5)
with p1:
    if st.button("🟢 Representative Normal", use_container_width=True):
        load_preset("normal")
        st.rerun()
with p2:
    if st.button("🔴 Rent-to-Income Inversion", use_container_width=True):
        load_preset("rent_inversion")
        st.rerun()
with p3:
    if st.button("🟠 Credit-Eviction Discordance", use_container_width=True):
        load_preset("credit_discordance")
        st.rerun()
with p4:
    if st.button("🔴 Unemployed Luxury Unit", use_container_width=True):
        load_preset("unemployed_luxury")
        st.rerun()
with p5:
    if st.button("🟠 Tenancy Mismatch", use_container_width=True):
        load_preset("tenure_mismatch")
        st.rerun()

st.divider()

# Input Form
with st.form("application_submission_form"):
    st.subheader("1. Applicant Information")
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        applicant_id = st.text_input("Applicant ID", value=st.session_state.form_data["applicant_id"])
    with col_a2:
        full_name = st.text_input("Applicant Full Name", value=st.session_state.form_data["full_name"])
    with col_a3:
        email = st.text_input("Email Address", value=st.session_state.form_data["email"])
        
    st.subheader("2. Financial & Lease Parameters")
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        monthly_income = st.number_input("Monthly Income ($)", min_value=0.0, max_value=100000.0, value=float(st.session_state.form_data["monthly_income"]), step=100.0)
    with col_b2:
        monthly_rent = st.number_input("Target Monthly Rent ($)", min_value=100.0, max_value=30000.0, value=float(st.session_state.form_data["monthly_rent"]), step=50.0)
    with col_b3:
        credit_score = st.slider("Credit Bureau Score", min_value=300, max_value=850, value=int(st.session_state.form_data["credit_score"]))
        
    st.subheader("3. Employment & Credit Background")
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        emp_status_options = ["Full-time", "Self-employed", "Part-time", "Retired", "Unemployed"]
        cur_status = st.session_state.form_data["employment_status"]
        status_idx = emp_status_options.index(cur_status) if cur_status in emp_status_options else 0
        employment_status = st.selectbox("Employment Classification", emp_status_options, index=status_idx)
    with col_c2:
        employment_duration = st.number_input("Employment Duration (Years)", min_value=0.0, max_value=50.0, value=float(st.session_state.form_data["employment_duration"]), step=0.5)
    with col_c3:
        existing_loans = st.number_input("Active Loan Obligations (Count)", min_value=0, max_value=30, value=int(st.session_state.form_data["existing_loans"]), step=1)
        
    st.subheader("4. Tenancy & Residential History")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        previous_evictions = st.number_input("Prior Evictions (Count)", min_value=0, max_value=10, value=int(st.session_state.form_data["previous_evictions"]), step=1)
    with col_d2:
        rental_history_duration = st.number_input("Rental History Duration (Years)", min_value=0.0, max_value=50.0, value=float(st.session_state.form_data["rental_history_duration"]), step=0.5)
        
    previous_residences = st.slider("Number of Previous Residences (Past 5 Years)", min_value=1, max_value=15, value=int(st.session_state.form_data["previous_residences"]))
    
    submit_button = st.form_submit_button("🛡️ Submit & Evaluate Application", use_container_width=True, type="primary")

# Evaluation logic
if submit_button:
    # 1. Input Validation
    validation_errors = []
    if not applicant_id.strip():
        validation_errors.append("Applicant ID cannot be empty.")
    if monthly_rent <= 0:
        validation_errors.append("Monthly rent must be greater than $0.")
    if monthly_income < 0:
        validation_errors.append("Monthly income cannot be negative.")
        
    if validation_errors:
        for err in validation_errors:
            st.error(f"Validation Error: {err}")
    else:
        app_dict = {
            "applicant_id": applicant_id.strip(),
            "full_name": full_name.strip(),
            "email": email.strip(),
            "monthly_income": float(monthly_income),
            "monthly_rent": float(monthly_rent),
            "credit_score": int(credit_score),
            "employment_duration": float(employment_duration),
            "previous_evictions": int(previous_evictions),
            "existing_loans": int(existing_loans),
            "employment_status": str(employment_status),
            "rental_history_duration": float(rental_history_duration),
            "previous_residences": int(previous_residences)
        }
        
        with st.spinner("Executing Autoencoder Inference & Calculating Residuals..."):
            try:
                detector = AnomalyDetector()
                score_res = detector.score_single_application(app_dict)
            except Exception as e:
                st.error(f"Model Inference Failed: {str(e)}. Please ensure the Autoencoder has been trained under Settings.")
                st.stop()
                
            # Generative AI or Deterministic Explanation
            active_provider = st.session_state.get("llm_provider", "groq")
            active_key = st.session_state.get("groq_api_key") if active_provider == "groq" else st.session_state.get("openai_api_key")
            active_model = st.session_state.get("groq_model") if active_provider == "groq" else st.session_state.get("openai_model")
            
            explanation_data = explain_anomaly(
                app_data=app_dict,
                reconstruction_error=score_res["reconstruction_error"],
                anomaly_category=score_res["anomaly_category"],
                top_contributions=score_res["top_contributing_features"],
                api_key=active_key,
                provider=active_provider,
                model_name=active_model
            )
            score_res["ai_explanation"] = explanation_data["explanation"]
            
            # Persist to SQLite Database
            app_record_id = save_application_record(
                app_data=app_dict,
                anomaly_result=score_res,
                reviewer_name="System Ingest",
                reviewer_notes=f"Auto-scored as {score_res['anomaly_category']}"
            )
            
            st.success(f"Application recorded successfully! Assigned Application ID: #{app_record_id}")
            
            # Results Presentation
            st.markdown("---")
            st.subheader("Underwriting Risk Assessment")
            
            res_col1, res_col2, res_col3 = st.columns(3)
            
            category = score_res["anomaly_category"]
            error_val = score_res["reconstruction_error"]
            badge_color = "#10B981" if category == "Low anomaly" else "#F59E0B" if category == "Medium anomaly" else "#EF4444"
            
            with res_col1:
                st.markdown(f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.2rem; text-align: center;">
                    <div style="font-size: 0.82rem; font-weight: 600; color: #64748B;">RECONSTRUCTION ERROR (MSE)</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #0F172A; margin: 0.3rem 0;">{error_val:.4f}</div>
                    <span style="font-size: 0.8rem; color: #64748B;">Baseline Median: {score_res.get('threshold_medium', 0.5):.2f}</span>
                </div>
                """, unsafe_allow_html=True)
                
            with res_col2:
                st.markdown(f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.2rem; text-align: center;">
                    <div style="font-size: 0.82rem; font-weight: 600; color: #64748B;">ANOMALY CLASSIFICATION</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: {badge_color}; margin: 0.6rem 0;">{category}</div>
                    <span style="font-size: 0.8rem; color: #64748B;">Validation Calibrated (P95/P99)</span>
                </div>
                """, unsafe_allow_html=True)
                
            with res_col3:
                st.markdown(f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.2rem; text-align: center;">
                    <div style="font-size: 0.82rem; font-weight: 600; color: #64748B;">RECOMMENDED ACTION</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #1E293B; margin: 0.5rem 0;">
                        {"Expedited Verification" if category == "Medium anomaly" else "Priority Audit" if category == "High anomaly" else "Standard Ingestion"}
                    </div>
                    <span style="font-size: 0.8rem; color: #64748B;">Non-automated human review</span>
                </div>
                """, unsafe_allow_html=True)
                
            st.info(f"📋 **Review Recommendation**: {score_res['review_recommendation']}")
            
            # Feature Contributions & AI Explanation Columns
            f_col1, f_col2 = st.columns([1, 1])
            
            with f_col1:
                st.subheader("Feature Reconstruction Discrepancies")
                st.caption("Percentage contribution of each input feature to total reconstruction error.")
                
                contrib_dict = score_res["top_contributing_features"]
                df_contrib = pd.DataFrame({
                    "Feature": list(contrib_dict.keys()),
                    "Contribution (%)": list(contrib_dict.values())
                }).sort_values(by="Contribution (%)", ascending=True)
                
                fig_contrib = px.bar(
                    df_contrib,
                    x="Contribution (%)",
                    y="Feature",
                    orientation="h",
                    color="Contribution (%)",
                    color_continuous_scale="Blues"
                )
                fig_contrib.update_layout(
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=300,
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_contrib, use_container_width=True)
                
            with f_col2:
                st.subheader("Generative AI Verification Guidance")
                st.caption(f"Engine: {explanation_data.get('source', 'RentGuard Explainer')}")
                
                with st.container(border=True):
                    st.write("**Pattern Summary:**")
                    st.write(explanation_data.get("explanation", "Standard profile adherence."))
                    
                    st.write("**Fields Requiring Documentation:**")
                    for f in explanation_data.get("fields_to_verify", []):
                        st.markdown(f"- `{f}`")
                        
                    st.write("**Suggested Underwriter Actions:**")
                    for step in explanation_data.get("suggested_steps", []):
                        st.markdown(f"1. {step}")
                        
                    st.write("**Executive Summary:**")
                    st.caption(explanation_data.get("manager_summary", "Review complete."))
