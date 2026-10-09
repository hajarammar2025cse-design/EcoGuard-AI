from django.urls import path
from hazards import views

urlpatterns = [
    path('flood/', views.flood_module_view, name='flood_module'),
    path('fire/', views.fire_module_view, name='fire_module'),
    path('pollution/', views.pollution_module_view, name='pollution_module'),
    path('ml-performance/', views.ml_performance_view, name='ml_performance'),
]
