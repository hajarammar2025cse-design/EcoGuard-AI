from django.urls import path
from accounts import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('users/', views.user_management_view, name='user_management'),
    path('users/<str:user_id>/toggle-role/', views.toggle_user_role, name='toggle_user_role'),
    path('users/<str:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
]
