import math
from django.db import models
from django.core.validators import RegexValidator
from hospital.models import Hospital, Ambulance  # Importing related models
from django.core.mail import send_mail
from django.conf import settings

class Patient(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(
            regex=r'^(97|98)\d{8}$',
            message="Enter a valid Nepali phone number (10 digits starting with 97 or 98)."
        )],
        unique=True
    )
    password = models.CharField(max_length=255)  # Use hashed passwords later
    created_at = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

    def haversine(self, lat1, lon1, lat2, lon2):
        # Radius of the Earth in km
        R = 6371
        # Convert degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c  # Distance in kilometers
        return distance

    def get_nearest_hospital(self):
        # If patient doesn't have a location, return None
        if not self.latitude or not self.longitude:
            return None

        nearest_hospital = None
        min_distance = float('inf')  # Set initial distance to infinity

        # Iterate over all hospitals and calculate the distance
        hospitals = Hospital.objects.all()
        for hospital in hospitals:
            distance = self.haversine(self.latitude, self.longitude, hospital.latitude, hospital.longitude)
            if distance < min_distance:
                min_distance = distance
                nearest_hospital = hospital

        return nearest_hospital, min_distance


# Other models remain the same as you provided
class Advertisement(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='ads/')  # Store ad images
    link = models.URLField()  # Redirect to hospital or other relevant links

    def __str__(self):
        return self.title


class PatientHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='histories')
    date = models.DateTimeField(auto_now_add=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True)
    details = models.TextField()

    def __str__(self):
        return f"{self.patient.name} - {self.date.strftime('%Y-%m-%d')}"


class HelpTopic(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()

    def __str__(self):
        return self.question


class UserAccountSettings(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='account_settings')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    notifications_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Settings for {self.patient.name}"
    

from hospital.models import Hospital
from django.core.mail import send_mail
from django.conf import settings

from django.core.mail import send_mail
from django.conf import settings

class AmbulanceRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='ambulance_requests')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='ambulance_requests')
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reason = models.TextField(default='No reason provided')

    def __str__(self):
        return f"Request by {self.patient.name} to {self.hospital.name} - {self.status}"

    def send_hospital_notification(self):
        # Notification to the hospital when the patient sends a request
        subject = "New Ambulance Request"
        message = (f"Patient Name: {self.patient.name}\n"
                   f"Email: {self.patient.email}\n"
                   f"Phone: {self.patient.phone_number}\n"
                   f"Address: {self.patient.latitude}, {self.patient.longitude}\n"
                   f"Reason: {self.reason}\n"
                   f"Status: {self.status}")
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.hospital.email],
            fail_silently=False,
        )

    def send_patient_notification(self, status):
        # Notification to the patient when the hospital accepts or rejects the request
        if status == 'Accepted':
            subject = "Ambulance Request Accepted"
            message = (f"Dear {self.patient.name},\n"
                       f"Your ambulance request to {self.hospital.name} has been accepted.\n"
                       f"Reason: {self.reason}\n"
                       f"Status: {status}")
        elif status == 'Rejected':
            subject = "Ambulance Request Rejected"
            message = (f"Dear {self.patient.name},\n"
                       f"Sorry, your ambulance request to {self.hospital.name} has been rejected.\n"
                       f"Reason: {self.reason}\n"
                       f"Status: {status}")
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.patient.email],
            fail_silently=False,
        )

    def save(self, *args, **kwargs):
        # If the request is being created, send a hospital notification
        if self._state.adding:
            self.send_hospital_notification()
        super().save(*args, **kwargs)

    def update_status(self, new_status):
        """This method will update the status and notify the patient."""
        self.status = new_status
        self.save()
        self.send_patient_notification(new_status)

from django.db import models
from django.contrib.auth.models import User

class MedicalHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='medical_history/', verbose_name='Medical History File')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Medical History for {self.user.username} - {self.upload_date}"
