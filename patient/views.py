from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from hospital.models import Hospitaldb, Hospital, Ambulance
from .models import Patient, Advertisement, PatientHistory
from .forms import PatientSignupForm, PatientLoginForm
from .serializers import AmbulanceSerializer  # Import the serializer
from django.http import HttpResponse, JsonResponse
from math import radians, cos, sin, sqrt, atan2
import heapq
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Patient, AmbulanceRequest


# Signup view for patients
def signup(request):
    if request.method == 'POST':
        form = PatientSignupForm(request.POST)
        if form.is_valid():
            # Get latitude and longitude from POST data (hidden fields)
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')

            # Save patient data without latitude and longitude from the form
            patient = form.save(commit=False)
            patient.password = make_password(form.cleaned_data['password'])
            
            # Assign latitude and longitude from hidden fields
            if latitude:
                patient.latitude = latitude
            if longitude:
                patient.longitude = longitude
                
            patient.save()

            return redirect('patient_login')
    else:
        form = PatientSignupForm()

    return render(request, 'patient/signup.html', {'form': form})

# Login view for patients
def login(request):
    if request.method == 'POST':
        form = PatientLoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            try:
                patient = Patient.objects.get(phone_number=phone_number)
                if check_password(password, patient.password):
                    request.session['patient_id'] = patient.id
                    return redirect('patient_dashboard')
                else:
                    form.add_error(None, 'Invalid credentials')
            except Patient.DoesNotExist:
                form.add_error(None, 'Patient not found')
    else:
        form = PatientLoginForm()
    return render(request, 'patient/login.html', {'form': form})


# Dashboard view
def dashboard(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')
    patient = Patient.objects.get(id=patient_id)
    ads = Advertisement.objects.all()
    return render(request, 'patient/dashboard.html', {'patient': patient, 'ads': ads})

# View for hospital list
def hospital(request):
    hospitals = Hospital.objects.all()
    return render(request, 'patient/hospital.html', {'hospitals': hospitals})

# User account page
def user_account(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')
    patient = Patient.objects.get(id=patient_id)
    return render(request, 'patient/user_account.html', {'patient': patient})

# View for ambulance details
def ambulance(request):
    ambulances = Ambulance.objects.filter(available=True)
    serializer = AmbulanceSerializer(ambulances, many=True)
    return render(request, 'patient/ambulance.html', {'ambulances': serializer.data})

# Help page view
def help_page(request):
    return render(request, 'patient/help_page.html')

# Patient history page
def patient_history(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')
    history = PatientHistory.objects.filter(patient_id=patient_id)
    return render(request, 'patient/patient_history.html', {'history': history})

# Logout view
def logout(request):
    request.session.flush()
    return redirect('patient_login')

# Nearest hospital view
def nearest_hospital(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')

    patient = Patient.objects.get(id=patient_id)

    # Get the nearest hospital and its distance
    nearest_hospital, distance = patient.get_nearest_hospital()

    if nearest_hospital:
        return JsonResponse({
            'nearest_hospital': {
                'name': nearest_hospital.name,
                'address': nearest_hospital.address,
                'latitude': nearest_hospital.latitude,
                'longitude': nearest_hospital.longitude
            },
            'distance': distance
        })
    else:
        return JsonResponse({'error': 'No hospital found or patient location is unavailable'})

# Function for haversine distance calculation
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius of Earth in kilometers
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)*2 + cos(lat1) * cos(lat2) * sin(dlon / 2)*2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

# Function to find nearest hospital using Dijkstra's algorithm (optional)
def dijkstra_shortest_path(start_lat, start_lon):
    hospitals = Hospital.objects.all()
    graph = {}
    for hospital in hospitals:
        graph[hospital.id] = []
        for neighbor in hospitals:
            if hospital != neighbor:
                distance = haversine_distance(hospital.latitude, hospital.longitude, neighbor.latitude, neighbor.longitude)
                graph[hospital.id].append((neighbor.id, distance))

    def dijkstra(start_id):
        distances = {hospital.id: float('inf') for hospital in hospitals}
        previous_nodes = {hospital.id: None for hospital in hospitals}
        distances[start_id] = 0
        queue = [(0, start_id)]

        while queue:
            current_distance, current_id = heapq.heappop(queue)

            if current_distance > distances[current_id]:
                continue

            for neighbor_id, weight in graph[current_id]:
                distance = current_distance + weight
                if distance < distances[neighbor_id]:
                    distances[neighbor_id] = distance
                    previous_nodes[neighbor_id] = current_id
                    heapq.heappush(queue, (distance, neighbor_id))

        return distances, previous_nodes

    start_hospital = Hospital.objects.filter(latitude=start_lat, longitude=start_lon).first()
    if start_hospital:
        distances, previous_nodes = dijkstra(start_hospital.id)
        nearest_hospital_id = min(distances, key=distances.get)
        nearest_hospital = Hospital.objects.get(id=nearest_hospital_id)
        return {
            'nearest_hospital': {
                'name': nearest_hospital.name,
                'address': nearest_hospital.address,
                'latitude': nearest_hospital.latitude,
                'longitude': nearest_hospital.longitude
            },
            'distance': distances[nearest_hospital_id]
        }
    return {'error': 'No hospital found near the given location'}

from django.http import JsonResponse

def get_hospitals(request):
    hospitals = Hospital.objects.all().values('name', 'address', 'latitude', 'longitude')
    return JsonResponse(list(hospitals), safe=False)

def request_ambulance(request, hospital_id):
    if not request.session.get('patient_id'):
        return redirect('patient_login')

    patient = get_object_or_404(Patient, id=request.session['patient_id'])

    # Get the correct Hospital instance
    hospital_instance = get_object_or_404(Hospital, id=hospital_id)

    # Prevent duplicate requests
    existing_request = AmbulanceRequest.objects.filter(patient=patient, hospital=hospital_instance, status='Pending').exists()
    if existing_request:
        messages.warning(request, 'You already have a pending request!')
        return redirect('patient_dashboard')

    # Create request
    ambulance_request = AmbulanceRequest.objects.create(patient=patient, hospital=hospital_instance, status='Pending')

    # Notify hospital via email
    subject = 'New Ambulance Request'
    message = (f"Patient Name: {patient.name}\n"
               f"Email: {patient.email}\n"
               f"Phone: {patient.phone_number}\n"
               f"Address: {patient.latitude}, {patient.longitude}\n"
               f"Status: {ambulance_request.status}")

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        ['hospital@example.com'],  # Ensure hospital email is valid
        fail_silently=False,
    )

    # Notify the patient
    patient_notification_subject = "Ambulance Request Submitted"
    patient_notification_message = (f"Dear {patient.name},\n\n"
                                    f"Your ambulance request to {hospital_instance.name} has been submitted.\n\n"
                                    f"Status: {ambulance_request.status}\n"
                                    f"We'll notify you once your request is processed.")

    send_mail(
        patient_notification_subject,
        patient_notification_message,
        settings.DEFAULT_FROM_EMAIL,
        [patient.email],
        fail_silently=False,
    )

    messages.success(request, 'Ambulance request sent successfully!')
    return redirect('patient_dashboard')

# Check request status
def check_request_status(request):
    if not request.session.get('patient_id'):
        return JsonResponse({'error': 'User not logged in'}, status=400)

    patient = get_object_or_404(Patient, id=request.session['patient_id'])
    request_status = AmbulanceRequest.objects.filter(patient=patient).last()

    if not request_status:
        return JsonResponse({'status': 'No active request'})

    return JsonResponse({'status': request_status.status})


# Respond to request (hospital action: Accept or Reject)
def respond_to_request(request, request_id, action):
    if not request.session.get('hospital_id'):
        return redirect('hospital_login')

    hospital = get_object_or_404(Hospital, id=request.session['hospital_id'])
    ambulance_request = get_object_or_404(AmbulanceRequest, id=request_id)

    if ambulance_request.hospital != hospital:
        messages.error(request, 'You do not have permission to respond to this request.')
        return redirect('hospital_dashboard')

    if action == 'accept':
        ambulance_request.update_status('Accepted')
        messages.success(request, 'Request accepted successfully.')
    elif action == 'reject':
        ambulance_request.update_status('Rejected')
        messages.success(request, 'Request rejected successfully.')
    else:
        messages.error(request, 'Invalid action.')

    return HttpResponse('Ambulance requested successfully!')  # You can redirect or show a success message
    return render(request, 'ambulance/request.html')  # Or just return a response

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import MedicalHistoryForm
from .models import MedicalHistory

def upload_medical_history(request):
    if request.method == 'POST':
        form = MedicalHistoryForm(request.POST, request.FILES)
        if form.is_valid():
            medical_history = form.save(commit=False)
            medical_history.user = request.user  # Associate the file with the logged-in user
            medical_history.save()
            messages.success(request, 'Medical history file uploaded successfully!')
            return redirect('view_medical_history')  # Redirect to view uploaded files
        else:
            messages.error(request, 'There was an error uploading the file.')
    else:
        form = MedicalHistoryForm()

    return render(request, 'medical/upload_medical_history.html', {'form': form})