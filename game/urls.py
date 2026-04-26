from django.urls import path
from . import views

urlpatterns = [
    # SPA
    path('', views.index, name='index'),

    # API endpoints
    path('api/verbs/', views.api_verbs, name='api_verbs'),
    path('api/save-session/', views.api_save_session, name='api_save_session'),

    # Admin panel
    path('admin-panel/login/', views.admin_login_view, name='admin_login'),
    path('admin-panel/logout/', views.admin_logout_view, name='admin_logout'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/verbs/', views.admin_verbs, name='admin_verbs'),
    path('admin-panel/sessions/', views.admin_sessions, name='admin_sessions'),
    path('admin-panel/sessions/<int:pk>/delete/', views.admin_delete_session, name='admin_delete_session'),
]
