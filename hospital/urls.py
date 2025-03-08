from django.urls import path
from . import views
from .views import hospital_list
from django.urls import path
from .views import view_ambulance_requests, respond_to_request

app_name = 'hospital'

urlpatterns = [
    path('signup/', views.hospital_signup, name='signup'),
    path('login/', views.hospital_login, name='login'),
    path('logout/', views.hospital_logout, name='logout'),
    path('dashboard/', views.dashboard, name='hospital_dashboard'),  # Correct link for dashboard
    path('manage_ambulances/', views.manage_ambulances, name='manage_ambulances'),
    path('notifications/', views.notifications, name='notifications'),
    path('account_settings/', views.account_settings, name='account_settings'),
    path('help_and_support/', views.help_and_support, name='help_and_support'),
    path('api/hospitals/', hospital_list, name='hospital-list'),
    path('profile/', views.profile, name='profile'),  # Ensure this is defined
    path('ambulance-requests/', view_ambulance_requests, name='view_ambulance_requests'),
    path('respond-request/<int:request_id>/<str:response>/', respond_to_request, name='respond_request'),
]