from django.urls import path
from predictions import views

urlpatterns = [
    path('', views.prediction_console_view, name='prediction_console'),
    path('api/predict/', views.api_predict, name='api_predict'),
]
