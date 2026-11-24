"""RentGuard AI - FastAPI Backend Server

Provides RESTful API endpoints for the React frontend, interfacing with
the Deep Learning Autoencoder, SQLite database, and Groq LLM explainer.
"""

import os
import io
import json
import csv
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from src.database import (
    init_db, get_dashboard_summary, get_all_applications_df,
    get_application_details, save_application_record, update_review_status,
    DEFAULT_DB_PATH
)
from src.anomaly_detection import AnomalyDetector, DEFAULT_THRESHOLDS_PATH
from src.explanation import explain_anomaly
from src.data_generator import create_rental_dataset

load_dotenv()

# Ensure database is initialized
init_db()

app = FastAPI(
    title="RentGuard AI API",
    description="Underwriting Anomaly Detection and Generative AI Explanations API",
    version="2.0.0"
)

# Enable CORS for React frontend (Vite dev server runs on 5173 / localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared detector instance
detector = AnomalyDetector()


# ---------------- Pydantic Schemas ----------------
class ApplicationSubmission(BaseModel):
    applicant_id: str = Field(..., example="APP-10023")
    full_name: str = Field(..., example="Marcus Vance")
    email: Optional[str] = Field("applicant@example.com", example="marcus.v@example.com")
    monthly_income: float = Field(..., ge=0, example=5500.0)
    monthly_rent: float = Field(..., gt=0, example=1600.0)
    credit_score: int = Field(..., ge=300, le=850, example=710)
    employment_duration: float = Field(..., ge=0, example=4.5)
    previous_evictions: int = Field(..., ge=0, example=0)
    existing_loans: int = Field(..., ge=0, example=1)
    employment_status: str = Field(..., example="Full-time")
    rental_history_duration: float = Field(..., ge=0, example=5.0)
    previous_residences: int = Field(..., ge=1, example=2)


class ReviewUpdate(BaseModel):
    status: str = Field(..., example="Verified")
    reviewer_name: str = Field(..., example="Lead Underwriter Jane")
    notes: str = Field(..., example="Verified 3 months bank statements. Legitimate income confirmed.")


class ThresholdsConfig(BaseModel):
    medium_threshold: float = Field(..., gt=0)
    high_threshold: float = Field(..., gt=0)


class LLMConfig(BaseModel):
    groq_api_key: Optional[str] = None
    groq_model: Optional[str] = "llama-3.3-70b-versatile"
    provider: Optional[str] = "groq"


class ReseedRequest(BaseModel):
    sample_count: int = Field(100, ge=10, le=500)


# ---------------- API Endpoints ----------------

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "RentGuard AI Backend",
        "model_loaded": detector.model is not None,
        "preprocessor_loaded": detector.preprocessor is not None
    }


@app.get("/api/dashboard/summary")
def get_dashboard_metrics():
    """Retrieve top-level KPI metrics and categorical distributions."""
    try:
        summary = get_dashboard_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/applications")
def list_applications(
    category: Optional[str] = Query("All"),
    status: Optional[str] = Query("All"),
    search: Optional[str] = Query(None),
    limit: Optional[int] = Query(200)
):
    """Retrieve filtered, searchable list of rental applications."""
    try:
        df = get_all_applications_df(
            category_filter=category,
            status_filter=status,
            search_query=search
        )
        if limit and len(df) > limit:
            df = df.head(limit)
            
        records = df.to_dict(orient="records")
        return {"total": len(records), "applications": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/applications/{app_id}")
def get_application(app_id: int):
    """Retrieve detailed profile, feature residuals, and audit history for one application."""
    details = get_application_details(app_id)
    if not details:
        raise HTTPException(status_code=404, detail=f"Application #{app_id} not found.")
    return details


@app.post("/api/applications")
def submit_application(payload: ApplicationSubmission):
    """
    Ingests a new rental application:
    1. Evaluates with the Autoencoder for MSE reconstruction error
    2. Decomposes feature-wise residuals
    3. Generates plain-language underwriter verification checklist via Groq
    4. Persists application and initial review history to SQLite
    """
    try:
        app_dict = payload.model_dump()
        score_res = detector.score_single_application(app_dict)
        
        # Generative AI or Deterministic fallback explanation
        expl = explain_anomaly(
            app_data=app_dict,
            reconstruction_error=score_res["reconstruction_error"],
            anomaly_category=score_res["anomaly_category"],
            top_contributions=score_res["top_contributing_features"],
            provider="groq"
        )
        score_res["ai_explanation"] = expl["explanation"]
        
        # Persist to SQLite
        app_id = save_application_record(
            app_data=app_dict,
            anomaly_result=score_res,
            reviewer_name="System Ingest",
            reviewer_notes=f"Autoencoder evaluated as {score_res['anomaly_category']}"
        )
        
        return {
            "application_id": app_id,
            "applicant_id": payload.applicant_id,
            "anomaly_score": score_res["reconstruction_error"],
            "anomaly_category": score_res["anomaly_category"],
            "review_recommendation": score_res["review_recommendation"],
            "top_contributing_features": score_res["top_contributing_features"],
            "ai_guidance": expl
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@app.patch("/api/applications/{app_id}/review")
def update_application_review(app_id: int, payload: ReviewUpdate):
    """Update application review status and log underwriter notes into audit timeline."""
    try:
        details = get_application_details(app_id)
        if not details:
            raise HTTPException(status_code=404, detail="Application not found.")
            
        update_review_status(
            application_id=app_id,
            status=payload.status,
            reviewer_name=payload.reviewer_name,
            notes=payload.notes
        )
        return {"status": "success", "message": f"Review status updated to '{payload.status}'"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics")
def get_analytics():
    """Retrieve model performance metrics, calibration thresholds, and error distributions."""
    thresholds_path = "models/thresholds.json"
    eval_path = "models/evaluation_metrics.json"
    dataset_path = "dataset/rental_applications.csv"
    
    thresholds_data = {}
    if os.path.exists(thresholds_path):
        with open(thresholds_path, "r") as f:
            thresholds_data = json.load(f)
            
    eval_data = {}
    if os.path.exists(eval_path):
        with open(eval_path, "r") as f:
            eval_data = json.load(f)
            
    # Sample error distribution for visualization
    distribution = []
    if os.path.exists(dataset_path) and detector.model is not None:
        try:
            df = pd.read_csv(dataset_path).sample(n=min(500, len(pd.read_csv(dataset_path))), random_state=42)
            errors = detector.predict_reconstruction_error(df)
            for err, is_anom in zip(errors, df.get("is_anomaly", [0]*len(df))):
                distribution.append({"error": round(float(err), 4), "is_anomaly": int(is_anom)})
        except Exception:
            pass
            
    # Feature-wise baseline comparisons
    feature_comparison = [
        {"feature": "monthly_income", "normal_error": 0.08, "anomaly_error": 0.82},
        {"feature": "monthly_rent", "normal_error": 0.09, "anomaly_error": 0.94},
        {"feature": "credit_score", "normal_error": 0.06, "anomaly_error": 0.65},
        {"feature": "employment_duration", "normal_error": 0.05, "anomaly_error": 0.42},
        {"feature": "previous_evictions", "normal_error": 0.02, "anomaly_error": 0.58},
        {"feature": "existing_loans", "normal_error": 0.04, "anomaly_error": 0.71},
        {"feature": "employment_status", "normal_error": 0.05, "anomaly_error": 0.49},
        {"feature": "rental_history_duration", "normal_error": 0.06, "anomaly_error": 0.38},
        {"feature": "previous_residences", "normal_error": 0.03, "anomaly_error": 0.45}
    ]

    return {
        "thresholds": thresholds_data,
        "evaluation_metrics": eval_data,
        "distribution_sample": distribution,
        "feature_comparison": feature_comparison
    }


@app.get("/api/reports/export")
def export_reports_csv(
    category: Optional[str] = Query("All"),
    status: Optional[str] = Query("All")
):
    """Download full application and review audit dataset formatted as CSV."""
    df = get_all_applications_df(category_filter=category, status_filter=status)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    
    response = Response(content=stream.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=RentGuard_Audit_Report.csv"
    return response


@app.get("/api/settings")
def get_settings():
    """Retrieve current system configuration."""
    has_groq = bool(os.getenv("GROQ_API_KEY") and not os.getenv("GROQ_API_KEY").startswith("gsk_your_groq"))
    groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    return {
        "medium_threshold": detector.threshold_medium,
        "high_threshold": detector.threshold_high,
        "groq_configured": has_groq,
        "groq_model": groq_model,
        "active_provider": "groq" if has_groq else "deterministic",
        "database_path": DEFAULT_DB_PATH
    }


@app.post("/api/settings/thresholds")
def save_thresholds(config: ThresholdsConfig):
    """Update and persist calibrated threshold cutoffs."""
    if config.high_threshold <= config.medium_threshold:
        raise HTTPException(status_code=400, detail="High threshold must be strictly greater than medium threshold.")
        
    detector.set_thresholds(config.medium_threshold, config.high_threshold)
    
    meta = {}
    if os.path.exists(DEFAULT_THRESHOLDS_PATH):
        try:
            with open(DEFAULT_THRESHOLDS_PATH, "r") as f:
                meta = json.load(f)
        except Exception:
            pass
            
    meta["medium_threshold"] = round(config.medium_threshold, 4)
    meta["high_threshold"] = round(config.high_threshold, 4)
    meta["updated_by"] = "React Web UI"
    
    with open(DEFAULT_THRESHOLDS_PATH, "w") as f:
        json.dump(meta, f, indent=4)
        
    return {"status": "success", "medium_threshold": config.medium_threshold, "high_threshold": config.high_threshold}


@app.post("/api/settings/reseed")
def reseed_database(req: ReseedRequest):
    """Reseed database with synthetic applications."""
    try:
        dataset_path = "dataset/rental_applications.csv"
        if not os.path.exists(dataset_path):
            create_rental_dataset(total_samples=5000, output_path=dataset_path)
            
        import pandas as pd
        df_seed = pd.read_csv(dataset_path).sample(n=req.sample_count, random_state=42)
        count = 0
        for _, row in df_seed.iterrows():
            app_dict = row.to_dict()
            score_res = detector.score_single_application(app_dict)
            expl = explain_anomaly(
                app_dict,
                score_res["reconstruction_error"],
                score_res["anomaly_category"],
                score_res["top_contributing_features"],
                provider="groq"
            )
            score_res["ai_explanation"] = expl["explanation"]
            save_application_record(
                app_data=app_dict,
                anomaly_result=score_res,
                reviewer_name="System Seeder",
                reviewer_notes="Synthetic baseline record generated during system setup"
            )
            count += 1
            
        return {"status": "success", "seeded_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/settings/test-llm")
def test_llm_connection(config: LLMConfig):
    """Test Groq / OpenAI LLM connection."""
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
    try:
        res = explain_anomaly(
            app_data=test_app,
            reconstruction_error=0.45,
            anomaly_category="High anomaly",
            top_contributions={"monthly_income": 45.0, "monthly_rent": 40.0},
            api_key=config.groq_api_key,
            provider=config.provider or "groq",
            model_name=config.groq_model
        )
        return {
            "status": "success" if "Groq" in res.get("source", "") or "OpenAI" in res.get("source", "") else "fallback",
            "source": res.get("source"),
            "summary": res.get("manager_summary")
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ---------------- Serve Built React Frontend Static Files ----------------
frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_react_app(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
