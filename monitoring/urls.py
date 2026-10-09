from django.urls import path
from monitoring import views

urlpatterns = [
    path('monitoring/', views.environmental_monitoring_view, name='environmental_monitoring'),
    path('monitoring/add/', views.add_environmental_data, name='add_environmental_data'),
    path('monitoring/<str:record_id>/edit/', views.edit_environmental_data, name='edit_environmental_data'),
    path('monitoring/<str:record_id>/delete/', views.delete_environmental_data, name='delete_environmental_data'),
    path('locations/', views.locations_list_view, name='locations_list'),
    path('locations/add/', views.add_location_view, name='add_location'),
    path('locations/<str:location_id>/delete/', views.delete_location_view, name='delete_location'),
    path('map/', views.live_map_view, name='live_map'),
    path('api/map-locations/', views.api_map_locations, name='api_map_locations'),
    path('api/dashboard-charts/', views.api_dashboard_charts, name='api_dashboard_charts'),
]
