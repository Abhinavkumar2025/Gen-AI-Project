"""RentGuard AI - Automated End-to-End System Test Suite

Validates dataset generation, preprocessing, model inference, threshold calibration,
database persistence, review audit logs, report exports, and explanation fallbacks.
"""

import os
import json
import unittest
import pandas as pd
import numpy as np

from src.data_generator import create_rental_dataset, generate_normal_applications, generate_anomalous_applications
from src.preprocessing import RentalPreprocessor, ALL_INPUT_FEATURES
from src.anomaly_detection import AnomalyDetector
from src.database import (
    init_db, save_application_record, update_review_status,
    get_all_applications_df, get_application_details, get_dashboard_summary
)
from src.explanation import explain_anomaly, generate_rule_based_explanation

TEST_DB_PATH = "data/test_rentguard.db"


class TestRentGuardSystem(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        init_db(TEST_DB_PATH)
        cls.detector = AnomalyDetector()
        
    @classmethod
    def tearDownClass(cls):
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except Exception:
                pass

    def test_01_dataset_generation(self):
        """Test dataset generation bounds, columns, and anomaly separation."""
        df = create_rental_dataset(total_samples=200, anomaly_rate=0.10, output_path="dataset/test_dataset.csv")
        self.assertEqual(len(df), 200)
        self.assertIn("applicant_id", df.columns)
        self.assertIn("monthly_income", df.columns)
        self.assertIn("monthly_rent", df.columns)
        self.assertIn("credit_score", df.columns)
        self.assertIn("is_anomaly", df.columns)
        
        # Verify value constraints
        self.assertTrue((df["credit_score"] >= 300).all())
        self.assertTrue((df["credit_score"] <= 850).all())
        self.assertTrue((df["monthly_income"] > 0).all())
        self.assertTrue((df["monthly_rent"] > 0).all())
        
        # Clean up
        if os.path.exists("dataset/test_dataset.csv"):
            os.remove("dataset/test_dataset.csv")

    def test_02_preprocessing_pipeline(self):
        """Test preprocessor fit, transform shapes, and feature index mapping."""
        df_normal = generate_normal_applications(50)
        prep = RentalPreprocessor()
        prep.fit(df_normal)
        self.assertTrue(prep.is_fitted)
        
        transformed = prep.transform(df_normal)
        self.assertEqual(transformed.shape[0], 50)
        self.assertEqual(transformed.shape[1], 13)  # 8 numerical + 5 one-hot categorical
        
        mapping = prep.get_feature_index_mapping()
        self.assertIn("monthly_income", mapping)
        self.assertIn("employment_status", mapping)
        self.assertEqual(len(mapping["employment_status"]), 5)

    def test_03_anomaly_detector_scoring(self):
        """Test prediction on normal vs. extreme anomalous application."""
        normal_app = {
            "applicant_id": "APP-TEST-NORM",
            "monthly_income": 6500.0,
            "monthly_rent": 1700.0,
            "credit_score": 740,
            "employment_duration": 5.0,
            "previous_evictions": 0,
            "existing_loans": 1,
            "employment_status": "Full-time",
            "rental_history_duration": 6.0,
            "previous_residences": 2
        }
        
        anom_app = {
            "applicant_id": "APP-TEST-ANOM",
            "monthly_income": 1200.0,
            "monthly_rent": 4500.0,
            "credit_score": 510,
            "employment_duration": 0.2,
            "previous_evictions": 3,
            "existing_loans": 9,
            "employment_status": "Part-time",
            "rental_history_duration": 1.0,
            "previous_residences": 7
        }
        
        res_normal = self.detector.score_single_application(normal_app)
        res_anom = self.detector.score_single_application(anom_app)
        
        self.assertIn("reconstruction_error", res_normal)
        self.assertIn("anomaly_category", res_normal)
        self.assertIn("top_contributing_features", res_normal)
        
        # Verify anomalous profile generates higher reconstruction error than normal profile
        self.assertGreater(res_anom["reconstruction_error"], res_normal["reconstruction_error"])
        self.assertEqual(res_normal["anomaly_category"], "Low anomaly")
        self.assertIn(res_anom["anomaly_category"], ["Medium anomaly", "High anomaly"])

    def test_04_database_crud_and_review_workflow(self):
        """Test database insertion, querying, and underwriter review status update."""
        app_data = {
            "applicant_id": "APP-TEST-DB01",
            "full_name": "Test Underwriter Applicant",
            "email": "test.applicant@example.com",
            "monthly_income": 5000.0,
            "monthly_rent": 1500.0,
            "credit_score": 710,
            "employment_duration": 3.5,
            "previous_evictions": 0,
            "existing_loans": 2,
            "employment_status": "Full-time",
            "rental_history_duration": 4.0,
            "previous_residences": 2
        }
        score_res = self.detector.score_single_application(app_data)
        
        # Insert
        app_id = save_application_record(
            app_data=app_data,
            anomaly_result=score_res,
            reviewer_name="Automated Test",
            reviewer_notes="Test seed application",
            db_path=TEST_DB_PATH
        )
        self.assertIsInstance(app_id, int)
        
        # Retrieve details
        details = get_application_details(app_id, db_path=TEST_DB_PATH)
        self.assertIsNotNone(details)
        self.assertEqual(details["applicant_id"], "APP-TEST-DB01")
        self.assertEqual(details["full_name"], "Test Underwriter Applicant")
        
        # Update review status
        update_review_status(
            application_id=app_id,
            status="Verified",
            reviewer_name="Senior Underwriter Jane",
            notes="Income documents verified against W2. Approved.",
            db_path=TEST_DB_PATH
        )
        
        updated_details = get_application_details(app_id, db_path=TEST_DB_PATH)
        history = updated_details["review_history"]
        self.assertEqual(len(history), 2)
        self.assertEqual(history[-1]["status"], "Verified")
        self.assertEqual(history[-1]["reviewer_name"], "Senior Underwriter Jane")

    def test_05_explanation_fallback_and_safety(self):
        """Test that explanation engine provides compliant checklists and falls back cleanly."""
        test_app = {
            "monthly_income": 1800.0,
            "monthly_rent": 3800.0,
            "credit_score": 620,
            "employment_duration": 1.0,
            "previous_evictions": 0,
            "existing_loans": 4,
            "employment_status": "Part-time",
            "rental_history_duration": 2.0,
            "previous_residences": 3
        }
        
        expl = explain_anomaly(
            app_data=test_app,
            reconstruction_error=0.85,
            anomaly_category="High anomaly",
            top_contributions={"monthly_rent": 52.0, "monthly_income": 34.0},
            api_key=None,  # Force fallback
            provider="groq"
        )
        
        self.assertIn("explanation", expl)
        self.assertIn("fields_to_verify", expl)
        self.assertIn("suggested_steps", expl)
        self.assertIn("manager_summary", expl)
        self.assertTrue(len(expl["fields_to_verify"]) > 0)
        self.assertTrue(len(expl["suggested_steps"]) > 0)
        
        # Test Groq with invalid key triggers graceful fallback without exception
        expl_groq_invalid = explain_anomaly(
            app_data=test_app,
            reconstruction_error=0.85,
            anomaly_category="High anomaly",
            top_contributions={"monthly_rent": 52.0, "monthly_income": 34.0},
            api_key="gsk_invalid_test_key_123",
            provider="groq"
        )
        self.assertIn("explanation", expl_groq_invalid)
        
        # Check non-accusatory language compliance
        text_corpus = f"{expl['explanation']} {expl['manager_summary']}".lower()
        self.assertNotIn("fraudulent", text_corpus)
        self.assertNotIn("guilty", text_corpus)
        self.assertNotIn("reject", text_corpus)


if __name__ == "__main__":
    unittest.main()
