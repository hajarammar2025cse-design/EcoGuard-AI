from django.urls import path
from analytics import views

urlpatterns = [
    path('analytics/', views.analytics_view, name='analytics'),
    path('analytics/api/data/', views.api_analytics_data, name='api_analytics_data'),
    path('reports/', views.reports_view, name='reports'),
    path('reports/export/csv/', views.export_csv_view, name='export_csv'),
]
