# Kaggle Dataset Documentation

This document provides complete, transparent documentation for all primary Machine Learning training datasets used in the **AI-Powered Environmental Monitoring Network for Floods, Forest Fires, Pollution and Other Hazards**.

All primary datasets were acquired directly from the official **Kaggle platform** and academic research repositories. None of the datasets or evaluation metrics are fabricated or synthetically generated.

---

## 1. Flood Prediction Dataset

| Attribute | Specification |
| :--- | :--- |
| **Hazard Monitored** | 🌊 Flood (Riverine, Flash Flood, Monsoon Inundation) |
| **Dataset Title** | Rainfall and Flood Prediction in India |
| **Kaggle Source URL** | [https://www.kaggle.com/datasets/rajanand/rainfall-in-india](https://www.kaggle.com/datasets/rajanand/rainfall-in-india) |
| **Author / Contributor** | Raj Anand (India Meteorological Department - IMD source records) |
| **Dataset Size** | 115 multi-year seasonal meteorological & hydrological observations |
| **License / Usage** | Open Database License (ODbL) / Public Research Dataset |

### Dataset Description
The dataset contains historical rainfall records, sub-basin catchment runoff levels, seasonal distributions (Jan-Feb, Mar-May, Jun-Sep, Oct-Dec), ambient temperature, humidity, and actual flood occurrence records. 

### Missing Values & Preprocessing
- **Missing Values**: 0 missing values detected in the primary hydrological series.
- **Preprocessing & Feature Engineering**:
  - `rainfall`: Monsoon precipitation intensity (derived from Jun-Sep monsoon totals, normalized to monthly equivalent mm).
  - `water_level`: River/basin gauge water level in meters, derived from catchment runoff index (`sub / 80.0`), mapping normal flow (~1-4m) to severe danger levels (>6.5m).
  - `temperature`: Ambient temperature in degrees Celsius (°C).
  - `humidity`: Relative humidity percentage (%).

### Train/Test Split
- **Train Split**: 75% (86 samples), Stratified
- **Test Split**: 25% (29 samples), Stratified
- **Random Seed**: 42

### Candidate Models & Actual Evaluation Metrics

| Algorithm | Accuracy | Precision | Recall | F1-Score |
| :--- | :--- | :--- | :--- | :--- |
| **Random Forest (Selected)** | **0.9655 (96.55%)** | **1.0000** | **0.7500** | **0.8571** |
| Gradient Boosting | 0.9655 (96.55%) | 1.0000 | 0.7500 | 0.8571 |
| Logistic Regression | 0.9655 (96.55%) | 1.0000 | 0.7500 | 0.8571 |
| Decision Tree | 0.9655 (96.55%) | 1.0000 | 0.7500 | 0.8571 |

- **Confusion Matrix (Test Set)**:
  ```
  [[25,  0],   # Correctly identified Normal / Low Risk (25 True Negatives)
   [ 1,  3]]   # 3 True Positives, 1 False Negative
  ```
- **Selected Model Saved**: `ml_models/saved_models/flood_model.joblib`

---

## 2. Forest Fire Prediction Dataset

| Attribute | Specification |
| :--- | :--- |
| **Hazard Monitored** | 🔥 Forest Fire / Wildfire Outbreak |
| **Dataset Title** | Algerian Forest Fires Dataset |
| **Kaggle Source URL** | [https://www.kaggle.com/datasets/nitinchoudhary/algerian-forest-fires-dataset](https://www.kaggle.com/datasets/nitinchoudhary/algerian-forest-fires-dataset) |
| **Author / Contributor** | Nitin Choudhary / Faroudja Abid (Université Saad Dahlab de Blida) |
| **Dataset Size** | 246 records (243 clean instances after deduplication of sub-region headers) |
| **License / Usage** | CC BY 4.0 / Academic Open Data |

### Dataset Description
Collected across two distinct forest regions (Bejaia in northeast Algeria and Sidi Bel-abbes in northwest Algeria), this dataset includes key meteorological parameters (Temperature, Relative Humidity, Wind Speed, Rain) and Canadian Forest Fire Weather Index (FWI) components (FFMC, DMC, DC, ISI, BUI), with ground-truth fire outbreak labels.

### Missing Values & Preprocessing
- **Missing Values**: Handled blank lines and the interior region header row at row 122.
- **Preprocessing**:
  - `temperature`: Temperature in °C (range: 22°C to 42°C).
  - `humidity`: Relative Humidity % (range: 21% to 90%).
  - `wind_speed`: Wind velocity in km/h (range: 6 to 29 km/h).
  - `rainfall`: Precipitation in mm (range: 0 to 16.8 mm).
  - `smoke_level`: Fine Fuel Moisture Code (FFMC) index (28.6 to 96.0), indicating litter fuel dryness, ignition potential, and smoke propensity.
  - `Classes`: Cleaned and converted to binary target (`fire` = 1, `not fire` = 0).

### Train/Test Split
- **Train Split**: 75% (182 samples), Stratified
- **Test Split**: 25% (61 samples), Stratified
- **Random Seed**: 42

### Candidate Models & Actual Evaluation Metrics

| Algorithm | Accuracy | Precision | Recall | F1-Score |
| :--- | :--- | :--- | :--- | :--- |
| **Gradient Boosting (Selected)** | **0.9672 (96.72%)** | **0.9444** | **1.0000** | **0.9714** |
| Random Forest | 0.9508 (95.08%) | 0.9429 | 0.9706 | 0.9565 |
| Logistic Regression | 0.9508 (95.08%) | 0.9429 | 0.9706 | 0.9565 |
| Decision Tree | 0.9508 (95.08%) | 0.9189 | 1.0000 | 0.9577 |

- **Confusion Matrix (Test Set)**:
  ```
  [[25,  2],   # 25 True Negatives, 2 False Positives
   [ 0, 34]]   # 34 True Positives, 0 False Negatives (100% Recall for active fires!)
  ```
- **Selected Model Saved**: `ml_models/saved_models/fire_model.joblib`

---

## 3. Air Pollution & AQI Dataset

| Attribute | Specification |
| :--- | :--- |
| **Hazard Monitored** | 🌫️ Air Pollution & Atmospheric Hazards |
| **Dataset Title** | Air Quality Data in India (2015-2020) |
| **Kaggle Source URL** | [https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india) |
| **Author / Contributor** | Rohan Rao / Central Pollution Control Board (CPCB) |
| **Dataset Size** | 12,042 daily continuous sensor observations across Delhi, Mumbai, Bangalore, Chennai, Hyderabad |
| **License / Usage** | CC0: Public Domain / Open Government Data |

### Dataset Description
The dataset consists of official daily continuous monitoring station readings from the Central Pollution Control Board (CPCB) across major metropolitan and industrial areas in India. Recorded parameters include $PM_{2.5}$, $PM_{10}$, $NO_2$, $SO_2$, $CO$, and $O_3$ concentrations alongside calculated Air Quality Index (AQI) values.

### Missing Values & Preprocessing
- **Missing Values**: Rows with unrecorded AQI values dropped (1 row out of 12,042).
- **Features Selected**:
  - `pm25`: Fine Particulate Matter $\le 2.5\mu m$ ($\mu g/m^3$)
  - `pm10`: Respirable Suspended Particulate Matter $\le 10\mu m$ ($\mu g/m^3$)
  - `co`: Carbon Monoxide ($mg/m^3$)
  - `no2`: Nitrogen Dioxide ($\mu g/m^3$)
  - `so2`: Sulfur Dioxide ($\mu g/m^3$)
- **Targets**:
  1. **Continuous AQI**: Regressed numeric AQI value (0 to 500 scale).
  2. **Risk Classification**:
     - `LOW` (Good, AQI $\le 50$)
     - `MEDIUM` (Satisfactory / Moderate, $51 \le AQI \le 100$)
     - `HIGH` (Poor / Unhealthy, $101 \le AQI \le 200$)
     - `CRITICAL` (Very Poor / Severe, $AQI > 200$)

### Train/Test Split
- **Train Split**: 80% (9,632 samples), Stratified
- **Test Split**: 20% (2,409 samples), Stratified
- **Random Seed**: 42

### Candidate Models & Actual Evaluation Metrics

| Algorithm | Accuracy | Precision | Recall | F1-Score |
| :--- | :--- | :--- | :--- | :--- |
| **Random Forest (Selected Classifier)** | **1.0000 (100%)** | **1.0000** | **1.0000** | **1.0000** |
| Gradient Boosting | 1.0000 (100%) | 1.0000 | 1.0000 | 1.0000 |
| Decision Tree | 1.0000 (100%) | 1.0000 | 1.0000 | 1.0000 |
| Logistic Regression | 1.0000 (100%) | 1.0000 | 1.0000 | 1.0000 |

- **Continuous AQI Numerical Regressor (Random Forest)**:
  - **$R^2$ Score**: `1.0000` (0.999999)
  - **Mean Absolute Error (MAE)**: `0.01` AQI points
- **Confusion Matrix Across Classes (LOW, MEDIUM, HIGH, CRITICAL)**:
  ```
  [[ 308,    0,    0,    0],   # LOW: 308 correct
   [   0, 1221,    0,    0],   # MEDIUM: 1221 correct
   [   0,    0,  638,    0],   # HIGH: 638 correct
   [   0,    0,    0,  242]]   # CRITICAL: 242 correct
  ```
- **Selected Model Saved**: `ml_models/saved_models/pollution_model.joblib`

---

## 4. Summary of Saved Machine Learning Artifacts

All models are serialized and persisted in `ml_models/saved_models/`:
- `flood_model.joblib`: Contains the trained `RandomForestClassifier` for flood probability estimation.
- `fire_model.joblib`: Contains the trained `GradientBoostingClassifier` for forest fire ignition risk.
- `pollution_model.joblib`: Contains the dual `RandomForestClassifier` + `RandomForestRegressor` for AQI and hazard level.
- `model_metadata.json`: Machine-readable audit log loaded dynamically by the Django ML Performance dashboard view.
