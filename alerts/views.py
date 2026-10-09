"""
Alerts Views: Real-time Incident Feed, Status Management, and Filtering
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from accounts.auth_helper import login_required_custom, admin_required_custom
from alerts.services import get_alerts, update_alert_status
from config.db import get_locations_col, get_alerts_col

@login_required_custom
def alerts_list_view(request):
    status_filter = request.GET.get('status', 'ALL')
    severity_filter = request.GET.get('severity', 'ALL')
    type_filter = request.GET.get('type', 'ALL')
    location_filter = request.GET.get('location', 'ALL')

    alerts = get_alerts(
        status=status_filter,
        severity=severity_filter,
        alert_type=type_filter,
        location=location_filter,
        limit=100
    )

    # Summary metrics
    col = get_alerts_col()
    total_active = col.count_documents({"status": "ACTIVE"})
    total_critical = col.count_documents({"severity": "CRITICAL", "status": "ACTIVE"})
    total_resolved = col.count_documents({"status": "RESOLVED"})

    # Locations for filter
    loc_col = get_locations_col()
    locations = list(loc_col.find({"status": "ACTIVE"}).sort("location_name", 1))

    context = {
        'alerts': alerts,
        'total_active': total_active,
        'total_critical': total_critical,
        'total_resolved': total_resolved,
        'status_filter': status_filter,
        'severity_filter': severity_filter,
        'type_filter': type_filter,
        'location_filter': location_filter,
        'locations': locations,
    }
    return render(request, 'alerts/index.html', context)

@admin_required_custom
@require_http_methods(["POST"])
def change_alert_status_view(request, alert_id):
    new_status = request.POST.get('status')
    if new_status in ['ACTIVE', 'ACKNOWLEDGED', 'RESOLVED']:
        if update_alert_status(alert_id, new_status):
            messages.success(request, f"Alert status updated to {new_status}.")
        else:
            messages.error(request, "Failed to update alert.")
    else:
        messages.error(request, "Invalid alert status provided.")

    return redirect(request.META.get('HTTP_REFERER', '/alerts/'))
