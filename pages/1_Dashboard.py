"""RentGuard AI - Property Manager Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.database import get_dashboard_summary, get_all_applications_df

st.set_page_config(page_title="Dashboard | RentGuard AI", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem 1.4rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kpi-title {
        font-size: 0.82rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-num {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.2;
        margin: 0.2rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Property Manager Underwriting Dashboard")
st.caption("Live monitoring of rental application flow, autoencoder anomaly flags, and underwriting audit status.")

# Fetch live metrics from database
summary = get_dashboard_summary()

total_apps = summary["total_applications"]
normal_apps = summary["normal_applications"]
flagged_apps = summary["flagged_applications"]
pending_reviews = summary["pending_reviews"]

# KPI Cards row
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Applications</div>
        <div class="kpi-num">{total_apps:,}</div>
        <span style="color: #64748B; font-size: 0.85rem;">Total ingested to date</span>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Normal Applications</div>
        <div class="kpi-num" style="color: #10B981;">{normal_apps:,}</div>
        <span style="color: #10B981; font-size: 0.85rem;">{(normal_apps/total_apps*100 if total_apps>0 else 0):.1f}% baseline adherence</span>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Flagged for Review</div>
        <div class="kpi-num" style="color: #F59E0B;">{flagged_apps:,}</div>
        <span style="color: #F59E0B; font-size: 0.85rem;">{(flagged_apps/total_apps*100 if total_apps>0 else 0):.1f}% statistical variance</span>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Pending Human Review</div>
        <div class="kpi-num" style="color: #EF4444;">{pending_reviews:,}</div>
        <span style="color: #EF4444; font-size: 0.85rem;">Priority underwriting queue</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Charts Section
col_chart1, col_chart2 = st.columns([1, 1])

with col_chart1:
    st.subheader("Anomaly Category Distribution")
    cat_counts = summary["category_distribution"]
    
    if cat_counts:
        categories = list(cat_counts.keys())
        counts = list(cat_counts.values())
        
        # Color mapping: Low=Emerald, Medium=Amber, High=Rose
        color_map = {
            "Low anomaly": "#10B981",
            "Medium anomaly": "#F59E0B",
            "High anomaly": "#EF4444"
        }
        colors = [color_map.get(c, "#6B7280") for c in categories]
        
        fig_donut = go.Figure(data=[go.Pie(
            labels=categories,
            values=counts,
            hole=.55,
            marker=dict(colors=colors),
            textinfo="label+percent",
            hoverinfo="label+value+percent"
        )])
        fig_donut.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=20, b=30, l=10, r=10),
            height=320
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.info("No application data available yet.")

with col_chart2:
    st.subheader("Underwriting Review Status Breakdown")
    status_counts = summary["status_distribution"]
    if status_counts:
        stat_names = list(status_counts.keys())
        stat_vals = list(status_counts.values())
        
        fig_bar = go.Figure(data=[go.Bar(
            x=stat_names,
            y=stat_vals,
            marker_color=["#EF4444" if s=="Pending" else "#3B82F6" if s=="Under Review" else "#10B981" if s=="Verified" else "#F59E0B" for s in stat_names],
            text=stat_vals,
            textposition="auto"
        )])
        fig_bar.update_layout(
            xaxis_title="Review Status",
            yaxis_title="Count",
            margin=dict(t=20, b=30, l=10, r=10),
            height=320
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No review status logs found.")

st.divider()

# Recent Applications Grid
st.subheader("Recent Applications Queue")
df_recent = get_all_applications_df().head(10)

if not df_recent.empty:
    display_cols = [
        "application_id", "applicant_id", "full_name",
        "monthly_income", "monthly_rent", "credit_score",
        "reconstruction_error", "anomaly_category", "review_status", "submission_date"
    ]
    df_show = df_recent[display_cols].copy()
    
    # Format currency and decimal places
    df_show["monthly_income"] = df_show["monthly_income"].apply(lambda x: f"${x:,.2f}")
    df_show["monthly_rent"] = df_show["monthly_rent"].apply(lambda x: f"${x:,.2f}")
    df_show["reconstruction_error"] = df_show["reconstruction_error"].apply(lambda x: f"{x:.4f}")
    
    df_show.rename(columns={
        "application_id": "App ID",
        "applicant_id": "Applicant ID",
        "full_name": "Full Name",
        "monthly_income": "Income",
        "monthly_rent": "Target Rent",
        "credit_score": "Credit Score",
        "reconstruction_error": "Reconstruction MSE",
        "anomaly_category": "Anomaly Tier",
        "review_status": "Review Status",
        "submission_date": "Submitted"
    }, inplace=True)
    
    st.dataframe(df_show, use_container_width=True, hide_index=True)
else:
    st.info("No applications registered in database. Use 'Submit Application' or Seed Starter Data.")
