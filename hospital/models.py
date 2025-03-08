from django.db import models
from django.contrib.auth.hashers import make_password


class Hospital(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(max_length=100)
    email = models.EmailField(unique=True)
    pan_number = models.CharField(max_length=9, unique=True, default="000000000")  # PAN number (9 digits)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        """Hashes the password before saving it."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check if the provided password matches the hashed password."""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)


class Hospitaldb(models.Model):
    name = models.CharField(max_length=255)
    speciality = models.CharField(max_length=255)
    contact = models.CharField(max_length=50)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):  # ✅ Double underscores here
        return self.name 
    
class Ambulance(models.Model):
    hospital = models.ForeignKey(Hospital, related_name='ambulances', on_delete=models.CASCADE)
    ambulance_number = models.CharField(max_length=20)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"Ambulance {self.ambulance_number}"

