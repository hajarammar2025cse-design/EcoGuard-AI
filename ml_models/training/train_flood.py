"""
Flood Risk Prediction Model Training Script
Dataset: Kaggle Rainfall & Hydrological Flood Dataset
Source: https://www.kaggle.com/datasets/rajanand/rainfall-in-india
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def train_flood_model():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(base_dir, 'datasets', 'flood_data.csv')
    saved_dir = os.path.join(base_dir, 'saved_models')
    os.makedirs(saved_dir, exist_ok=True)

    print("=" * 60)
    print("FLOOD RISK MODEL TRAINING")
    print(f"Loading Kaggle dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    print(f"Dataset shape: {df.shape}")

    # Data Preprocessing & Feature Engineering
    # Map hydrological features to physical environmental units:
    # - rainfall: average monthly / seasonal rainfall intensity (mm)
    # - water_level: river / catchment water gauge level in meters (derived from runoff index 'sub' / 80)
    # - temperature: ambient temperature (°C)
    # - humidity: relative humidity (%)
    X = pd.DataFrame()
    X['rainfall'] = (df['Jun-Sep'] / 4.0).round(2)
    X['water_level'] = (df['sub'] / 80.0).round(2)
    X['temperature'] = df['Temp'].astype(float)
    X['humidity'] = df['Humidity'].astype(float)
    y = df['flood'].astype(int)

    print("\nFeature Summary:")
    print(X.describe())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, max_depth=3, random_state=42),
        "Logistic Regression": LogisticRegression(random_state=42, max_iter=500),
        "Decision Tree": DecisionTreeClassifier(max_depth=5, random_state=42)
    }

    best_name = None
    best_model = None
    best_f1 = -1.0
    model_evaluations = {}

    print("\nEvaluating Candidate Algorithms:")
    for name, clf in models.items():
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        cm = confusion_matrix(y_test, y_pred).tolist()

        model_evaluations[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "confusion_matrix": cm
        }
        print(f"[{name}] Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | F1: {f1:.4f}")

        if f1 > best_f1:
            best_f1 = f1
            best_name = name
            best_model = clf

    print(f"\n--> Selected Best Model: {best_name} with F1: {best_f1:.4f}")

    # Save model and artifacts
    model_file = os.path.join(saved_dir, 'flood_model.joblib')
    joblib.dump({
        'model': best_model,
        'algorithm': best_name,
        'features': ['rainfall', 'water_level', 'temperature', 'humidity'],
        'metrics': model_evaluations[best_name]
    }, model_file)
    print(f"Model saved to: {model_file}")

    metadata = {
        "hazard": "Flood",
        "dataset_name": "Rainfall and Flood Prediction in India",
        "kaggle_url": "https://www.kaggle.com/datasets/rajanand/rainfall-in-india",
        "author": "Raj Anand",
        "total_samples": int(len(df)),
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "features": ['rainfall', 'water_level', 'temperature', 'humidity'],
        "target": "flood (0=No Flood/Normal, 1=High Flood Risk)",
        "selected_algorithm": best_name,
        "metrics": model_evaluations[best_name],
        "all_algorithms_comparison": model_evaluations
    }

    return metadata

if __name__ == '__main__':
    res = train_flood_model()
    print("\nResult metadata:\n", json.dumps(res, indent=2))
