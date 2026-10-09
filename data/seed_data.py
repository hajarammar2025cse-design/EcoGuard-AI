"""
Database Seeder Script for MongoDB
Initializes Collections, Indexes, Default Admin/User Accounts,
Monitored Sensor Stations, and Initial Environmental Readings.
All demonstration monitoring records are explicitly flagged with is_demo=True
('Demo Monitoring Data') as per project documentation standards.
"""
import os
import sys
from datetime import datetime, timedelta
import random

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth.hashers import make_password
from config.db import (
    get_db, init_mongo_indexes, get_users_col, get_locations_col,
    get_env_data_col, get_hazards_col, get_alerts_col, get_predictions_col
)
from predictions.services import predict_flood, predict_fire, predict_pollution

def seed_database():
    print("=" * 65)
    print("SEEDING MONGODB ENVIRONMENTAL MONITORING DATABASE")
    print("=" * 65)

    db = get_db()
    init_mongo_indexes()

    users_col = get_users_col()
    loc_col = get_locations_col()
    env_col = get_env_data_col()
    alert_col = get_alerts_col()
    pred_col = get_predictions_col()
    hazard_col = get_hazards_col()

    # 1. Seed User Accounts
    print("\n[1/5] Checking and Creating Default User Accounts...")
    # Admin User
    if not users_col.find_one({"username": "admin"}):
        users_col.insert_one({
            "username": "admin",
            "email": "admin@environmental-network.org",
            "password": make_password("admin123"),
            "role": "ADMIN",
            "is_active": True,
            "created_at": datetime.utcnow()
        })
        print("  -> Created Admin Account: 'admin' / 'admin123'")
    else:
        print("  -> Admin account already exists.")

    # Standard User
    if not users_col.find_one({"username": "user"}):
        users_col.insert_one({
            "username": "user",
            "email": "officer@environmental-network.org",
            "password": make_password("user123"),
            "role": "USER",
            "is_active": True,
            "created_at": datetime.utcnow()
        })
        print("  -> Created User Account: 'user' / 'user123'")
    else:
        print("  -> Standard user account already exists.")

    # 2. Seed Monitored Station Locations
    print("\n[2/5] Seeding Monitored Environmental Sensor Stations...")
    default_locations = [
        {
            "location_name": "Brahmaputra Basin Station",
            "district_city": "Guwahati, Assam",
            "latitude": 26.1856,
            "longitude": 91.7478,
            "type": "RIVER_BASIN",
            "status": "ACTIVE",
            "created_at": datetime.utcnow()
        },
        {
            "location_name": "Wayanad Forest Reserve",
            "district_city": "Wayanad, Kerala",
            "latitude": 11.6854,
            "longitude": 76.1320,
            "type": "FOREST",
            "status": "ACTIVE",
            "created_at": datetime.utcnow()
        },
        {
            "location_name": "Delhi Central Station",
            "district_city": "New Delhi, Delhi",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "type": "URBAN",
            "status": "ACTIVE",
            "created_at": datetime.utcnow()
        },
        {
            "location_name": "Mumbai Harbor Station",
            "district_city": "Mumbai, Maharashtra",
            "latitude": 18.9220,
            "longitude": 72.8347,
            "type": "COASTAL",
            "status": "ACTIVE",
            "created_at": datetime.utcnow()
        },
        {
            "location_name": "Bandipur National Forest",
            "district_city": "Chamarajanagar, Karnataka",
            "latitude": 11.6664,
            "longitude": 76.6291,
            "type": "FOREST",
            "status": "ACTIVE",
            "created_at": datetime.utcnow()
        },
        {
            "location_name": "Singrauli Industrial Belt",
            "district_city": "Singrauli, Madhya Pradesh",
            "latitude": 24.1997,
            "longitude": 82.6644,
            "type": "INDUSTRIAL",
            "status": "ACTIVE",
            "created_at": datetime.utcnow()
        },
        {
            "location_name": "Kuttanad Waterways Gauge",
            "district_city": "Alappuzha, Kerala",
            "latitude": 9.4981,
            "longitude": 76.3388,
            "type": "RIVER_BASIN",
            "status": "ACTIVE",
            "created_at": datetime.utcnow()
        },
        {
            "location_name": "Manali Valley Catchment",
            "district_city": "Kullu, Himachal Pradesh",
            "latitude": 32.2396,
            "longitude": 77.1887,
            "type": "RIVER_BASIN",
            "status": "ACTIVE",
            "created_at": datetime.utcnow()
        }
    ]

    for loc in default_locations:
        loc_col.update_one(
            {"location_name": loc["location_name"]},
            {"$set": loc},
            upsert=True
        )
    print(f"  -> {len(default_locations)} Monitored stations verified and seeded.")

    # 3. Seed Environmental Sensor Telemetry (Time-series history)
    print("\n[3/5] Seeding Demonstration Environmental Monitoring Data...")
    # Clear previous demo records if needed to have a fresh clean dataset
    env_col.delete_many({"is_demo": True})
    alert_col.delete_many({})
    pred_col.delete_many({})
    hazard_col.delete_many({})

    # Sensor profiles tailored by station geography
    profiles = {
        "Brahmaputra Basin Station": {
            "temp_base": 27.0, "hum_base": 85.0, "rain_base": 85.0, "water_base": 7.2,
            "pm25": 38.0, "pm10": 65.0, "co": 0.8, "no2": 32.0, "so2": 18.0, "smoke": 40.0
        },
        "Wayanad Forest Reserve": {
            "temp_base": 31.0, "hum_base": 55.0, "rain_base": 2.0, "water_base": 2.1,
            "pm25": 22.0, "pm10": 42.0, "co": 0.5, "no2": 15.0, "so2": 10.0, "smoke": 82.0
        },
        "Delhi Central Station": {
            "temp_base": 33.0, "hum_base": 48.0, "rain_base": 0.0, "water_base": 1.8,
            "pm25": 165.0, "pm10": 280.0, "co": 3.2, "no2": 88.0, "so2": 52.0, "smoke": 65.0
        },
        "Mumbai Harbor Station": {
            "temp_base": 30.0, "hum_base": 78.0, "rain_base": 25.0, "water_base": 3.8,
            "pm25": 58.0, "pm10": 115.0, "co": 1.4, "no2": 45.0, "so2": 28.0, "smoke": 50.0
        },
        "Bandipur National Forest": {
            "temp_base": 36.5, "hum_base": 32.0, "rain_base": 0.0, "water_base": 1.4,
            "pm25": 30.0, "pm10": 55.0, "co": 0.6, "no2": 20.0, "so2": 12.0, "smoke": 89.0
        },
        "Singrauli Industrial Belt": {
            "temp_base": 34.0, "hum_base": 42.0, "rain_base": 0.5, "water_base": 2.5,
            "pm25": 145.0, "pm10": 260.0, "co": 2.8, "no2": 75.0, "so2": 95.0, "smoke": 70.0
        },
        "Kuttanad Waterways Gauge": {
            "temp_base": 28.0, "hum_base": 88.0, "rain_base": 75.0, "water_base": 6.8,
            "pm25": 25.0, "pm10": 48.0, "co": 0.6, "no2": 18.0, "so2": 14.0, "smoke": 35.0
        },
        "Manali Valley Catchment": {
            "temp_base": 21.0, "hum_base": 72.0, "rain_base": 40.0, "water_base": 4.5,
            "pm25": 18.0, "pm10": 35.0, "co": 0.4, "no2": 12.0, "so2": 8.0, "smoke": 30.0
        }
    }

    now = datetime.utcnow()
    total_records = 0

    # Generate 5 time steps (e.g., across the last 48 hours) for each station
    for loc_name, prof in profiles.items():
        for step in range(5, -1, -1):
            ts = now - timedelta(hours=step * 8)
            # Add minor natural variance
            variance = random.uniform(-0.08, 0.08)
            temp = round(prof["temp_base"] * (1 + variance), 1)
            humidity = round(min(100.0, max(15.0, prof["hum_base"] * (1 + variance))), 1)
            rainfall = round(max(0.0, prof["rain_base"] * (1 + random.uniform(-0.15, 0.15))), 1)
            water_level = round(max(0.5, prof["water_base"] * (1 + random.uniform(-0.1, 0.1))), 2)
            wind_speed = round(random.uniform(8.0, 24.0), 1)
            pm25 = round(max(5.0, prof["pm25"] * (1 + variance)), 1)
            pm10 = round(max(10.0, prof["pm10"] * (1 + variance)), 1)
            co = round(max(0.1, prof["co"] * (1 + variance)), 2)
            no2 = round(max(5.0, prof["no2"] * (1 + variance)), 1)
            so2 = round(max(3.0, prof["so2"] * (1 + variance)), 1)
            smoke = round(min(98.0, max(20.0, prof["smoke"] * (1 + variance))), 1)

            # Predict AQI with trained ML model
            pol_res = predict_pollution(pm25, pm10, co, no2, so2, location=loc_name, save_record=False)
            aqi = pol_res['prediction']

            doc = {
                "location": loc_name,
                "temperature": temp,
                "humidity": humidity,
                "rainfall": rainfall,
                "water_level": water_level,
                "wind_speed": wind_speed,
                "pm25": pm25,
                "pm10": pm10,
                "co": co,
                "no2": no2,
                "so2": so2,
                "aqi": aqi,
                "smoke_level": smoke,
                "is_demo": True,  # Explicitly labeled demonstration data
                "timestamp": ts
            }
            env_col.insert_one(doc)
            total_records += 1

            # On the latest time step (step == 0), run live ML predictions and trigger alerts
            if step == 0:
                predict_flood(rainfall, water_level, temp, humidity, location=loc_name, save_record=True, user="Automated Monitor")
                predict_fire(temp, humidity, wind_speed, rainfall, smoke, location=loc_name, save_record=True, user="Automated Monitor")
                predict_pollution(pm25, pm10, co, no2, so2, location=loc_name, save_record=True, user="Automated Monitor")

    print(f"  -> Generated {total_records} structured time-series records across 8 stations.")
    print("  -> Automated Kaggle ML predictions and alerts triggered successfully.")

    # 4. Seed Environmental Hazards records
    print("\n[4/5] Seeding Active & Monitored Hazard Incidents...")
    active_hazards = [
        {
            "location": "Brahmaputra Basin Station",
            "hazard_type": "FLOOD",
            "severity": "HIGH",
            "description": "High water levels breaching safety thresholds due to upstream catchment rainfall.",
            "detected_time": now - timedelta(hours=4),
            "status": "ACTIVE"
        },
        {
            "location": "Bandipur National Forest",
            "hazard_type": "FOREST_FIRE",
            "severity": "HIGH",
            "description": "Extreme litter dryness and elevated wind velocity creating severe ignition risk.",
            "detected_time": now - timedelta(hours=6),
            "status": "ACTIVE"
        },
        {
            "location": "Delhi Central Station",
            "hazard_type": "AIR_POLLUTION",
            "severity": "CRITICAL",
            "description": "Severe particulate accumulation (PM2.5 > 160 ug/m3) posing critical public health hazard.",
            "detected_time": now - timedelta(hours=2),
            "status": "ACTIVE"
        },
        {
            "location": "Singrauli Industrial Belt",
            "hazard_type": "AIR_POLLUTION",
            "severity": "HIGH",
            "description": "Elevated sulfur dioxide and industrial particulates exceeding NAAQS safe limits.",
            "detected_time": now - timedelta(hours=8),
            "status": "MONITORING"
        }
    ]
    for h in active_hazards:
        hazard_col.insert_one(h)
    print(f"  -> Seeded {len(active_hazards)} environmental hazard records.")

    print("\n[5/5] Database Verification:")
    print(f"  - Users in DB: {users_col.count_documents({})}")
    print(f"  - Locations: {loc_col.count_documents({})}")
    print(f"  - Environmental Records: {env_col.count_documents({})}")
    print(f"  - Predictions Stored: {pred_col.count_documents({})}")
    print(f"  - Alerts Generated: {alert_col.count_documents({})}")
    print(f"  - Hazards Logged: {hazard_col.count_documents({})}")

    print("\n" + "=" * 65)
    print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
    print("Demo Admin: username='admin' | password='admin123'")
    print("Demo User:  username='user'  | password='user123'")
    print("=" * 65)

if __name__ == '__main__':
    seed_database()
