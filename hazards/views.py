"""
Dedicated Environmental Hazard Modules:
- Flood Hazard Monitoring & Hydrological Risk
- Forest Fire Weather & Ignition Risk
- Atmospheric Pollution & Air Quality Index
- ML Model Performance Auditing
"""
import json
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import JsonResponse
from accounts.auth_helper import login_required_custom
from config.db import (
    get_env_data_col, get_locations_col, get_predictions_col,
    get_alerts_col, serialize_docs
)
from predictions.services import (
    predict_flood, predict_fire, predict_pollution, load_model_metadata
)

@login_required_custom
def flood_module_view(request):
    """
    Flood Monitoring Module
    Displays hydrometeorological sensors, real-time predictions, historical trends,
    and interactive parameter simulation.
    """
    env_col = get_env_data_col()
    loc_col = get_locations_col()
    locations = list(loc_col.find({"status": "ACTIVE"}).sort("location_name", 1))

    # Selected location filter
    selected_loc = request.GET.get('location', locations[0]['location_name'] if locations else 'River Basin')
    
    # Latest reading for selected location
    latest = env_col.find_one({"location": selected_loc}, sort=[("timestamp", -1)])
    if not latest:
        latest = env_col.find_one(sort=[("timestamp", -1)])

    rainfall = latest.get('rainfall', 45.0) if latest else 45.0
    water_level = latest.get('water_level', 4.2) if latest else 4.2
    temp = latest.get('temperature', 28.5) if latest else 28.5
    humidity = latest.get('humidity', 75.0) if latest else 75.0

    # If user submitted simulator form
    if request.method == 'POST':
        try:
            rainfall = float(request.POST.get('rainfall', rainfall))
            water_level = float(request.POST.get('water_level', water_level))
            temp = float(request.POST.get('temperature', temp))
            humidity = float(request.POST.get('humidity', humidity))
            selected_loc = request.POST.get('location', selected_loc)
        except ValueError:
            pass

    # Real ML prediction using trained Kaggle model
    pred_res = predict_flood(rainfall, water_level, temp, humidity, location=selected_loc, save_record=(request.method == 'POST'))

    # Historical hydrological records for Chart.js
    history = list(env_col.find({"location": selected_loc}).sort("timestamp", -1).limit(10))
    history.reverse()

    history_labels = [h.get('timestamp').strftime('%m/%d %H:%M') if h.get('timestamp') else '' for h in history]
    history_rain = [h.get('rainfall', 0) for h in history]
    history_water = [h.get('water_level', 0) for h in history]

    context = {
        'locations': locations,
        'selected_loc': selected_loc,
        'rainfall': rainfall,
        'water_level': water_level,
        'temperature': temp,
        'humidity': humidity,
        'prediction': pred_res,
        'history_labels': json.dumps(history_labels),
        'history_rain': json.dumps(history_rain),
        'history_water': json.dumps(history_water)
    }
    return render(request, 'hazards/flood.html', context)

@login_required_custom
def fire_module_view(request):
    """
    Forest Fire Hazard Module
    Displays meteorological indices, fire probability, ignition danger,
    and GIS fire hazard mapping.
    """
    env_col = get_env_data_col()
    loc_col = get_locations_col()
    locations = list(loc_col.find({"status": "ACTIVE"}).sort("location_name", 1))

    selected_loc = request.GET.get('location', locations[0]['location_name'] if locations else 'Forest Zone')

    latest = env_col.find_one({"location": selected_loc}, sort=[("timestamp", -1)])
    if not latest:
        latest = env_col.find_one(sort=[("timestamp", -1)])

    temp = latest.get('temperature', 33.0) if latest else 33.0
    humidity = latest.get('humidity', 42.0) if latest else 42.0
    wind_speed = latest.get('wind_speed', 16.0) if latest else 16.0
    rainfall = latest.get('rainfall', 0.2) if latest else 0.2
    smoke_level = latest.get('smoke_level', 78.0) if latest else 78.0

    if request.method == 'POST':
        try:
            temp = float(request.POST.get('temperature', temp))
            humidity = float(request.POST.get('humidity', humidity))
            wind_speed = float(request.POST.get('wind_speed', wind_speed))
            rainfall = float(request.POST.get('rainfall', rainfall))
            smoke_level = float(request.POST.get('smoke_level', smoke_level))
            selected_loc = request.POST.get('location', selected_loc)
        except ValueError:
            pass

    # Real ML prediction using trained Kaggle model
    pred_res = predict_fire(temp, humidity, wind_speed, rainfall, smoke_level, location=selected_loc, save_record=(request.method == 'POST'))

    context = {
        'locations': locations,
        'selected_loc': selected_loc,
        'temperature': temp,
        'humidity': humidity,
        'wind_speed': wind_speed,
        'rainfall': rainfall,
        'smoke_level': smoke_level,
        'prediction': pred_res,
    }
    return render(request, 'hazards/fire.html', context)

@login_required_custom
def pollution_module_view(request):
    """
    Air Pollution Module
    Displays particulate telemetry (PM2.5, PM10), gaseous pollutants (CO, NO2, SO2),
    AQI classification, and multi-location comparisons.
    """
    env_col = get_env_data_col()
    loc_col = get_locations_col()
    locations = list(loc_col.find({"status": "ACTIVE"}).sort("location_name", 1))

    selected_loc = request.GET.get('location', locations[0]['location_name'] if locations else 'Urban Metro')

    latest = env_col.find_one({"location": selected_loc}, sort=[("timestamp", -1)])
    if not latest:
        latest = env_col.find_one(sort=[("timestamp", -1)])

    pm25 = latest.get('pm25', 65.0) if latest else 65.0
    pm10 = latest.get('pm10', 120.0) if latest else 120.0
    co = latest.get('co', 1.2) if latest else 1.2
    no2 = latest.get('no2', 45.0) if latest else 45.0
    so2 = latest.get('so2', 25.0) if latest else 25.0

    if request.method == 'POST':
        try:
            pm25 = float(request.POST.get('pm25', pm25))
            pm10 = float(request.POST.get('pm10', pm10))
            co = float(request.POST.get('co', co))
            no2 = float(request.POST.get('no2', no2))
            so2 = float(request.POST.get('so2', so2))
            selected_loc = request.POST.get('location', selected_loc)
        except ValueError:
            pass

    pred_res = predict_pollution(pm25, pm10, co, no2, so2, location=selected_loc, save_record=(request.method == 'POST'))

    # Comparison across all locations
    comparison_data = []
    for loc in locations:
        lname = loc['location_name']
        rec = env_col.find_one({"location": lname}, sort=[("timestamp", -1)])
        if rec:
            comparison_data.append({
                "location": lname,
                "pm25": rec.get('pm25', 0),
                "pm10": rec.get('pm10', 0),
                "aqi": rec.get('aqi', 0),
                "status": "Critical" if rec.get('aqi', 0) > 200 else ("High" if rec.get('aqi', 0) > 100 else "Moderate")
            })

    # Historical trend for selected location
    history = list(env_col.find({"location": selected_loc}).sort("timestamp", -1).limit(10))
    history.reverse()
    history_labels = [h.get('timestamp').strftime('%m/%d %H:%M') if h.get('timestamp') else '' for h in history]
    history_aqi = [h.get('aqi', 0) for h in history]
    history_pm25 = [h.get('pm25', 0) for h in history]

    context = {
        'locations': locations,
        'selected_loc': selected_loc,
        'pm25': pm25,
        'pm10': pm10,
        'co': co,
        'no2': no2,
        'so2': so2,
        'prediction': pred_res,
        'comparison_data': comparison_data,
        'history_labels': json.dumps(history_labels),
        'history_aqi': json.dumps(history_aqi),
        'history_pm25': json.dumps(history_pm25),
    }
    return render(request, 'hazards/pollution.html', context)

@login_required_custom
def ml_performance_view(request):
    """
    ML Model Performance Audit Page
    Displays real, un-fabricated evaluation metrics, algorithm comparisons,
    and confusion matrices loaded directly from model_metadata.json.
    """
    metadata = load_model_metadata()
    return render(request, 'ml_performance/index.html', {'metadata': metadata})
