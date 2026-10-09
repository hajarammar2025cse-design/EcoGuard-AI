"""
Air Pollution & AQI Model Training Script
Dataset: Air Quality Data in India (CPCB / Kaggle)
Kaggle Source: https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, r2_score, mean_absolute_error

def train_pollution_model():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(base_dir, 'datasets', 'air_quality_data.csv')
    saved_dir = os.path.join(base_dir, 'saved_models')
    os.makedirs(saved_dir, exist_ok=True)

    print("=" * 60)
    print("AIR POLLUTION & AQI MODEL TRAINING")
    print(f"Loading Kaggle dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    print(f"Raw dataset shape: {df.shape}")

    # Drop missing AQI and pollutants
    df = df.dropna(subset=['AQI', 'PM2.5', 'PM10', 'CO', 'NO2', 'SO2']).copy()

    X = pd.DataFrame()
    X['pm25'] = pd.to_numeric(df['PM2.5'])
    X['pm10'] = pd.to_numeric(df['PM10'])
    X['co'] = pd.to_numeric(df['CO'])
    X['no2'] = pd.to_numeric(df['NO2'])
    X['so2'] = pd.to_numeric(df['SO2'])

    y_aqi = pd.to_numeric(df['AQI'])

    # Standard Air Quality Risk Categories:
    # LOW: 0 - 50 (Good)
    # MEDIUM: 51 - 100 (Satisfactory / Moderate)
    # HIGH: 101 - 200 (Poor / Unhealthy)
    # CRITICAL: > 200 (Very Poor / Severe)
    def categorize_aqi(aqi):
        if aqi <= 50:
            return 'LOW'
        elif aqi <= 100:
            return 'MEDIUM'
        elif aqi <= 200:
            return 'HIGH'
        else:
            return 'CRITICAL'

    y_class = y_aqi.apply(categorize_aqi)

    print("\nFeature Summary:")
    print(X.describe())
    print("\nTarget Class Distribution:")
    print(y_class.value_counts())

    X_train, X_test, y_train, y_test, y_train_aqi, y_test_aqi = train_test_split(
        X, y_class, y_aqi, test_size=0.20, random_state=42, stratify=y_class
    )

    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=6, random_state=42),
        "Logistic Regression": LogisticRegression(random_state=42, max_iter=500)
    }

    best_name = None
    best_model = None
    best_f1 = -1.0
    model_evaluations = {}

    print("\nEvaluating Candidate Classifiers:")
    for name, clf in models.items():
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, average='weighted', zero_division=0))
        rec = float(recall_score(y_test, y_pred, average='weighted', zero_division=0))
        f1 = float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
        cm = confusion_matrix(y_test, y_pred, labels=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']).tolist()

        model_evaluations[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "confusion_matrix": cm,
            "classes": ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        }
        print(f"[{name}] Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | F1: {f1:.4f}")

        if f1 > best_f1:
            best_f1 = f1
            best_name = name
            best_model = clf

    print(f"\n--> Selected Best Classifier: {best_name} with F1: {best_f1:.4f}")

    # Also train AQI value regressor for continuous numerical prediction
    print("\nTraining AQI Numerical Regressor (Random Forest)...")
    regressor = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    regressor.fit(X_train, y_train_aqi)
    y_pred_reg = regressor.predict(X_test)
    r2 = float(r2_score(y_test_aqi, y_pred_reg))
    mae = float(mean_absolute_error(y_test_aqi, y_pred_reg))
    print(f"Regressor R2: {r2:.4f} | MAE: {mae:.2f}")

    model_file = os.path.join(saved_dir, 'pollution_model.joblib')
    joblib.dump({
        'classifier': best_model,
        'regressor': regressor,
        'algorithm': best_name,
        'features': ['pm25', 'pm10', 'co', 'no2', 'so2'],
        'metrics': model_evaluations[best_name],
        'regression_metrics': {
            'r2_score': round(r2, 4),
            'mae': round(mae, 4)
        }
    }, model_file)
    print(f"Model saved to: {model_file}")

    metadata = {
        "hazard": "Air Pollution",
        "dataset_name": "Air Quality Data in India (2015-2020)",
        "kaggle_url": "https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india",
        "author": "Rohan Rao / Central Pollution Control Board (CPCB)",
        "total_samples": int(len(X)),
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "features": ['pm25', 'pm10', 'co', 'no2', 'so2'],
        "target": "AQI & Pollution Risk Level (LOW, MEDIUM, HIGH, CRITICAL)",
        "selected_algorithm": best_name,
        "metrics": model_evaluations[best_name],
        "regression_metrics": {
            'r2_score': round(r2, 4),
            'mae': round(mae, 4)
        },
        "all_algorithms_comparison": model_evaluations
    }

    return metadata

if __name__ == '__main__':
    res = train_pollution_model()
    print("\nResult metadata:\n", json.dumps(res, indent=2))
