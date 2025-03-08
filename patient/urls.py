from django.urls import path
from . import views
from .views import request_ambulance, check_request_status

urlpatterns = [
    path('signup/', views.signup, name='patient_signup'),
    path('login/', views.login, name='patient_login'),
    path('dashboard/', views.dashboard, name='patient_dashboard'),
    path('hospital/', views.hospital, name='hospital'),
    path('ambulance/', views.ambulance, name='ambulance'),
    path('user_account/', views.user_account, name='user_account'),
    path('help/', views.help_page, name='help_page'),
    path('patient-history/', views.patient_history, name='patient_history'),
    path('logout/', views.logout, name='logout'),
    path('upload/', views.upload_medical_history, name='upload_medical_history'),
    path('request-ambulance/<int:hospital_id>/', request_ambulance, name='request_ambulance'),
    path('check-request-status/', check_request_status, name='check_request_status'),
]