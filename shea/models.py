from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

class AmbulanceDriver(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    license_number = models.CharField(max_length=100)
    hospital = models.ForeignKey('hospital.Hospitaldb', on_delete=models.CASCADE)  # Assuming there is a Hospital model
    password = models.CharField(max_length=255, default="null")  # To store the hashed password
    created_at = models.DateTimeField(auto_now_add=True, null=True)  # Removed default=timezone.now

    def set_password(self, raw_password):
        """Sets the password after hashing it"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Checks if the provided password matches the stored hashed password"""
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = "Ambulance Driver"
        verbose_name_plural = "Ambulance Drivers"

class Ambulance(models.Model):
    driver = models.ForeignKey(AmbulanceDriver, on_delete=models.CASCADE)
    hospital = models.ForeignKey('hospital.Hospital', on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    registration_number = models.CharField(max_length=50)

    def __str__(self):
        return self.registration_number
