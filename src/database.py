"""RentGuard AI - SQLite Database Layer

Manages relational tables for applicants, applications, anomaly scores,
and audit review histories with transactional safety.
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd

DEFAULT_DB_PATH = os.path.join("data", "rentguard.db")


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Create or connect to the SQLite database with row-factory enabled."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initialize SQLite database tables and indexes."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # 1. Applicants table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applicants (
        applicant_id TEXT PRIMARY KEY,
        full_name TEXT,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 2. Applications table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        applicant_id TEXT NOT NULL,
        monthly_income REAL NOT NULL,
        monthly_rent REAL NOT NULL,
        credit_score INTEGER NOT NULL,
        employment_duration REAL NOT NULL,
        previous_evictions INTEGER NOT NULL,
        existing_loans INTEGER NOT NULL,
        employment_status TEXT NOT NULL,
        rental_history_duration REAL NOT NULL,
        previous_residences INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
    );
    """)
    
    # 3. Anomaly results table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anomaly_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id INTEGER NOT NULL,
        applicant_id TEXT NOT NULL,
        reconstruction_error REAL NOT NULL,
        anomaly_category TEXT NOT NULL,
        top_contributions_json TEXT,
        review_recommendation TEXT,
        ai_explanation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (application_id) REFERENCES applications(id),
        FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
    );
    """)
    
    # 4. Review history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS review_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id INTEGER NOT NULL,
        applicant_id TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending',
        reviewer_name TEXT,
        reviewer_notes TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (application_id) REFERENCES applications(id),
        FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
    );
    """)
    
    # Create indexing for rapid dashboard and filter queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_apps_applicant ON applications(applicant_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_anomaly_category ON anomaly_results(anomaly_category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_status ON review_history(status);")
    
    conn.commit()
    conn.close()
    print(f"[Database] SQLite schema verified and ready at {db_path}")


def save_application_record(
    app_data: Dict[str, Any],
    anomaly_result: Dict[str, Any],
    reviewer_name: str = "System Automated",
    reviewer_notes: str = "Initial autoencoder ingestion",
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """
    Atomically insert applicant, application, anomaly result, and initial review status.
    Returns the generated application_id.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    applicant_id = app_data["applicant_id"]
    full_name = app_data.get("full_name", f"Applicant {applicant_id}")
    email = app_data.get("email", f"{applicant_id.lower()}@example.com")
    
    try:
        # Upsert applicant
        cursor.execute("""
        INSERT INTO applicants (applicant_id, full_name, email)
        VALUES (?, ?, ?)
        ON CONFLICT(applicant_id) DO UPDATE SET full_name=excluded.full_name;
        """, (applicant_id, full_name, email))
        
        # Insert application
        cursor.execute("""
        INSERT INTO applications (
            applicant_id, monthly_income, monthly_rent, credit_score,
            employment_duration, previous_evictions, existing_loans,
            employment_status, rental_history_duration, previous_residences
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            applicant_id,
            float(app_data["monthly_income"]),
            float(app_data["monthly_rent"]),
            int(app_data["credit_score"]),
            float(app_data["employment_duration"]),
            int(app_data["previous_evictions"]),
            int(app_data["existing_loans"]),
            str(app_data["employment_status"]),
            float(app_data["rental_history_duration"]),
            int(app_data["previous_residences"])
        ))
        application_id = cursor.lastrowid
        
        # Insert anomaly results
        top_contrib_str = json.dumps(anomaly_result.get("top_contributing_features", {}))
        cursor.execute("""
        INSERT INTO anomaly_results (
            application_id, applicant_id, reconstruction_error,
            anomaly_category, top_contributions_json, review_recommendation, ai_explanation
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            application_id,
            applicant_id,
            float(anomaly_result["reconstruction_error"]),
            str(anomaly_result["anomaly_category"]),
            top_contrib_str,
            str(anomaly_result.get("review_recommendation", "")),
            str(anomaly_result.get("ai_explanation", ""))
        ))
        
        # Insert initial review state
        cursor.execute("""
        INSERT INTO review_history (
            application_id, applicant_id, status, reviewer_name, reviewer_notes
        ) VALUES (?, ?, 'Pending', ?, ?);
        """, (application_id, applicant_id, reviewer_name, reviewer_notes))
        
        conn.commit()
        return application_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def update_review_status(
    application_id: int,
    status: str,
    reviewer_name: str,
    notes: str,
    db_path: str = DEFAULT_DB_PATH
) -> None:
    """Record reviewer notes and update review status."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO review_history (
        application_id, applicant_id, status, reviewer_name, reviewer_notes, updated_at
    )
    SELECT ?, applicant_id, ?, ?, ?, CURRENT_TIMESTAMP
    FROM applications WHERE id = ?;
    """, (application_id, status, reviewer_name, notes, application_id))
    conn.commit()
    conn.close()


def get_all_applications_df(
    category_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    search_query: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH
) -> pd.DataFrame:
    """Retrieve full unified view of applications, scores, and latest review status."""
    conn = get_connection(db_path)
    query = """
    SELECT 
        a.id AS application_id,
        a.applicant_id,
        ap.full_name,
        a.monthly_income,
        a.monthly_rent,
        a.credit_score,
        a.employment_duration,
        a.previous_evictions,
        a.existing_loans,
        a.employment_status,
        a.rental_history_duration,
        a.previous_residences,
        ar.reconstruction_error,
        ar.anomaly_category,
        ar.review_recommendation,
        ar.top_contributions_json,
        ar.ai_explanation,
        rh.status AS review_status,
        rh.reviewer_name,
        rh.reviewer_notes,
        rh.updated_at AS last_review_date,
        a.created_at AS submission_date
    FROM applications a
    JOIN applicants ap ON a.applicant_id = ap.applicant_id
    JOIN anomaly_results ar ON a.id = ar.application_id
    JOIN (
        SELECT application_id, status, reviewer_name, reviewer_notes, updated_at,
               ROW_NUMBER() OVER (PARTITION BY application_id ORDER BY id DESC) as rn
        FROM review_history
    ) rh ON a.id = rh.application_id AND rh.rn = 1
    WHERE 1=1
    """
    params = []
    if category_filter and category_filter != "All":
        query += " AND ar.anomaly_category = ?"
        params.append(category_filter)
    if status_filter and status_filter != "All":
        query += " AND rh.status = ?"
        params.append(status_filter)
    if search_query:
        query += " AND (a.applicant_id LIKE ? OR ap.full_name LIKE ?)"
        params.append(f"%{search_query}%")
        params.append(f"%{search_query}%")
        
    query += " ORDER BY a.id DESC;"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_application_details(application_id: int, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieve comprehensive application record with historical review timeline."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        a.*, ap.full_name, ap.email,
        ar.reconstruction_error, ar.anomaly_category, ar.top_contributions_json,
        ar.review_recommendation, ar.ai_explanation
    FROM applications a
    JOIN applicants ap ON a.applicant_id = ap.applicant_id
    JOIN anomaly_results ar ON a.id = ar.application_id
    WHERE a.id = ?;
    """, (application_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
        
    result = dict(row)
    if result.get("top_contributions_json"):
        result["top_contributing_features"] = json.loads(result["top_contributions_json"])
        
    # Fetch review history
    cursor.execute("""
    SELECT status, reviewer_name, reviewer_notes, updated_at
    FROM review_history
    WHERE application_id = ?
    ORDER BY id ASC;
    """, (application_id,))
    result["review_history"] = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return result


def get_dashboard_summary(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Calculate aggregated metrics for property manager dashboard."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM applications;")
    total_apps = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM anomaly_results WHERE anomaly_category = 'Low anomaly';")
    normal_apps = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM anomaly_results WHERE anomaly_category IN ('Medium anomaly', 'High anomaly');")
    flagged_apps = cursor.fetchone()[0]
    
    cursor.execute("""
    SELECT COUNT(*) FROM (
        SELECT application_id, status, ROW_NUMBER() OVER (PARTITION BY application_id ORDER BY id DESC) as rn
        FROM review_history
    ) WHERE rn = 1 AND status = 'Pending';
    """)
    pending_reviews = cursor.fetchone()[0]
    
    # Category distribution
    cursor.execute("""
    SELECT anomaly_category, COUNT(*) as count 
    FROM anomaly_results 
    GROUP BY anomaly_category;
    """)
    cat_counts = {r["anomaly_category"]: r["count"] for r in cursor.fetchall()}
    
    # Review status distribution
    cursor.execute("""
    SELECT status, COUNT(*) as count FROM (
        SELECT application_id, status, ROW_NUMBER() OVER (PARTITION BY application_id ORDER BY id DESC) as rn
        FROM review_history
    ) WHERE rn = 1 GROUP BY status;
    """)
    status_counts = {r["status"]: r["count"] for r in cursor.fetchall()}
    
    conn.close()
    return {
        "total_applications": total_apps,
        "normal_applications": normal_apps,
        "flagged_applications": flagged_apps,
        "pending_reviews": pending_reviews,
        "category_distribution": cat_counts,
        "status_distribution": status_counts
    }
