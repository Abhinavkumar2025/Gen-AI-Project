"""RentGuard AI - System Settings & Threshold Calibration
"""

import os
import json
import streamlit as st
import pandas as pd

from src.anomaly_detection import AnomalyDetector, DEFAULT_THRESHOLDS_PATH
from src.database import get_connection, save_application_record
from src.explanation import explain_anomaly
from src.data_generator import create_rental_dataset

st.set_page_config(page_title="Settings | RentGuard AI", page_icon="⚙️", layout="wide")

st.title("⚙️ System Configuration & Model Calibration")
st.caption("Manage unsupervised anomaly thresholds, configure Groq / OpenAI LLM underwriting explanations, and manage pipeline artifacts.")

# Tabbed Layout
tab_thresh, tab_ai, tab_model = st.tabs([
    "🎯 Anomaly Threshold Calibration",
    "⚡ Groq / AI Underwriting Explainer",
    "🔄 Model Training & Data Operations"
])

# ----------------- TAB 1: THRESHOLDS -----------------
with tab_thresh:
    st.subheader("Calibrated Anomaly Classification Thresholds")
    st.markdown("""
    RentGuard AI assigns applications to three operational risk tiers based on their
    reconstruction error ($MSE$). These thresholds are calibrated against validation-split normal profiles.
    """)
    
    current_medium = 0.0525
    current_high = 0.1420
    meta_info = {}
    
    if os.path.exists(DEFAULT_THRESHOLDS_PATH):
        try:
            with open(DEFAULT_THRESHOLDS_PATH, "r") as f:
                meta_info = json.load(f)
                current_medium = float(meta_info.get("medium_threshold", 0.0525))
                current_high = float(meta_info.get("high_threshold", 0.1420))
        except Exception:
            pass
            
    with st.form("thresholds_form"):
        col_th1, col_th2 = st.columns(2)
        with col_th1:
            new_medium = st.number_input(
                "Medium Anomaly Threshold (P95 Cutoff)",
                min_value=0.001,
                max_value=5.0,
                value=float(current_medium),
                step=0.005,
                format="%.4f",
                help="Applications with reconstruction error below this value are classified as Low Anomaly (routine)."
            )
        with col_th2:
            new_high = st.number_input(
                "High Anomaly Threshold (P99 Cutoff)",
                min_value=float(new_medium),
                max_value=15.0,
                value=float(current_high),
                step=0.005,
                format="%.4f",
                help="Applications with reconstruction error above this value trigger priority underwriter scrutiny."
            )
            
        save_thresh_btn = st.form_submit_button("💾 Save Calibrated Thresholds", type="primary")
        
        if save_thresh_btn:
            if new_high <= new_medium:
                st.error("High Anomaly Threshold must be strictly greater than Medium Anomaly Threshold.")
            else:
                meta_info["medium_threshold"] = round(new_medium, 4)
                meta_info["high_threshold"] = round(new_high, 4)
                meta_info["updated_by"] = "Property Manager / Administrator"
                os.makedirs(os.path.dirname(DEFAULT_THRESHOLDS_PATH), exist_ok=True)
                with open(DEFAULT_THRESHOLDS_PATH, "w") as f:
                    json.dump(meta_info, f, indent=4)
                st.success(f"Thresholds saved successfully! Medium: {new_medium:.4f} | High: {new_high:.4f}")

# ----------------- TAB 2: AI EXPLANATION (GROQ / OPENAI) -----------------
with tab_ai:
    st.subheader("⚡ Groq AI Underwriting Explainer Configuration")
    st.markdown("""
    Configure the ultra-fast **Groq API** powering natural-language verification checklists.
    RentGuard AI uses Groq LPUs to achieve sub-second underwriter explanations.
    If no API key is supplied, the platform automatically utilizes our deterministic underwriting rule engine.
    """)
    
    # Provider selection
    provider = st.radio(
        "Active LLM Provider",
        options=["Groq (Ultra-Fast LPUs)", "OpenAI", "Deterministic Rule Engine (Offline)"],
        index=0,
        horizontal=True
    )
    
    col_ai1, col_ai2 = st.columns([2, 1])
    
    if provider == "Groq (Ultra-Fast LPUs)":
        with col_ai1:
            current_groq_key = os.getenv("GROQ_API_KEY", "")
            if current_groq_key.startswith("gsk_your_groq"):
                current_groq_key = ""
            if "groq_api_key" in st.session_state:
                current_groq_key = st.session_state["groq_api_key"]
                
            groq_key_input = st.text_input(
                "Groq API Key",
                value=current_groq_key,
                type="password",
                placeholder="gsk_...",
                help="Your Groq API key (starts with gsk_). Never exposed in UI output."
            )
            
            groq_models = [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768"
            ]
            selected_groq_model = st.selectbox(
                "Groq Model",
                options=groq_models,
                index=0,
                help="llama-3.3-70b-versatile provides the highest underwriting reasoning fidelity."
            )
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("Save Groq Configuration", use_container_width=True, type="primary"):
                    st.session_state["groq_api_key"] = groq_key_input.strip()
                    st.session_state["groq_model"] = selected_groq_model
                    st.session_state["llm_provider"] = "groq"
                    # Also write to .env if present
                    st.success("Groq configuration saved for this session!")
                    
            with c_btn2:
                if st.button("⚡ Test Groq Connection", use_container_width=True):
                    test_key = groq_key_input.strip() or current_groq_key
                    if not test_key:
                        st.warning("Please enter a Groq API Key (starts with `gsk_`) to test.")
                    else:
                        with st.spinner("Connecting to Groq LPU API..."):
                            test_app = {
                                "monthly_income": 2000,
                                "monthly_rent": 3500,
                                "credit_score": 600,
                                "employment_duration": 1,
                                "previous_evictions": 0,
                                "existing_loans": 3,
                                "employment_status": "Full-time",
                                "rental_history_duration": 2,
                                "previous_residences": 2
                            }
                            res = explain_anomaly(
                                app_data=test_app,
                                reconstruction_error=0.45,
                                anomaly_category="High anomaly",
                                top_contributions={"monthly_income": 45.0, "monthly_rent": 40.0},
                                api_key=test_key,
                                provider="groq",
                                model_name=selected_groq_model
                            )
                            if "Groq" in res.get("source", ""):
                                st.success(f"Connection Successful! Responded via {res.get('source')}")
                                st.write(f"Sample explanation: *{res.get('manager_summary')}*")
                            else:
                                st.error(f"Groq connection failed. Reason: {res.get('source')}")
                                
        with col_ai2:
            st.markdown("""
            <div style="background: #F1F5F9; border-radius: 10px; padding: 1.2rem; border: 1px solid #CBD5E1;">
                <h5 style="margin-top:0;">⚡ Why Groq?</h5>
                <p style="font-size:0.85rem; color:#475569;">
                    Groq's LPUs provide real-time token throughput (500+ tokens/sec) for Llama-3.3, delivering instantaneous underwriting explanations with zero lag.
                </p>
                <hr style="margin: 0.8rem 0;">
                <h6 style="margin:0;">Get a Free Groq Key:</h6>
                <p style="font-size:0.82rem; color:#475569;">
                    Create a free key at <a href="https://console.groq.com/keys" target="_blank">console.groq.com</a>.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
    elif provider == "OpenAI":
        with col_ai1:
            current_oa_key = os.getenv("OPENAI_API_KEY", "")
            if "openai_api_key" in st.session_state:
                current_oa_key = st.session_state["openai_api_key"]
                
            oa_key_input = st.text_input("OpenAI API Key", value=current_oa_key, type="password", placeholder="sk-proj-...")
            selected_oa_model = st.selectbox("OpenAI Model", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"], index=0)
            
            if st.button("Save OpenAI Configuration", type="primary"):
                st.session_state["openai_api_key"] = oa_key_input.strip()
                st.session_state["openai_model"] = selected_oa_model
                st.session_state["llm_provider"] = "openai"
                st.success("OpenAI configuration saved!")
        with col_ai2:
            st.info("OpenAI integration active as alternate provider.")
    else:
        st.session_state["llm_provider"] = "deterministic"
        st.info("Using built-in deterministic rule engine. No external API keys required.")

# ----------------- TAB 3: MODEL OPERATIONS -----------------
with tab_model:
    st.subheader("Model Lifecycle & Database Seeding Operations")
    
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        st.markdown("#### Retrain Deep Learning Autoencoder")
        st.markdown("Re-fit the preprocessor and retrain the Keras neural network on normal applications.")
        
        epochs = st.slider("Training Epochs", min_value=10, max_value=80, value=35, step=5)
        batch_size = st.selectbox("Batch Size", [32, 64, 128], index=1)
        
        if st.button("🚀 Retrain Autoencoder Model", type="primary", use_container_width=True):
            with st.spinner(f"Training Autoencoder for {epochs} epochs... Please wait..."):
                try:
                    from src.train_model import train_and_calibrate
                    results = train_and_calibrate(epochs=epochs, batch_size=batch_size)
                    st.success("Autoencoder retrained and calibrated successfully!")
                    st.json(results["eval_metrics"])
                except Exception as e:
                    st.error(f"Retraining failed: {str(e)}")
                    
    with col_m2:
        st.markdown("#### Database Seeding & Reset")
        st.markdown("Populate SQLite database with fresh synthetic rental applications.")
        
        seed_count = st.slider("Sample Records to Seed", min_value=50, max_value=300, value=150, step=25)
        
        if st.button("🌱 Populate / Reseed Database", use_container_width=True):
            with st.spinner("Seeding database with synthetic records..."):
                try:
                    dataset_path = "dataset/rental_applications.csv"
                    if not os.path.exists(dataset_path):
                        create_rental_dataset(total_samples=5000, output_path=dataset_path)
                    
                    df_seed = pd.read_csv(dataset_path).sample(n=seed_count, random_state=42)
                    detector = AnomalyDetector()
                    
                    seeded_count = 0
                    for _, row in df_seed.iterrows():
                        app_dict = row.to_dict()
                        score_res = detector.score_single_application(app_dict)
                        expl = explain_anomaly(
                            app_dict,
                            score_res["reconstruction_error"],
                            score_res["anomaly_category"],
                            score_res["top_contributing_features"],
                            provider=st.session_state.get("llm_provider", "groq"),
                            api_key=st.session_state.get("groq_api_key")
                        )
                        score_res["ai_explanation"] = expl["explanation"]
                        save_application_record(
                            app_data=app_dict,
                            anomaly_result=score_res,
                            reviewer_name="System Seeder",
                            reviewer_notes="Synthetic baseline record generated during system setup"
                        )
                        seeded_count += 1
                        
                    st.success(f"Successfully seeded {seeded_count} applications into SQLite database!")
                except Exception as e:
                    st.error(f"Database seeding failed: {str(e)}")
