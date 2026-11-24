"""RentGuard AI - Anomaly Detection Engine

Calculates autoencoder reconstruction errors, feature-wise error attributions,
and validation-calibrated risk tiers for rental applications.
"""

import os
import json
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, confusion_matrix
)

from src.preprocessing import RentalPreprocessor, ALL_INPUT_FEATURES

DEFAULT_MODEL_PATH = "models/autoencoder.keras"
DEFAULT_PREPROCESSOR_PATH = "models/preprocessor.joblib"
DEFAULT_THRESHOLDS_PATH = "models/thresholds.json"


class AnomalyDetector:
    """Core anomaly detector wrapper around the Keras Autoencoder."""
    
    def __init__(
        self,
        model_path: str = DEFAULT_MODEL_PATH,
        preprocessor_path: str = DEFAULT_PREPROCESSOR_PATH,
        thresholds_path: str = DEFAULT_THRESHOLDS_PATH
    ):
        self.model_path = model_path
        self.preprocessor_path = preprocessor_path
        self.thresholds_path = thresholds_path
        self.model = None
        self.preprocessor: Optional[RentalPreprocessor] = None
        self.threshold_medium: float = 0.50
        self.threshold_high: float = 1.20
        self.threshold_meta: Dict[str, Any] = {}
        self._load_artifacts()
        
    def _load_artifacts(self) -> None:
        """Load trained autoencoder, fitted preprocessor, and calibrated thresholds."""
        if os.path.exists(self.preprocessor_path):
            self.preprocessor = RentalPreprocessor.load(self.preprocessor_path)
            
        if os.path.exists(self.model_path):
            from tensorflow import keras
            self.model = keras.models.load_model(self.model_path)
            
        if os.path.exists(self.thresholds_path):
            with open(self.thresholds_path, "r") as f:
                self.threshold_meta = json.load(f)
                self.threshold_medium = float(self.threshold_meta.get("medium_threshold", 0.50))
                self.threshold_high = float(self.threshold_meta.get("high_threshold", 1.20))
                
    def set_thresholds(self, medium: float, high: float) -> None:
        """Manually override or tune anomaly classification thresholds."""
        self.threshold_medium = float(medium)
        self.threshold_high = float(high)
        
    def predict_reconstruction_error(self, df: pd.DataFrame) -> np.ndarray:
        """
        Compute row-wise Mean Squared Error (MSE) reconstruction loss:
        MSE = (1/D) * sum((X - X_hat)^2)
        """
        if self.model is None or self.preprocessor is None:
            self._load_artifacts()
            if self.model is None or self.preprocessor is None:
                raise RuntimeError("Model or preprocessor artifacts could not be loaded. Please train model first.")
                
        X_scaled = self.preprocessor.transform(df)
        X_reconstructed = self.model.predict(X_scaled, verbose=0)
        
        # Calculate sample-wise MSE across all latent output dimensions
        squared_errors = np.square(X_scaled - X_reconstructed)
        sample_mse = np.mean(squared_errors, axis=1)
        return sample_mse
        
    def score_single_application(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform complete anomaly scoring for a single newly submitted application.
        Returns reconstruction error, category, feature contributions, and recommendations.
        """
        df_single = pd.DataFrame([app_data])
        X_scaled = self.preprocessor.transform(df_single)
        X_hat = self.model.predict(X_scaled, verbose=0)
        
        # Feature-wise squared error across transformed columns
        col_squared_err = np.square(X_scaled[0] - X_hat[0])
        total_mse = float(np.mean(col_squared_err))
        
        # Map transformed feature errors back to original human-readable features
        mapping = self.preprocessor.get_feature_index_mapping()
        feature_errors = {}
        for feature_name, indices in mapping.items():
            # For numerical: single column MSE; for categorical: mean or sum across one-hot representations
            feat_err = float(np.sum(col_squared_err[indices]))
            feature_errors[feature_name] = feat_err
            
        sum_feat_err = sum(feature_errors.values()) or 1e-9
        feature_pct = {k: round((v / sum_feat_err) * 100.0, 2) for k, v in feature_errors.items()}
        # Sort descending by contribution percentage
        sorted_contributions = dict(sorted(feature_pct.items(), key=lambda item: item[1], reverse=True))
        
        # Determine anomaly tier
        if total_mse <= self.threshold_medium:
            category = "Low anomaly"
            recommendation = (
                "Standard Review: Application metrics fall within typical historical distribution. "
                "Proceed with routine document check."
            )
        elif total_mse <= self.threshold_high:
            category = "Medium anomaly"
            recommendation = (
                "Expedited Review: Moderate statistical variance detected. "
                "Verify top contributing fields before approving tenancy."
            )
        else:
            category = "High anomaly"
            recommendation = (
                "Priority Review: Substantial reconstruction divergence observed. "
                "Thorough manual verification of financial and rental documentation is required."
            )
            
        return {
            "reconstruction_error": round(total_mse, 4),
            "anomaly_category": category,
            "review_recommendation": recommendation,
            "top_contributing_features": sorted_contributions,
            "threshold_medium": self.threshold_medium,
            "threshold_high": self.threshold_high
        }
        
    def evaluate_on_benchmark(self, df_test: pd.DataFrame) -> Dict[str, Any]:
        """
        Compute rigorous anomaly classification metrics on held-out test data.
        Note: Ground-truth `is_anomaly` is used strictly for offline validation.
        """
        if "is_anomaly" not in df_test.columns:
            raise ValueError("Test dataframe must contain 'is_anomaly' column for benchmarking.")
            
        y_true = df_test["is_anomaly"].values
        reconstruction_errors = self.predict_reconstruction_error(df_test)
        
        # Binary prediction based on High/Medium threshold for evaluation
        # Flagged = Medium or High anomaly (error > threshold_medium)
        y_pred = (reconstruction_errors >= self.threshold_medium).astype(int)
        
        roc_auc = float(roc_auc_score(y_true, reconstruction_errors))
        pr_auc = float(average_precision_score(y_true, reconstruction_errors))
        precision = float(precision_score(y_true, y_pred, zero_division=0))
        recall = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
        
        return {
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "false_positive_rate": round(fpr, 4),
            "confusion_matrix": {
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive": int(tp)
            },
            "sample_count": len(df_test),
            "threshold_medium": self.threshold_medium,
            "threshold_high": self.threshold_high
        }
