"""
Master Training Script for Environmental Hazard Prediction Models
Executes end-to-end training for Flood, Forest Fire, and Pollution models
using authentic Kaggle datasets and saves evaluation metadata.
"""
import os
import sys
import json

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from train_flood import train_flood_model
from train_fire import train_fire_model
from train_pollution import train_pollution_model

def train_all():
    print("=" * 70)
    print("AI-POWERED ENVIRONMENTAL MONITORING NETWORK")
    print("STARTING FULL MACHINE LEARNING TRAINING PIPELINE")
    print("=" * 70)

    results = {}

    print("\n[1/3] Training Flood Risk Model...")
    flood_meta = train_flood_model()
    results["flood"] = flood_meta

    print("\n[2/3] Training Forest Fire Model...")
    fire_meta = train_fire_model()
    results["fire"] = fire_meta

    print("\n[3/3] Training Air Pollution & AQI Model...")
    pollution_meta = train_pollution_model()
    results["pollution"] = pollution_meta

    base_dir = os.path.dirname(current_dir)
    metadata_path = os.path.join(base_dir, 'saved_models', 'model_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 70)
    print("ALL MODELS TRAINED AND SAVED SUCCESSFULLY!")
    print(f"Metadata written to: {metadata_path}")
    print("=" * 70)

    # Print summary table
    print("\nEVALUATION SUMMARY OF TRAINED KAGGLE MODELS:")
    print("-" * 70)
    print(f"{'Hazard':<15} | {'Algorithm':<18} | {'Accuracy':<10} | {'F1-Score':<10}")
    print("-" * 70)
    for hazard, meta in results.items():
        alg = meta['selected_algorithm']
        acc = meta['metrics']['accuracy']
        f1 = meta['metrics']['f1_score']
        print(f"{meta['hazard']:<15} | {alg:<18} | {acc:<10.4f} | {f1:<10.4f}")
    print("-" * 70)

if __name__ == '__main__':
    train_all()
