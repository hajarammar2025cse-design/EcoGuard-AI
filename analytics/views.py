"""
Analytics & Environmental Reporting Module
Aggregates longitudinal sensor trends, pollutant concentrations,
risk classifications, and generates downloadable/printable auditing reports.
"""
import csv
import json
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from accounts.auth_helper import login_required_custom
from config.db import (
    get_env_data_col, get_locations_col, get_alerts_col,
    get_predictions_col, serialize_docs
)

@login_required_custom
def analytics_view(request):
    """
    Longitudinal Environmental & Pollution Analytics
    """
    loc_col = get_locations_col()
    locations = list(loc_col.find({"status": "ACTIVE"}).sort("location_name", 1))

    selected_location = request.GET.get('location', 'ALL')
    selected_range = request.GET.get('range', '30d')  # 7d, 30d, 90d, all

    context = {
        'locations': locations,
        'selected_location': selected_location,
        'selected_range': selected_range
    }
    return render(request, 'analytics/index.html', context)

@login_required_custom
def api_analytics_data(request):
    """
    JSON API feeding multi-axis Chart.js visualizations
    """
    env_col = get_env_data_col()
    alert_col = get_alerts_col()
    pred_col = get_predictions_col()

    location = request.GET.get('location', 'ALL')
    time_range = request.GET.get('range', '30d')

    query = {}
    if location and location != 'ALL':
        query['location'] = location

    # Date cutoff
    now = datetime.utcnow()
    if time_range == '7d':
        query['timestamp'] = {'$gte': now - timedelta(days=7)}
    elif time_range == '30d':
        query['timestamp'] = {'$gte': now - timedelta(days=30)}
    elif time_range == '90d':
        query['timestamp'] = {'$gte': now - timedelta(days=90)}

    cursor = env_col.find(query).sort("timestamp", 1).limit(30)
    records = list(cursor)

    labels = []
    temps = []
    humidity = []
    rainfall = []
    wind = []
    aqi = []
    pm25 = []
    pm10 = []
    co = []
    no2 = []
    so2 = []

    for r in records:
        ts = r.get('timestamp')
        date_str = ts.strftime('%m/%d %H:%M') if isinstance(ts, datetime) else 'T'
        labels.append(f"{r.get('location', '')[:5]} {date_str}")
        temps.append(r.get('temperature', 0))
        humidity.append(r.get('humidity', 0))
        rainfall.append(r.get('rainfall', 0))
        wind.append(r.get('wind_speed', 0))
        aqi.append(r.get('aqi', 0))
        pm25.append(r.get('pm25', 0))
        pm10.append(r.get('pm10', 0))
        co.append(r.get('co', 0))
        no2.append(r.get('no2', 0))
        so2.append(r.get('so2', 0))

    # Hazards count
    flood_alerts = alert_col.count_documents({"alert_type": "FLOOD"})
    fire_alerts = alert_col.count_documents({"alert_type": "FOREST_FIRE"})
    pollution_alerts = alert_col.count_documents({"alert_type": "AIR_POLLUTION"})

    # Risk levels count
    low_count = pred_col.count_documents({"risk_level": "LOW"})
    med_count = pred_col.count_documents({"risk_level": "MEDIUM"})
    high_count = pred_col.count_documents({"risk_level": "HIGH"})
    crit_count = pred_col.count_documents({"risk_level": "CRITICAL"})

    return JsonResponse({
        "labels": labels,
        "meteorological": {
            "temperature": temps,
            "humidity": humidity,
            "rainfall": rainfall,
            "wind_speed": wind
        },
        "pollution": {
            "aqi": aqi,
            "pm25": pm25,
            "pm10": pm10,
            "co": co,
            "no2": no2,
            "so2": so2
        },
        "hazard_counts": [flood_alerts, fire_alerts, pollution_alerts],
        "risk_counts": [low_count, med_count, high_count, crit_count]
    })

@login_required_custom
def reports_view(request):
    """
    Environmental Summary and Printable Executive Report View
    """
    loc_col = get_locations_col()
    env_col = get_env_data_col()
    alert_col = get_alerts_col()
    pred_col = get_predictions_col()

    location_filter = request.GET.get('location', 'ALL')
    query = {}
    if location_filter and location_filter != 'ALL':
        query['location'] = location_filter

    records = list(env_col.find(query).sort("timestamp", -1))
    locations = list(loc_col.find({"status": "ACTIVE"}).sort("location_name", 1))

    # Calculate summaries
    total_samples = len(records)
    avg_temp = round(sum(r.get('temperature', 0) for r in records) / total_samples, 1) if total_samples else 0.0
    total_rainfall = round(sum(r.get('rainfall', 0) for r in records), 1)
    avg_aqi = round(sum(r.get('aqi', 0) for r in records) / total_samples, 1) if total_samples else 0.0

    total_alerts = alert_col.count_documents(query)
    flood_preds = pred_col.count_documents({**query, "hazard_type": "FLOOD"})
    fire_preds = pred_col.count_documents({**query, "hazard_type": "FOREST_FIRE"})
    pollution_preds = pred_col.count_documents({**query, "hazard_type": "AIR_POLLUTION"})

    # High-risk locations identification
    high_risk_locs = []
    for loc in locations:
        lname = loc['location_name']
        latest = env_col.find_one({"location": lname}, sort=[("timestamp", -1)])
        if latest:
            is_risk = (latest.get('water_level', 0) >= 6.0 or latest.get('temperature', 0) >= 35.0 or latest.get('aqi', 0) >= 150)
            if is_risk:
                high_risk_locs.append({
                    "name": lname,
                    "district": loc.get('district_city', ''),
                    "water_level": latest.get('water_level', 0),
                    "temp": latest.get('temperature', 0),
                    "aqi": latest.get('aqi', 0),
                    "status": "CRITICAL" if (latest.get('water_level', 0) >= 8.0 or latest.get('aqi', 0) >= 250) else "HIGH"
                })

    context = {
        'locations': locations,
        'selected_location': location_filter,
        'records': serialize_docs(records[:25]),
        'total_samples': total_samples,
        'avg_temperature': avg_temp,
        'total_rainfall': total_rainfall,
        'avg_aqi': avg_aqi,
        'total_alerts': total_alerts,
        'flood_preds': flood_preds,
        'fire_preds': fire_preds,
        'pollution_preds': pollution_preds,
        'high_risk_locs': high_risk_locs,
        'generated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    }
    return render(request, 'reports/index.html', context)

@login_required_custom
def export_csv_view(request):
    """
    Exports filtered environmental monitoring data to CSV format.
    """
    env_col = get_env_data_col()
    location_filter = request.GET.get('location', 'ALL')
    query = {}
    if location_filter and location_filter != 'ALL':
        query['location'] = location_filter

    records = list(env_col.find(query).sort("timestamp", -1))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="environmental_report_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Record ID', 'Location', 'Timestamp (UTC)', 'Temperature (C)',
        'Humidity (%)', 'Rainfall (mm)', 'Water Level (m)', 'Wind Speed (km/h)',
        'PM2.5 (ug/m3)', 'PM10 (ug/m3)', 'CO (mg/m3)', 'NO2 (ug/m3)', 'SO2 (ug/m3)',
        'AQI', 'Smoke Level (FFMC)', 'Data Type'
    ])

    for r in records:
        writer.writerow([
            str(r.get('_id', '')),
            r.get('location', ''),
            r.get('timestamp').strftime('%Y-%m-%d %H:%M:%S') if r.get('timestamp') else '',
            r.get('temperature', ''),
            r.get('humidity', ''),
            r.get('rainfall', ''),
            r.get('water_level', ''),
            r.get('wind_speed', ''),
            r.get('pm25', ''),
            r.get('pm10', ''),
            r.get('co', ''),
            r.get('no2', ''),
            r.get('so2', ''),
            r.get('aqi', ''),
            r.get('smoke_level', ''),
            'Demo Monitoring Data' if r.get('is_demo', False) else 'Live Sensor Data'
        ])

    return response
