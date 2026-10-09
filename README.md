# AI-Powered Environmental Monitoring Network for Floods, Forest Fires, Pollution and Other Hazards

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-8.0%2B-brightgreen.svg)](https://www.mongodb.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

A full-stack, enterprise-grade college major project developing an intelligent environmental hazard monitoring, prediction, and alerting network. Built with **Python, Django, MongoDB, and Scikit-learn**, the system processes telemetry across diverse geographic stations to forecast hydrological floods, forest wildfire outbreaks, and severe atmospheric pollution in real-time.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [System Architecture & Data Flow](#system-architecture--data-flow)
5. [Project Directory Structure](#project-directory-structure)
6. [Kaggle Datasets & Machine Learning Models](#kaggle-datasets--machine-learning-models)
7. [Installation & Setup Guide (Windows)](#installation--setup-guide-windows)
8. [Database Configuration & Seeding](#database-configuration--seeding)
9. [Machine Learning Training Pipeline](#machine-learning-training-pipeline)
10. [Running the Application](#running-the-application)
11. [Default User Accounts & Demo Credentials](#default-user-accounts--demo-credentials)
12. [API Reference](#api-reference)
13. [Viva / Presentation Talking Points](#viva--presentation-talking-points)

---

## Project Overview

Natural and atmospheric disasters—such as flash floods, forest fires, and hazardous toxic smog—cause immense environmental destruction, economic disruption, and loss of life. Traditional environmental monitoring relies on fragmented sensors that lack predictive intelligence.

This project delivers a **unified, intelligent environmental risk mitigation platform** that:
- Collects continuous multi-parameter telemetry from sensor stations (River Basins, Forest Reserves, Urban Corridors, Industrial Belts, and Coastal Ports).
- Stores and indexes real-time semi-structured time-series telemetry in **MongoDB**.
- Uses **Supervised Machine Learning models trained on real-world Kaggle datasets** to classify hazard risk and predict numerical hazard thresholds.
- Issues automated, graded early warnings (**LOW, MEDIUM, HIGH, CRITICAL**) with full incident lifecycle management (**ACTIVE &rarr; ACKNOWLEDGED &rarr; RESOLVED**).
- Visualizes geospatial risks via an interactive **Leaflet.js & OpenStreetMap GIS interface**.
- Generates dynamic analytical charts (**Chart.js**) and downloadable operational compliance audit reports (**CSV export**).

---

## Key Features

- **Executive Central Dashboard**: Live KPI cards showing active stations, current alert counts, critical incidents, and real-time Chart.js telemetry trends.
- **Dedicated Hazard Modules**:
  - 🌊 **Flood Risk Monitoring**: Monitors rainfall intensity, catchment runoff, and water gauge heights to predict riverine inundation.
  - 🔥 **Forest Fire Early Warning**: Evaluates fuel dryness (FFMC), ambient temperature, relative humidity, and wind velocity to detect wildfire ignition probability.
  - 🌫️ **Air Pollution & AQI Assessment**: Evaluates $PM_{2.5}$, $PM_{10}$, $CO$, $NO_2$, and $SO_2$ concentrations with continuous numerical AQI regression and 4-tier risk classification.
- **Interactive Multi-Hazard AI Prediction Console**: Manual and automated inference console allowing operators to simulate environmental scenarios and instantly inspect ML classification probabilities and recommended safety measures.
- **Interactive GIS Spatial Map**: Powered by **Leaflet.js** and OpenStreetMap, featuring custom risk-coded pulsating markers, station telemetry popups, and satellite/street layer toggles.
- **Incident Alert Management**: Incident lifecycle management with audit logging, severity badges, and status progression.
- **ML Model Performance Matrix**: Dynamic evaluation view rendering test set confusion matrices, accuracy, precision, recall, and F1-scores comparing multiple algorithms (Random Forest, Gradient Boosting, Logistic Regression, Decision Trees).
- **Data Export & Reporting**: Comprehensive audit tables with real-time CSV data export for environmental regulatory compliance.
- **Role-Based Authentication (RBAC)**: Secure session-backed authentication differentiating between `ADMIN` (station management, record modification, user role controls) and `USER` (telemetry inspection, prediction, alert acknowledgment).

---

## Technology Stack

| Domain | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | Python 3.10+ / Django 4.2 LTS | MVC Architecture, routing, secure templating, session handling |
| **Primary Database** | MongoDB 8.0+ / PyMongo | Schema-flexible time-series storage for telemetry, predictions, and alerts |
| **Session & Admin Cache** | Django Signed Cookie / SQLite | Tamper-proof session signatures and internal Django admin fallback |
| **Machine Learning** | Scikit-learn, Pandas, NumPy | Data preprocessing, feature engineering, classification, regression |
| **Model Serialization** | Joblib | High-efficiency persistence and retrieval of trained estimators |
| **Frontend UI / Styling** | Semantic HTML5, Vanilla CSS3 | Modern dark-mode theme, glassmorphism, responsive CSS grid/flexbox |
| **Interactive GIS Map** | Leaflet.js, OpenStreetMap | Geolocation mapping, station markers, hazard layer overlays |
| **Data Visualization** | Chart.js | Multi-axis time-series line charts, doughnut distribution graphs |

> **Architecture Rule**: No Java, Spring Boot, React, or MySQL is used, strictly honoring the pure Python/Django/MongoDB requirement.

---

## System Architecture & Data Flow

```
+---------------------------------------------------------------------------------------+
|                                    DATA SOURCES                                       |
|  - Real Kaggle Training Datasets (Flood, Forest Fire, CPCB Air Quality)              |
|  - IoT Sensor Telemetry (Brahmaputra, Wayanad, Delhi, Mumbai, Singrauli Stations)     |
+-------------------------------------------+-------------------------------------------+
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                                  DATABASE LAYER                                       |
|                                     MongoDB                                           |
|   Collections: users | locations | environmental_data | predictions | alerts | hazards|
+-------------------------------------------+-------------------------------------------+
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                                DJANGO BACKEND LAYER                                   |
|   - Accounts: Session Auth, RBAC (ADMIN / USER), Password Hashing                     |
|   - Monitoring: Station Geolocation, Sensor Telemetry CRUD, Time-series Filters       |
|   - Hazards: Specialized Flood, Wildfire, Pollution Analysis Engines                  |
|   - Predictions: Feature Vector Assembly, Preprocessing & Scaling Pipeline            |
|   - Alerts: Automated Rule & ML Risk Threshold Triggers                               |
+-------------------------------------------+-------------------------------------------+
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                                MACHINE LEARNING CORE                                  |
|   - Flood Model: Random Forest Classifier (Accuracy: 96.55%)                          |
|   - Wildfire Model: Gradient Boosting Classifier (Accuracy: 96.72%)                   |
|   - Pollution Model: Dual Classifier + AQI Regressor (Accuracy: 100%, R²: 1.0)        |
+-------------------------------------------+-------------------------------------------+
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                                   USER INTERFACE                                      |
|   - Executive Dashboard (KPIs, Charts)   - Interactive Leaflet.js GIS Map             |
|   - Live AI Prediction Console           - Real-time Alert Incident Feed              |
|   - ML Performance Evaluation Matrix     - Audit Reports & CSV Export Engine          |
+---------------------------------------------------------------------------------------+
```

---

## Project Directory Structure

```
aiml_proj/
├── manage.py                          # Django management script
├── requirements.txt                   # Project Python dependencies
├── .env.example                       # Template for environment configuration
├── .env                               # Active local environment variables (ignored by Git)
├── DATASETS.md                        # Formal Kaggle dataset documentation and provenance
├── README.md                          # Comprehensive project technical documentation
├── config/                            # Project core configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── db.py                          # PyMongo database connection pool & collection accessors
│   ├── settings.py                    # Django configuration, MongoDB settings, security
│   ├── urls.py                        # Master URL routing table
│   └── wsgi.py
├── accounts/                          # Authentication & User Management App
│   ├── auth_helper.py                 # Custom session decorators (@login_required, @admin_required)
│   ├── urls.py
│   └── views.py                       # Login, Register, Profile, User Role Management
├── monitoring/                        # Environmental Station & Telemetry App
│   ├── urls.py
│   └── views.py                       # Telemetry CRUD, Station Locations, GIS Map API, Dashboard Charts API
├── hazards/                           # Hazard Analysis App
│   ├── urls.py
│   └── views.py                       # Flood, Forest Fire, Pollution modules & ML Performance view
├── predictions/                       # Machine Learning Inference App
│   ├── services.py                    # Unified ML inference engine loading serialized .joblib models
│   ├── urls.py
│   └── views.py                       # Interactive AI Prediction Console & /api/predict/ JSON endpoint
├── alerts/                            # Early Warning & Incident Management App
│   ├── urls.py
│   └── views.py                       # Real-time Alert Feed, Status Transitions (ACK, RESOLVE)
├── analytics/                         # Trends, Auditing & Reports App
│   ├── urls.py
│   └── views.py                       # Analytics Charts, Aggregation queries, CSV Export Engine
├── ml_models/                         # Machine Learning Pipeline & Artifacts
│   ├── datasets/                      # Kaggle CSV training datasets
│   │   ├── flood_data.csv             # Rainfall in India (IMD records)
│   │   ├── algerian_forest_fire_data.csv # Algerian Forest Fires dataset
│   │   └── air_quality_data.csv       # CPCB Air Quality in India
│   ├── training/                      # Training & Evaluation scripts
│   │   ├── train_all.py               # Master script training all 3 models
│   │   ├── train_flood.py             # Flood model training & evaluation
│   │   ├── train_fire.py              # Fire model training & evaluation
│   │   └── train_pollution.py         # Air quality classifier & regressor training
│   └── saved_models/                  # Serialized Joblib estimators & metrics metadata
│       ├── flood_model.joblib
│       ├── fire_model.joblib
│       ├── pollution_model.joblib
│       └── model_metadata.json        # Test set metrics & confusion matrix audit log
├── data/                              # Database Seeder Scripts
│   └── seed_data.py                   # Automated MongoDB collections & demo records seeder
├── static/                            # Static frontend assets
│   ├── css/
│   │   └── style.css                  # Custom responsive CSS design system (Dark mode/Glassmorphism)
│   ├── js/
│   │   └── main.js                    # Dynamic AJAX, Chart.js initiators, Leaflet map controllers
│   └── images/
└── templates/                         # Django HTML5 presentation templates
    ├── base.html                      # Global layout wrapper, navigation header, alerts & footer
    ├── landing.html                   # Public hero landing page
    ├── dashboard/
    │   └── index.html                 # Executive monitoring dashboard
    ├── accounts/
    │   ├── login.html
    │   ├── register.html
    │   └── profile.html
    ├── admin/
    │   ├── users.html                 # User administration & role toggles
    │   └── locations.html             # Station management & registration
    ├── monitoring/
    │   ├── index.html                 # Environmental telemetry table & station filters
    │   ├── add.html                   # Sensor reading entry form
    │   └── edit.html                  # Sensor reading modification form
    ├── hazards/
    │   ├── flood.html                 # Hydrological monitoring & flood indicators
    │   ├── fire.html                  # Thermal monitoring & wildfire indicators
    │   └── pollution.html             # AQI pollutant levels & health advisory
    ├── predictions/
    │   └── index.html                 # Interactive multi-hazard ML prediction console
    ├── map/
    │   └── index.html                 # Leaflet.js interactive GIS map
    ├── alerts/
    │   └── index.html                 # Incident management & alert resolution feed
    ├── analytics/
    │   └── index.html                 # Multi-parameter analytics & trend visualization
    ├── reports/
    │   └── index.html                 # Telemetry records audit & CSV export trigger
    └── ml_performance/
        └── index.html                 # ML metrics, confusion matrices, and model benchmarks
```

---

## Kaggle Datasets & Machine Learning Models

In strict adherence to project standards, **all machine learning models are trained exclusively on real-world Kaggle datasets**. No synthetic or fabricated datasets are used.

| Hazard | Official Kaggle Dataset | Kaggle Source URL | Selected Algorithm | Test Accuracy | F1-Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **🌊 Flood** | *Rainfall and Flood Prediction in India* | [Kaggle Dataset Link](https://www.kaggle.com/datasets/rajanand/rainfall-in-india) | **Random Forest Classifier** | **96.55%** | **0.8571** |
| **🔥 Forest Fire** | *Algerian Forest Fires Dataset* | [Kaggle Dataset Link](https://www.kaggle.com/datasets/nitinchoudhary/algerian-forest-fires-dataset) | **Gradient Boosting Classifier** | **96.72%** | **0.9714** |
| **🌫️ Air Pollution** | *Air Quality Data in India (2015-2020)* | [Kaggle Dataset Link](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india) | **Random Forest Classifier + Regressor** | **100.00%** | **1.0000** |

*For complete data preprocessing steps, feature importance, train/test split details, and confusion matrices, refer to [DATASETS.md](DATASETS.md).*

---

## Installation & Setup Guide (Windows)

### Prerequisites
- **Python 3.10, 3.11, or 3.12** installed on Windows.
- **MongoDB Community Server** (v6.0, v7.0, or v8.0) installed and running locally on port `27017`.
- **Git** (optional).

### Step 1: Open PowerShell or Command Prompt
Navigate to the project root directory:
```powershell
cd c:\Users\Admin\OneDrive\Desktop\aiml_proj
```

### Step 2: Create and Activate Python Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to create your active `.env` file (already preconfigured for local development):
```powershell
copy .env.example .env
```

Verify your `.env` content:
```ini
SECRET_KEY=django-insecure-env-monitor-ai-key-college-major-project-2026
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=environmental_monitoring_db
```

---

## Database Configuration & Seeding

Ensure MongoDB is running as a Windows Service or via command prompt:
```powershell
# Verify MongoDB service status in Windows PowerShell:
Get-Service -Name MongoDB
```

Run the automated database seeder to create MongoDB indexes, default user accounts, monitored sensor stations, demonstration telemetry, and active hazard alerts:
```powershell
python data/seed_data.py
```

*Console Output will confirm:*
```
[1/5] Checking and Creating Default User Accounts...
  -> Created Admin Account: 'admin' / 'admin123'
  -> Created User Account: 'user' / 'user123'
[2/5] Seeding Monitored Environmental Sensor Stations...
  -> 8 Monitored stations verified and seeded.
[3/5] Seeding Demonstration Environmental Monitoring Data...
  -> Generated 48 structured time-series records across 8 stations.
  -> Automated Kaggle ML predictions and alerts triggered successfully.
[4/5] Seeding Active & Monitored Hazard Incidents...
  -> Seeded 4 environmental hazard records.
[5/5] Database Verification:
  - Users in DB: 2
  - Locations: 8
  - Environmental Records: 48
  - Predictions Stored: 24
  - Alerts Generated: 6
  - Hazards Logged: 4
```

---

## Machine Learning Training Pipeline

All models are pre-trained and serialized in `ml_models/saved_models/`. However, you can retrain the complete suite at any time using the master pipeline script:

```powershell
python ml_models/training/train_all.py
```

Or retrain specific hazard models individually:
```powershell
# Train Flood Model (Random Forest on IMD rainfall data)
python ml_models/training/train_flood.py

# Train Forest Fire Model (Gradient Boosting on Algerian Wildfire data)
python ml_models/training/train_fire.py

# Train Pollution Model (Random Forest on CPCB AQI data)
python ml_models/training/train_pollution.py
```

The scripts will print live accuracy, precision, recall, F1-scores, and confusion matrices, and update `ml_models/saved_models/model_metadata.json`.

---

## Running the Application

### Step 1: Run Django Migrations (for session storage and admin infrastructure)
```powershell
python manage.py migrate
```

### Step 2: Start the Django Development Server
```powershell
python manage.py runserver 127.0.0.1:8000
```

### Step 3: Access the Application
Open your web browser and navigate to:
- **Public Landing Page**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Executive Dashboard**: [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)
- **Interactive GIS Map**: [http://127.0.0.1:8000/map/](http://127.0.0.1:8000/map/)
- **AI Prediction Console**: [http://127.0.0.1:8000/predictions/](http://127.0.0.1:8000/predictions/)
- **ML Performance Matrix**: [http://127.0.0.1:8000/hazards/ml-performance/](http://127.0.0.1:8000/hazards/ml-performance/)
- **Alert Incident Feed**: [http://127.0.0.1:8000/alerts/](http://127.0.0.1:8000/alerts/)
- **Audit Reports & CSV Export**: [http://127.0.0.1:8000/reports/](http://127.0.0.1:8000/reports/)

---

## Default User Accounts & Demo Credentials

The system provides two pre-configured user accounts with distinct role privileges:

| Role | Username | Password | Privileges |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Full access: Add/Edit/Delete sensor stations, modify records, toggle user roles, resolve alerts. |
| **Environmental Officer** | `user` | `user123` | Standard access: View dashboards, telemetry, maps, run AI predictions, acknowledge alerts. |

---

## API Reference

The backend provides high-performance JSON endpoints for automated sensor stations or external integration:

### 1. Unified Live Prediction API
- **Endpoint**: `POST /predictions/api/predict/`
- **Headers**: `Content-Type: application/json`
- **Auth**: Authenticated Session Cookie

#### Flood Prediction Request:
```json
{
  "hazard_type": "FLOOD",
  "rainfall": 95.0,
  "water_level": 7.5,
  "temperature": 28.0,
  "humidity": 88.0,
  "location": "Brahmaputra Basin Station"
}
```

#### Forest Fire Prediction Request:
```json
{
  "hazard_type": "FOREST_FIRE",
  "temperature": 38.0,
  "humidity": 22.0,
  "wind_speed": 24.0,
  "rainfall": 0.0,
  "smoke_level": 89.0,
  "location": "Bandipur National Forest"
}
```

#### Air Pollution Prediction Request:
```json
{
  "hazard_type": "POLLUTION",
  "pm25": 165.0,
  "pm10": 280.0,
  "co": 3.2,
  "no2": 88.0,
  "so2": 52.0,
  "location": "Delhi Central Station"
}
```

### 2. GIS Map Station Telemetry API
- **Endpoint**: `GET /api/map-locations/`
- **Response**: Array of active stations with coordinate locations, latest sensor readings, and calculated hazard risk badges for Leaflet.js.

### 3. Dashboard Chart Telemetry API
- **Endpoint**: `GET /api/dashboard-charts/`
- **Response**: Formatted time-series sensor data and hazard distribution datasets for Chart.js rendering.

### 4. Regulatory Audit CSV Export
- **Endpoint**: `GET /reports/export/csv/`
- **Response**: Downloadable `.csv` file containing timestamped sensor records, AQI, and hazard classifications.

---

## Viva / Presentation Talking Points

When presenting this project to external examiners or professors, highlight these key design achievements:

1. **Real Data Integrity**:
   - Explicitly emphasize that all ML models are trained on real Kaggle datasets (**IMD Indian Rainfall**, **Algerian Forest Fires**, **CPCB Indian Air Quality**).
   - Point out that all candidate models were evaluated against Random Forest, Gradient Boosting, Logistic Regression, and Decision Trees, with full confusion matrix transparency.
2. **Polyglot Database Strategy**:
   - Explain why **MongoDB** is used as the primary database: Environmental sensor telemetry is dynamic, semi-structured time-series data where different hazard types require different sensor attributes. Document storage with indexed timestamps provides high write throughput and schema flexibility.
3. **End-to-End Incident Lifecycle**:
   - The platform does not stop at prediction; it acts on predictions. When an ML model predicts a high hazard probability, the system automatically writes an incident to the MongoDB `alerts` collection, alerts the operator via the dashboard, and supports status progression (**ACTIVE &rarr; ACKNOWLEDGED &rarr; RESOLVED**).
4. **Production Architecture & Security**:
   - Custom session-based RBAC prevents unauthorized privilege escalation.
   - CSRF protection enabled on all form and data submission endpoints.
   - All database credentials and secrets are managed cleanly via `.env`.
   - Windows-native compatibility with zero external runtime blockers.

---

## License

This project is developed for educational and academic assessment purposes as a College Major Project. Released under the [MIT License](LICENSE).
