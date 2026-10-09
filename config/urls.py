"""
URL Configuration for Environmental Hazard Monitoring Network
"""
from django.contrib import admin
from django.urls import path, include
from monitoring.views import landing_view, dashboard_view

urlpatterns = [
    # Landing Page & Dashboard Root
    path('', landing_view, name='landing'),
    path('dashboard/', dashboard_view, name='dashboard'),

    # Modular App Endpoints
    path('accounts/', include('accounts.urls')),
    path('', include('monitoring.urls')),
    path('hazards/', include('hazards.urls')),
    path('predictions/', include('predictions.urls')),
    path('alerts/', include('alerts.urls')),
    path('', include('analytics.urls')),
]
