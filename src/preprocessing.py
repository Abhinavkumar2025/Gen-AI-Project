"""RentGuard AI - Preprocessing Pipeline

Provides consistent fitted preprocessing for numerical and categorical features
using Scikit-Learn ColumnTransformer with feature tracking and inverse mapping.
"""

import os
from typing import List, Tuple, Dict, Any
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import joblib

NUMERICAL_FEATURES = [
    "monthly_income",
    "monthly_rent",
    "credit_score",
    "employment_duration",
    "previous_evictions",
    "existing_loans",
    "rental_history_duration",
    "previous_residences"
]

CATEGORICAL_FEATURES = [
    "employment_status"
]

ALL_INPUT_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES


class RentalPreprocessor:
    """Preprocesses raw rental application features for autoencoder consumption."""
    
    def __init__(self):
        self.num_features = NUMERICAL_FEATURES
        self.cat_features = CATEGORICAL_FEATURES
        self.pipeline: ColumnTransformer = None
        self.feature_names_out: List[str] = []
        self.is_fitted: bool = False
        
    def _build_pipeline(self) -> ColumnTransformer:
        return ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), self.num_features),
                (
                    "cat",
                    OneHotEncoder(
                        handle_unknown="ignore",
                        sparse_output=False,
                        categories=[["Full-time", "Self-employed", "Part-time", "Retired", "Unemployed"]]
                    ),
                    self.cat_features
                )
            ],
            remainder="drop"
        )
        
    def fit(self, df: pd.DataFrame) -> "RentalPreprocessor":
        """Fit preprocessor exclusively on representative normal training records."""
        self.pipeline = self._build_pipeline()
        clean_df = df[ALL_INPUT_FEATURES].copy()
        self.pipeline.fit(clean_df)
        
        # Build transformed feature names
        num_names = list(self.num_features)
        cat_encoder = self.pipeline.named_transformers_["cat"]
        cat_names = [f"employment_status_{c}" for c in cat_encoder.categories_[0]]
        self.feature_names_out = num_names + cat_names
        self.is_fitted = True
        return self
        
    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transform input dataframe into scaled numeric array."""
        if not self.is_fitted:
            raise ValueError("RentalPreprocessor must be fitted before transforming data.")
        clean_df = df[ALL_INPUT_FEATURES].copy()
        return self.pipeline.transform(clean_df)
        
    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        """Fit and transform in one step."""
        return self.fit(df).transform(df)
        
    def get_feature_index_mapping(self) -> Dict[str, List[int]]:
        """Maps original human-readable feature names to their transformed array column indices."""
        mapping = {}
        for i, col in enumerate(self.num_features):
            mapping[col] = [i]
            
        cat_start_idx = len(self.num_features)
        cat_indices = list(range(cat_start_idx, len(self.feature_names_out)))
        mapping["employment_status"] = cat_indices
        return mapping
        
    def save(self, filepath: str = "models/preprocessor.joblib") -> None:
        """Persist preprocessor to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self, filepath)
        print(f"[Preprocessor] Saved to {filepath}")
        
    @classmethod
    def load(cls, filepath: str = "models/preprocessor.joblib") -> "RentalPreprocessor":
        """Load fitted preprocessor from disk."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Preprocessor file not found at {filepath}")
        return joblib.load(filepath)
