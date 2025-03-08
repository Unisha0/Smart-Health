from django.urls import path
from . import views

app_name = 'shea'
urlpatterns = [
    path('signup/', views.ambulance_driver_signup, name='ambulance_driver_signup'),
    path('login/', views.ambulance_driver_login, name='ambulance_driver_login'),
    path('dashboard/', views.ambulance_driver_dashboard, name='ambulance_driver_dashboard'),
    # Add any other necessary routes
]
