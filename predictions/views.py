"""
Unified AI Prediction Views
Provides multi-hazard interactive inference console and prediction audit logs.
"""
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from accounts.auth_helper import login_required_custom
from config.db import get_locations_col, get_predictions_col, serialize_docs
from predictions.services import predict_flood, predict_fire, predict_pollution

@login_required_custom
def prediction_console_view(request):
    """
    Unified AI Hazard Prediction Console
    Dynamically swaps feature inputs for Flood, Forest Fire, and Air Pollution
    and evaluates risk with trained Kaggle models.
    """
    loc_col = get_locations_col()
    pred_col = get_predictions_col()
    locations = list(loc_col.find({"status": "ACTIVE"}).sort("location_name", 1))

    selected_hazard = request.POST.get('hazard_type', request.GET.get('hazard_type', 'FLOOD'))
    selected_location = request.POST.get('location', locations[0]['location_name'] if locations else 'General Sector')

    prediction_result = None

    if request.method == 'POST':
        user = request.session.get('username', 'Anonymous')
        try:
            if selected_hazard == 'FLOOD':
                rf = float(request.POST.get('rainfall', 0))
                wl = float(request.POST.get('water_level', 0))
                tp = float(request.POST.get('temperature', 25))
                hm = float(request.POST.get('humidity', 70))
                prediction_result = predict_flood(rf, wl, tp, hm, location=selected_location, save_record=True, user=user)

            elif selected_hazard == 'FOREST_FIRE':
                tp = float(request.POST.get('temperature', 30))
                hm = float(request.POST.get('humidity', 40))
                ws = float(request.POST.get('wind_speed', 15))
                rf = float(request.POST.get('rainfall', 0))
                sl = float(request.POST.get('smoke_level', 50))
                prediction_result = predict_fire(tp, hm, ws, rf, sl, location=selected_location, save_record=True, user=user)

            elif selected_hazard == 'POLLUTION':
                pm25 = float(request.POST.get('pm25', 50))
                pm10 = float(request.POST.get('pm10', 100))
                co = float(request.POST.get('co', 1.0))
                no2 = float(request.POST.get('no2', 40))
                so2 = float(request.POST.get('so2', 20))
                prediction_result = predict_pollution(pm25, pm10, co, no2, so2, location=selected_location, save_record=True, user=user)

        except ValueError as e:
            prediction_result = {
                "error": f"Invalid numerical inputs provided: {str(e)}"
            }

    # Fetch recent predictions history
    recent_predictions = serialize_docs(pred_col.find().sort("timestamp", -1).limit(15))

    context = {
        'locations': locations,
        'selected_hazard': selected_hazard,
        'selected_location': selected_location,
        'prediction_result': prediction_result,
        'recent_predictions': recent_predictions
    }
    return render(request, 'predictions/index.html', context)

@login_required_custom
def api_predict(request):
    """
    JSON API for automated sensor pipelines or client-side AJAX inference requests.
    Supports both JSON request body and form data.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "POST required"}, status=405)

    data = {}
    if request.content_type == 'application/json' and request.body:
        try:
            import json
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = {}
    if not data:
        data = request.POST

    hazard_type = str(data.get('hazard_type', '')).upper()
    location = data.get('location', 'External Source')
    user = request.session.get('username', 'API')

    try:
        if hazard_type in ('FLOOD',):
            res = predict_flood(
                float(data.get('rainfall', 0)),
                float(data.get('water_level', 0)),
                float(data.get('temperature', 25)),
                float(data.get('humidity', 70)),
                location=location,
                save_record=True,
                user=user
            )
        elif hazard_type in ('FOREST_FIRE', 'FIRE'):
            res = predict_fire(
                float(data.get('temperature', 30)),
                float(data.get('humidity', 40)),
                float(data.get('wind_speed', 15)),
                float(data.get('rainfall', 0)),
                float(data.get('smoke_level', 50)),
                location=location,
                save_record=True,
                user=user
            )
        elif hazard_type in ('POLLUTION', 'AIR_POLLUTION'):
            res = predict_pollution(
                float(data.get('pm25', 50)),
                float(data.get('pm10', 100)),
                float(data.get('co', 1.0)),
                float(data.get('no2', 40)),
                float(data.get('so2', 20)),
                location=location,
                save_record=True,
                user=user
            )
        else:
            return JsonResponse({"error": f"Unknown hazard type: {hazard_type}. Supported: FLOOD, FOREST_FIRE, POLLUTION"}, status=400)

        # Ensure datetime is formatted
        if isinstance(res.get('timestamp'), datetime):
            res['timestamp'] = res['timestamp'].strftime('%Y-%m-%d %H:%M:%S')

        return JsonResponse({"status": "success", "result": res})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

