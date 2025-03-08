import math
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.db.models import Q
from hospital.models import Ambulance, Hospital, Hospitaldb
from .forms import HospitalSignupForm, HospitalLoginForm, HospitalForm, AmbulanceForm

# Hospital Signup
def hospital_signup(request):
    if request.method == 'POST':
        form = HospitalSignupForm(request.POST)
        if form.is_valid():
            hospital = form.save(commit=False)
            hospital.set_password(form.cleaned_data['password'])
            hospital.save()
            messages.success(request, f"Hospital {hospital.name} registered successfully!")
            return redirect('hospital:login')  # Redirect to login page after successful signup
    else:
        form = HospitalSignupForm()
    return render(request, 'hospital/signup.html', {'form': form})

# Hospital Login
def hospital_login(request):
    if request.method == 'POST':
        form = HospitalLoginForm(request.POST)
        if form.is_valid():
            pan_number = form.cleaned_data['pan_number']
            password = form.cleaned_data['password']
            try:
                hospital = Hospital.objects.get(pan_number=pan_number)
                if hospital.check_password(password):  # Using the check_password method
                    # Save hospital ID and name in session
                    request.session['hospital_id'] = hospital.id
                    request.session['hospital_name'] = hospital.name
                    messages.success(request, f"Welcome to {hospital.name}!")
                    return redirect('hospital:hospital_dashboard')  # Redirect to hospital dashboard after successful login
                else:
                    messages.error(request, "Invalid password.")
            except Hospital.DoesNotExist:
                messages.error(request, "Hospital does not exist.")
        else:
            messages.error(request, "Invalid form submission.")
    else:
        form = HospitalLoginForm()
    return render(request, 'hospital/login.html', {'form': form})

# Hospital Dashboard
def dashboard(request):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hospital:login')  # Redirect to login page if not logged in

    hospital = Hospital.objects.get(id=hospital_id)
    ambulances_count = Ambulance.objects.filter(hospital=hospital).count()

    context = {
        'hospital': hospital,
        'ambulances_count': ambulances_count
    }

    return render(request, 'hospital/hospital_dashboard.html', context)


# Hospital Logout
def hospital_logout(request):
    logout(request)
    request.session.flush()  # Clear session data after logout
    messages.success(request, "Logged out successfully.")
    return redirect('hospital:login')  # Redirect to login page after logging out

# Manage Ambulances
def manage_ambulances(request):
    if not request.session.get('hospital_id'):  # Check if hospital is logged in
        return redirect('hospital:login')  # Redirect to login if not logged in

    hospital = Hospital.objects.get(id=request.session['hospital_id'])
    ambulances = Ambulance.objects.filter(hospital=hospital)
    return render(request, 'hospital/manage_ambulances.html', {'ambulances': ambulances})

# Notifications Page
def notifications(request):
    if not request.session.get('hospital_id'):
        return redirect('hospital:login')

    return render(request, 'hospital/notifications.html')

# Account Settings Page
def account_settings(request):
    if not request.session.get('hospital_id'):
        return redirect('hospital:login')

    return render(request, 'hospital/account_settings.html')

# Help & Support Page
def help_and_support(request):
    if not request.session.get('hospital_id'):
        return redirect('hospital:login')

    return render(request, 'hospital/help.html')

from django.http import JsonResponse
from hospital.models import Hospitaldb

def hospital_list(request):
    hospitals = Hospitaldb.objects.all().values("name", "speciality", "contact", "address", "latitude", "longitude")
    return JsonResponse(list(hospitals), safe=False)


def hospital_list(request):
    # Get the search term (name or specialty)
    search_term = request.GET.get('search', '').lower()

    # Get the patient's current location for proximity calculation (can be passed from frontend)
    patient_lat = float(request.GET.get('lat', 27.7172))  # Default: Kathmandu latitude
    patient_lon = float(request.GET.get('lon', 85.3240))  # Default: Kathmandu longitude

    # Search hospitals by name or specialty
    hospitals = Hospitaldb.objects.filter(
        Q(name__icontains=search_term) | Q(speciality__icontains=search_term)
    ).values("id","name", "speciality", "contact", "address", "latitude", "longitude")

    # Sort hospitals by distance to the patient using haversine formula
    hospitals = sorted(hospitals, key=lambda hospital: haversine_distance(
        patient_lat, patient_lon, hospital['latitude'], hospital['longitude']))

    # Return the hospitals as a JsonResponse
    return JsonResponse(list(hospitals), safe=False)

# Haversine formula for distance calculation
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius of the Earth in km
    dLat = (lat2 - lat1) * (3.14159 / 180)
    dLon = (lon2 - lon1) * (3.14159 / 180)
    lat1 = lat1 * (3.14159 / 180)
    lat2 = lat2 * (3.14159 / 180)
    
    a = (pow(math.sin(dLat / 2), 2) +
         math.cos(lat1) * math.cos(lat2) *
         pow(math.sin(dLon / 2), 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Distance in km

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Ambulance
from patient.models import AmbulanceRequest  # Import AmbulanceRequest model from the patient app
from django.core.mail import send_mail

# View all pending requests for a hospital
def view_ambulance_requests(request):
    if not request.session.get('hospital_id'):  # Ensure hospital is logged in
        return redirect('hospital_login')

    hospital = get_object_or_404(Hospital, id=request.session['hospital_id'])  # Get hospital by session ID
    requests = AmbulanceRequest.objects.filter(hospital=hospital, status='Pending')  # Filter pending requests

    return render(request, 'hospital/notifications.html', {'requests': requests})

# Accept or reject ambulance request
def respond_to_request(request, request_id, response):
    if not request.session.get('hospital_id'):
        return redirect('hospital_login')  # Redirect if hospital is not logged in

    ambulance_request = get_object_or_404(AmbulanceRequest, id=request_id)  # Get ambulance request by ID

    # Ensure that the hospital is authorized to handle the request
    if ambulance_request.hospital != request.user.hospital:
        messages.error(request, "You do not have permission to respond to this request.")
        return redirect('view_ambulance_requests')

    if response == 'accept':
        ambulance_request.status = 'Accepted'
        message = f"Hospital has accepted your ambulance request, {ambulance_request.patient.name}! 🚑"
    else:
        ambulance_request.status = 'Rejected'
        message = f"Sorry {ambulance_request.patient.name}, your request was declined."

    ambulance_request.save()  # Save the updated status of the request

    # Notify the patient via email
    send_mail(
        subject='Ambulance Request Update',
        message=message,
        from_email='assistantsmarthealth@gmail.com',  # Updated to your email address
        recipient_list=[ambulance_request.patient.email],  # Send email to patient
        fail_silently=True,
    )

    messages.success(request, f"Request {response}ed successfully!")
    return redirect('view_ambulance_requests')  # Redirect to the list of requests

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Hospital

def profile(request):
    # Get hospital_id from session
    hospital_id = request.session.get('hospital_id')

    if not hospital_id:
        messages.error(request, "You need to log in first.")
        return redirect('hospital:login')  # Redirect to login if not authenticated

    # Fetch hospital details
    hospital = get_object_or_404(Hospital, id=hospital_id)

    return render(request, 'hospital/profile.html', {'hospital': hospital})

