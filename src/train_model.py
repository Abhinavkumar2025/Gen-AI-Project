"""RentGuard AI - Autoencoder Model Training Pipeline

Builds, compiles, trains, calibrates, and evaluates the Deep Learning Autoencoder
on representative normal rental applications using TensorFlow/Keras.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from keras import layers, regularizers

from src.data_generator import create_rental_dataset
from src.preprocessing import RentalPreprocessor, ALL_INPUT_FEATURES
from src.anomaly_detection import AnomalyDetector


def build_autoencoder(input_dim: int, latent_dim: int = 8) -> keras.Model:
    """
    Constructs a symmetric deep autoencoder architecture with bottleneck latent space.
    Input -> Dense(32) -> Dense(16) -> Latent(8) -> Dense(16) -> Dense(32) -> Output(dim).
    """
    inputs = keras.Input(shape=(input_dim,), name="input_features")
    
    # Encoder
    x = layers.Dense(32, activation="relu", kernel_regularizer=regularizers.l2(1e-4), name="encoder_dense_1")(inputs)
    x = layers.BatchNormalization(name="encoder_bn_1")(x)
    x = layers.Dense(16, activation="relu", name="encoder_dense_2")(x)
    
    # Latent Bottleneck
    latent = layers.Dense(latent_dim, activation="relu", name="latent_space")(x)
    
    # Decoder
    x = layers.Dense(16, activation="relu", name="decoder_dense_1")(latent)
    x = layers.BatchNormalization(name="decoder_bn_1")(x)
    x = layers.Dense(32, activation="relu", name="decoder_dense_2")(x)
    outputs = layers.Dense(input_dim, activation="linear", name="reconstructed_features")(x)
    
    autoencoder = keras.Model(inputs=inputs, outputs=outputs, name="RentGuard_Autoencoder")
    autoencoder.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="mse",
        metrics=["mae"]
    )
    return autoencoder


def train_and_calibrate(
    data_path: str = "dataset/rental_applications.csv",
    models_dir: str = "models",
    epochs: int = 40,
    batch_size: int = 64,
    random_state: int = 42
):
    """Executes full training and threshold calibration workflow."""
    os.makedirs(models_dir, exist_ok=True)
    
    # 1. Ensure dataset exists
    if not os.path.exists(data_path):
        print("[Training] Dataset not found. Generating synthetic rental dataset...")
        df_all = create_rental_dataset(total_samples=8000, anomaly_rate=0.08, output_path=data_path, seed=random_state)
    else:
        df_all = pd.read_csv(data_path)
        
    print(f"[Training] Loaded dataset with {len(df_all)} total records.")
    
    # 2. Partition normal records and test evaluation records
    # Split normal data: 75% for train/val, 25% for test benchmark
    df_normal = df_all[df_all["is_anomaly"] == 0].copy()
    df_anomaly = df_all[df_all["is_anomaly"] == 1].copy()
    
    normal_train_val, normal_test = train_test_split(df_normal, test_size=0.20, random_state=random_state)
    normal_train, normal_val = train_test_split(normal_train_val, test_size=0.20, random_state=random_state)
    
    # Combined test benchmark
    df_benchmark_test = pd.concat([normal_test, df_anomaly], ignore_index=True)
    
    print(f"[Training] Training set size: {len(normal_train)} normal records")
    print(f"[Training] Validation set size: {len(normal_val)} normal records")
    print(f"[Training] Test benchmark size: {len(df_benchmark_test)} records ({len(normal_test)} normal, {len(df_anomaly)} anomaly)")
    
    # 3. Fit preprocessing pipeline ONLY on normal training applications
    preprocessor = RentalPreprocessor()
    preprocessor.fit(normal_train)
    preprocessor_path = os.path.join(models_dir, "preprocessor.joblib")
    preprocessor.save(preprocessor_path)
    
    X_train = preprocessor.transform(normal_train)
    X_val = preprocessor.transform(normal_val)
    
    input_dim = X_train.shape[1]
    print(f"[Training] Preprocessed input dimension: {input_dim}")
    
    # 4. Build and train Autoencoder
    model = build_autoencoder(input_dim=input_dim, latent_dim=8)
    model.summary()
    
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=6,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-5,
            verbose=1
        )
    ]
    
    print("[Training] Fitting Autoencoder...")
    history = model.fit(
        X_train,
        X_train,
        validation_data=(X_val, X_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1
    )
    
    # Save trained Keras model
    model_path = os.path.join(models_dir, "autoencoder.keras")
    model.save(model_path)
    print(f"[Training] Autoencoder saved to {model_path}")
    
    # 5. Calibrate Anomaly Thresholds using Validation Set (Normal pool)
    val_reconstructions = model.predict(X_val, verbose=0)
    val_mse = np.mean(np.square(X_val - val_reconstructions), axis=1)
    
    # 95th percentile -> Medium anomaly threshold
    # 99th percentile -> High anomaly threshold
    p95 = float(np.percentile(val_mse, 95))
    p99 = float(np.percentile(val_mse, 99))
    p50 = float(np.percentile(val_mse, 50))
    p75 = float(np.percentile(val_mse, 75))
    
    thresholds = {
        "calibration_dataset": "Normal Validation Set",
        "sample_size": len(val_mse),
        "median_reconstruction_error": round(p50, 4),
        "p75_reconstruction_error": round(p75, 4),
        "medium_threshold": round(p95, 4),
        "high_threshold": round(p99, 4),
        "medium_percentile": 95,
        "high_percentile": 99,
        "calibration_notes": (
            "Thresholds derived from statistical percentiles on pure validation normal records. "
            "Reconstruction errors <= p95 are classified as Low Anomaly; "
            "between p95 and p99 as Medium Anomaly; > p99 as High Anomaly."
        )
    }
    
    thresholds_path = os.path.join(models_dir, "thresholds.json")
    with open(thresholds_path, "w") as f:
        json.dump(thresholds, f, indent=4)
    print(f"[Training] Calibrated thresholds saved to {thresholds_path}: Medium={p95:.4f}, High={p99:.4f}")
    
    # 6. Benchmark Evaluation on held-out test data
    detector = AnomalyDetector(
        model_path=model_path,
        preprocessor_path=preprocessor_path,
        thresholds_path=thresholds_path
    )
    
    eval_metrics = detector.evaluate_on_benchmark(df_benchmark_test)
    eval_path = os.path.join(models_dir, "evaluation_metrics.json")
    with open(eval_path, "w") as f:
        json.dump(eval_metrics, f, indent=4)
        
    print("\n[Evaluation] Benchmark Results on Synthetic Test Data:")
    print(f" - ROC-AUC: {eval_metrics['roc_auc']:.4f}")
    print(f" - PR-AUC:  {eval_metrics['pr_auc']:.4f}")
    print(f" - Precision: {eval_metrics['precision']:.4f}")
    print(f" - Recall:    {eval_metrics['recall']:.4f}")
    print(f" - F1-Score:  {eval_metrics['f1_score']:.4f}")
    print(f" - False Positive Rate: {eval_metrics['false_positive_rate']:.4f}")
    print(f" - Confusion Matrix: {eval_metrics['confusion_matrix']}")
    
    return {
        "model_path": model_path,
        "preprocessor_path": preprocessor_path,
        "thresholds": thresholds,
        "eval_metrics": eval_metrics
    }


if __name__ == "__main__":
    train_and_calibrate()
