"""
Forest Fire Prediction Model Training Script
Dataset: Algerian Forest Fires Dataset (Kaggle / UCI)
Kaggle Source: https://www.kaggle.com/datasets/nitinchoudhary/algerian-forest-fires-dataset
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

def train_fire_model():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(base_dir, 'datasets', 'algerian_forest_fire_data.csv')
    saved_dir = os.path.join(base_dir, 'saved_models')
    os.makedirs(saved_dir, exist_ok=True)

    print("=" * 60)
    print("FOREST FIRE RISK MODEL TRAINING")
    print(f"Loading Kaggle dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    print(f"Raw dataset shape: {df.shape}")

    # Data Cleaning: remove interior header row and strip whitespace
    df = df[df['Temperature'] != 'Temperature'].dropna()
    df.columns = df.columns.str.strip()

    X = pd.DataFrame()
    X['temperature'] = pd.to_numeric(df['Temperature'], errors='coerce')
    X['humidity'] = pd.to_numeric(df['RH'], errors='coerce')
    X['wind_speed'] = pd.to_numeric(df['Ws'], errors='coerce')
    X['rainfall'] = pd.to_numeric(df['Rain'], errors='coerce')
    X['smoke_level'] = pd.to_numeric(df['FFMC'], errors='coerce')

    # Target: 1 for fire, 0 for not fire
    y = (df['Classes'].astype(str).str.strip().str.lower().str.startswith('fire')).astype(int)

    # Clean any remaining NaNs
    valid_idx = ~(X.isna().any(axis=1) | y.isna())
    X = X[valid_idx]
    y = y[valid_idx]

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

    model_file = os.path.join(saved_dir, 'fire_model.joblib')
    joblib.dump({
        'model': best_model,
        'algorithm': best_name,
        'features': ['temperature', 'humidity', 'wind_speed', 'rainfall', 'smoke_level'],
        'metrics': model_evaluations[best_name]
    }, model_file)
    print(f"Model saved to: {model_file}")

    metadata = {
        "hazard": "Forest Fire",
        "dataset_name": "Algerian Forest Fires Dataset",
        "kaggle_url": "https://www.kaggle.com/datasets/nitinchoudhary/algerian-forest-fires-dataset",
        "author": "Nitin Choudhary / Faroudja Abid",
        "total_samples": int(len(X)),
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "features": ['temperature', 'humidity', 'wind_speed', 'rainfall', 'smoke_level'],
        "target": "Classes (0=Not Fire / Safe, 1=Fire Occurrence)",
        "selected_algorithm": best_name,
        "metrics": model_evaluations[best_name],
        "all_algorithms_comparison": model_evaluations
    }

    return metadata

if __name__ == '__main__':
    res = train_fire_model()
    print("\nResult metadata:\n", json.dumps(res, indent=2))
