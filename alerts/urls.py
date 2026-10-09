from django.urls import path
from alerts import views

urlpatterns = [
    path('', views.alerts_list_view, name='alerts_list'),
    path('<str:alert_id>/status/', views.change_alert_status_view, name='change_alert_status'),
]
