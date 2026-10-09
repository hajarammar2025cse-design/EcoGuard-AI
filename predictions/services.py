"""
Machine Learning Inference & Environmental Risk Prediction Service
Loads serialized Joblib models trained on Kaggle datasets and computes
live hazard probabilities, risk categorizations, and automated alert triggers.
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from config.db import get_predictions_col, serialize_doc

_MODELS_CACHE = {}

def get_saved_models_dir():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'ml_models', 'saved_models')

def load_model(hazard_type):
    """
    Lazy loader for serialized ML models with memory caching.
    """
    if hazard_type in _MODELS_CACHE:
        return _MODELS_CACHE[hazard_type]

    saved_dir = get_saved_models_dir()
    file_map = {
        'FLOOD': 'flood_model.joblib',
        'FOREST_FIRE': 'fire_model.joblib',
        'POLLUTION': 'pollution_model.joblib'
    }

    filename = file_map.get(hazard_type)
    if not filename:
        raise ValueError(f"Unknown hazard model type: {hazard_type}")

    file_path = os.path.join(saved_dir, filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Trained model artifact not found at {file_path}. Please execute ml_models/training/train_all.py")

    artifact = joblib.load(file_path)
    _MODELS_CACHE[hazard_type] = artifact
    return artifact

def load_model_metadata():
    """
    Loads model evaluation metrics and dataset information.
    """
    saved_dir = get_saved_models_dir()
    meta_path = os.path.join(saved_dir, 'model_metadata.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            return json.load(f)
    return {}

def predict_flood(rainfall, water_level, temperature, humidity, location="Unknown", save_record=True, user=None):
    """
    Predicts Flood Risk using the trained Kaggle Random Forest model.
    Inputs:
      - rainfall: mm
      - water_level: river gauge depth (m)
      - temperature: °C
      - humidity: %
    """
    artifact = load_model('FLOOD')
    clf = artifact['model']

    X = pd.DataFrame([{
        'rainfall': float(rainfall),
        'water_level': float(water_level),
        'temperature': float(temperature),
        'humidity': float(humidity)
    }])

    pred = int(clf.predict(X)[0])
    probs = clf.predict_proba(X)[0]
    flood_prob = float(probs[1]) if len(probs) > 1 else float(pred)

    # Risk level determination based on probability & hydrologic danger marks
    prob_pct = round(flood_prob * 100, 1)
    if prob_pct >= 75 or float(water_level) >= 8.0:
        risk_level = "CRITICAL"
        explanation = f"Critical flood warning: Inundation probability is {prob_pct}%. River water level ({water_level}m) or rainfall ({rainfall}mm) has breached emergency thresholds."
    elif prob_pct >= 45 or float(water_level) >= 6.0:
        risk_level = "HIGH"
        explanation = f"High flood advisory: Probability of flooding is {prob_pct}%. Hydrological saturation elevated."
    elif prob_pct >= 20:
        risk_level = "MEDIUM"
        explanation = f"Moderate runoff detected: Probability is {prob_pct}%. Water level ({water_level}m) is approaching alert thresholds."
    else:
        risk_level = "LOW"
        explanation = f"Normal hydrological status: Probability of flooding is {prob_pct}%. Conditions are within safe catchment parameters."

    result = {
        "hazard_type": "FLOOD",
        "location": location,
        "input_parameters": {
            "rainfall": float(rainfall),
            "water_level": float(water_level),
            "temperature": float(temperature),
            "humidity": float(humidity)
        },
        "prediction": pred,
        "probability": prob_pct,
        "risk_level": risk_level,
        "explanation": explanation,
        "algorithm": artifact.get('algorithm', 'Random Forest'),
        "timestamp": datetime.utcnow()
    }

    if save_record:
        save_prediction_record(result, user)
        trigger_alert_if_hazardous(result)

    return result

def predict_fire(temperature, humidity, wind_speed, rainfall, smoke_level, location="Unknown", save_record=True, user=None):
    """
    Predicts Forest Fire ignition risk using the trained Kaggle Gradient Boosting model.
    Inputs:
      - temperature: °C
      - humidity: %
      - wind_speed: km/h
      - rainfall: mm
      - smoke_level: FFMC fine fuel dryness / smoke index (0-100)
    """
    artifact = load_model('FOREST_FIRE')
    clf = artifact['model']

    X = pd.DataFrame([{
        'temperature': float(temperature),
        'humidity': float(humidity),
        'wind_speed': float(wind_speed),
        'rainfall': float(rainfall),
        'smoke_level': float(smoke_level)
    }])

    pred = int(clf.predict(X)[0])
    probs = clf.predict_proba(X)[0]
    fire_prob = float(probs[1]) if len(probs) > 1 else float(pred)

    prob_pct = round(fire_prob * 100, 1)
    if prob_pct >= 75 or (float(temperature) >= 38 and float(humidity) <= 25):
        risk_level = "CRITICAL"
        explanation = f"Critical wildfire outbreak danger: Probability {prob_pct}%. Extreme fuel dryness (FFMC {smoke_level}), high temp ({temperature}°C), and low humidity ({humidity}%)."
    elif prob_pct >= 50:
        risk_level = "HIGH"
        explanation = f"High forest fire risk: Fire potential {prob_pct}%. Favorable meteorological ignition and rapid spread conditions detected."
    elif prob_pct >= 25:
        risk_level = "MEDIUM"
        explanation = f"Elevated fire weather: Probability {prob_pct}%. Precautionary observation recommended."
    else:
        risk_level = "LOW"
        explanation = f"Safe conditions: Probability of fire outbreak is {prob_pct}%. Litter fuel moisture and rainfall buffer are adequate."

    result = {
        "hazard_type": "FOREST_FIRE",
        "location": location,
        "input_parameters": {
            "temperature": float(temperature),
            "humidity": float(humidity),
            "wind_speed": float(wind_speed),
            "rainfall": float(rainfall),
            "smoke_level": float(smoke_level)
        },
        "prediction": pred,
        "probability": prob_pct,
        "risk_level": risk_level,
        "explanation": explanation,
        "algorithm": artifact.get('algorithm', 'Gradient Boosting'),
        "timestamp": datetime.utcnow()
    }

    if save_record:
        save_prediction_record(result, user)
        trigger_alert_if_hazardous(result)

    return result

def predict_pollution(pm25, pm10, co, no2, so2, location="Unknown", save_record=True, user=None):
    """
    Predicts Continuous AQI & Air Quality Hazard Category using Kaggle Dual Model.
    Inputs:
      - pm25: ug/m3
      - pm10: ug/m3
      - co: mg/m3
      - no2: ug/m3
      - so2: ug/m3
    """
    artifact = load_model('POLLUTION')
    classifier = artifact['classifier']
    regressor = artifact['regressor']

    X = pd.DataFrame([{
        'pm25': float(pm25),
        'pm10': float(pm10),
        'co': float(co),
        'no2': float(no2),
        'so2': float(so2)
    }])

    predicted_aqi = round(float(regressor.predict(X)[0]), 1)
    risk_class = str(classifier.predict(X)[0])
    
    # Calculate confidence / probability
    probs = classifier.predict_proba(X)[0]
    classes = list(classifier.classes_)
    class_idx = classes.index(risk_class) if risk_class in classes else 0
    confidence = round(float(probs[class_idx]) * 100, 1)

    if risk_class == "CRITICAL" or predicted_aqi > 200:
        risk_level = "CRITICAL"
        explanation = f"Severe/hazardous air quality: Predicted AQI is {predicted_aqi}. High particulate load (PM2.5: {pm25} µg/m³, PM10: {pm10} µg/m³) poses severe respiratory hazards."
    elif risk_class == "HIGH" or predicted_aqi > 100:
        risk_level = "HIGH"
        explanation = f"Poor/unhealthy air quality: Predicted AQI is {predicted_aqi}. Sensitive groups and general population experience increased health vulnerability."
    elif risk_class == "MEDIUM" or predicted_aqi > 50:
        risk_level = "MEDIUM"
        explanation = f"Moderate air quality: Predicted AQI is {predicted_aqi}. Acceptable atmospheric quality with minor concerns for hypersensitive individuals."
    else:
        risk_level = "LOW"
        explanation = f"Good air quality: Predicted AQI is {predicted_aqi}. Clean ambient atmospheric conditions compliant with health standards."

    result = {
        "hazard_type": "AIR_POLLUTION",
        "location": location,
        "input_parameters": {
            "pm25": float(pm25),
            "pm10": float(pm10),
            "co": float(co),
            "no2": float(no2),
            "so2": float(so2)
        },
        "prediction": predicted_aqi,
        "probability": confidence,
        "risk_level": risk_level,
        "explanation": explanation,
        "algorithm": artifact.get('algorithm', 'Random Forest'),
        "timestamp": datetime.utcnow()
    }

    if save_record:
        save_prediction_record(result, user)
        trigger_alert_if_hazardous(result)

    return result

def save_prediction_record(prediction_data, user=None):
    """
    Saves prediction outcome to MongoDB 'predictions' collection.
    """
    try:
        col = get_predictions_col()
        doc = dict(prediction_data)
        if user:
            doc['created_by'] = user
        col.insert_one(doc)
    except Exception as e:
        print(f"Prediction saving error: {e}")

def trigger_alert_if_hazardous(prediction_data):
    """
    Automatically creates an active hazard alert when risk is HIGH or CRITICAL.
    """
    risk_level = prediction_data.get('risk_level')
    if risk_level in ['HIGH', 'CRITICAL']:
        try:
            from alerts.services import create_alert
            hazard_type = prediction_data.get('hazard_type')
            location = prediction_data.get('location', 'General Sector')
            prob = prediction_data.get('probability', 0)
            pred_val = prediction_data.get('prediction', 0)

            if hazard_type == 'FLOOD':
                message = f"Immediate Flood Risk ({risk_level}): Model estimated {prob}% inundation likelihood for {location}."
            elif hazard_type == 'FOREST_FIRE':
                message = f"Forest Fire Danger ({risk_level}): High wildfire outbreak potential ({prob}%) detected at {location}."
            elif hazard_type == 'AIR_POLLUTION':
                message = f"Hazardous Atmospheric Pollution ({risk_level}): AQI reached {pred_val} at {location}."
            else:
                message = f"Environmental Hazard Alert ({risk_level}) for {location}."

            create_alert(
                alert_type=hazard_type,
                location=location,
                severity=risk_level,
                message=message
            )
        except Exception as e:
            print(f"Automated alert trigger error: {e}")
