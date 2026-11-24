"""RentGuard AI - Main Application & Executive Landing

Intelligent Rental Application Anomaly Detection System for Property Managers.
"""

import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from src.database import init_db, get_dashboard_summary, get_all_applications_df
from src.anomaly_detection import AnomalyDetector
from src.data_generator import create_rental_dataset

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="RentGuard AI | Anomaly Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom SaaS CSS Styling
st.markdown("""
<style>
    /* Global styling */
    .main {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Top banner */
    .brand-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 2.2rem 2.5rem;
        border-radius: 14px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #FFFFFF;
    }
    
    .brand-title {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin: 0;
        background: linear-gradient(90deg, #FFFFFF 0%, #93C5FD 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .brand-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-top: 0.5rem;
        font-weight: 400;
        max-width: 800px;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.4rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.06);
        transition: transform 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px -2px rgba(0, 0, 0, 0.08);
    }
    .metric-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 2.1rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0.3rem 0;
    }
    .metric-caption {
        font-size: 0.85rem;
        color: #059669;
        font-weight: 500;
    }
    
    /* Status Badges */
    .badge-low {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-med {
        background-color: #FEF08A;
        color: #713F12;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-high {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.78rem;
        display: inline-block;
    }
    
    /* Ethical banner */
    .compliance-callout {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1.5rem;
        font-size: 0.92rem;
        color: #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)


def ensure_system_initialized():
    """Ensure database and seed data are ready."""
    init_db()
    # Check if applications table has any records
    summary = get_dashboard_summary()
    if summary["total_applications"] == 0:
        dataset_path = "dataset/rental_applications.csv"
        if not os.path.exists(dataset_path):
            create_rental_dataset(total_samples=5000, anomaly_rate=0.08, output_path=dataset_path)
            
        # If model is already trained, seed 150 starter applications into database
        if os.path.exists("models/autoencoder.keras") and os.path.exists("models/preprocessor.joblib"):
            try:
                from src.database import save_application_record
                from src.explanation import generate_rule_based_explanation
                
                detector = AnomalyDetector()
                df_seed = pd.read_csv(dataset_path).head(150)
                
                for _, row in df_seed.iterrows():
                    app_dict = row.to_dict()
                    score_res = detector.score_single_application(app_dict)
                    expl = generate_rule_based_explanation(
                        app_dict,
                        score_res["reconstruction_error"],
                        score_res["anomaly_category"],
                        score_res["top_contributing_features"]
                    )
                    score_res["ai_explanation"] = expl["explanation"]
                    save_application_record(
                        app_data=app_dict,
                        anomaly_result=score_res,
                        reviewer_name="System Ingest",
                        reviewer_notes="Auto-populated synthetic baseline record"
                    )
            except Exception as e:
                print(f"[Init] Seeding skipped: {e}")


ensure_system_initialized()

# App Header
st.markdown("""
<div class="brand-header">
    <div style="display: flex; align-items: center; gap: 15px;">
        <span style="font-size: 2.8rem;">🛡️</span>
        <div>
            <h1 class="brand-title">RentGuard AI</h1>
            <p class="brand-subtitle">
                Intelligent Rental Application Anomaly Detection & Underwriting Intelligence.
                Empowering property managers to uncover atypical applications through unsupervised deep learning.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Ethical Compliance Disclaimer
st.markdown("""
<div class="compliance-callout">
    <strong>⚖️ Fair Housing & Responsible AI Compliance Directive:</strong>
    RentGuard AI utilizes statistical autoencoder reconstruction error to highlight applications that deviate from reference benchmarks.
    <strong>The system NEVER automatically declares an applicant fraudulent or executes automated lease rejections.</strong>
    Every flagged record is strictly surfaced for comprehensive human-in-the-loop manual review.
</div>
""", unsafe_allow_html=True)

# Navigation Cards
st.subheader("Platform Capabilities")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">📊</div>
        <h4 style="margin: 0; color: #0F172A;">Property Dashboard</h4>
        <p style="color: #64748B; font-size: 0.9rem; margin-top: 0.4rem;">
            Real-time analytics, anomaly risk distribution, pending review queues, and recent leasing activity.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Dashboard", key="btn_dash", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")

with col2:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">📝</div>
        <h4 style="margin: 0; color: #0F172A;">Submit Application</h4>
        <p style="color: #64748B; font-size: 0.9rem; margin-top: 0.4rem;">
            Ingest new applicant files with real-time deep learning scoring, feature residual radar, and AI explanation.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Submit New Application", key="btn_sub", use_container_width=True):
        st.switch_page("pages/2_Submit_Application.py")

with col3:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">🔬</div>
        <h4 style="margin: 0; color: #0F172A;">Anomaly Analysis</h4>
        <p style="color: #64748B; font-size: 0.9rem; margin-top: 0.4rem;">
            Inspect reconstruction error curves, feature-wise attribution breakdowns, and ROC/PR benchmark curves.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Explore Model Insights", key="btn_eval", use_container_width=True):
        st.switch_page("pages/4_Anomaly_Analysis.py")

st.divider()

# System Status Overview
st.subheader("System Architecture & Engine Status")
c1, c2, c3, c4 = st.columns(4)

with c1:
    model_exists = os.path.exists("models/autoencoder.keras")
    st.metric("Autoencoder Model", "Ready" if model_exists else "Not Trained", delta="TensorFlow / Keras" if model_exists else "Requires Training")

with c2:
    prep_exists = os.path.exists("models/preprocessor.joblib")
    st.metric("Preprocessing Pipeline", "Fitted" if prep_exists else "Missing", delta="ColumnTransformer")

with c3:
    thresh_exists = os.path.exists("models/thresholds.json")
    st.metric("Calibrated Thresholds", "P95 / P99 Active" if thresh_exists else "Default", delta="Validation-Tuned")

with c4:
    has_groq = bool(os.getenv("GROQ_API_KEY") and not os.getenv("GROQ_API_KEY").startswith("gsk_your_groq"))
    has_openai = bool(os.getenv("OPENAI_API_KEY") and not os.getenv("OPENAI_API_KEY").startswith("your_openai"))
    if has_groq or st.session_state.get("groq_api_key"):
        st.metric("Generative AI Explainer", "Groq LPU Active", delta="Llama-3.3-70B")
    elif has_openai or st.session_state.get("openai_api_key"):
        st.metric("Generative AI Explainer", "OpenAI Connected", delta="GPT-4o")
    else:
        st.metric("Generative AI Explainer", "Deterministic Fallback", delta="Active (Zero Downtime)")

st.markdown("""
---
<p style="text-align: center; color: #94A3B8; font-size: 0.85rem;">
    RentGuard AI &copy; 2026 | Enterprise Rental Underwriting & Anomaly Detection System.
</p>
""", unsafe_allow_html=True)
