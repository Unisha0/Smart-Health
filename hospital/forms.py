from django import forms
from .models import Hospital, Ambulance
from django.core.exceptions import ValidationError

# Custom validator for PAN number to ensure it's exactly 9 digits long
def validate_pan_number(value):
    if not value.isdigit() or len(value) != 9:
        raise ValidationError('PAN number must be exactly 9 digits.')
    return value

class HospitalSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = Hospital
        fields = ['name', 'address', 'email', 'pan_number', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean_pan_number(self):
        pan_number = self.cleaned_data.get('pan_number')
        return validate_pan_number(pan_number)

class HospitalLoginForm(forms.Form):
    pan_number = forms.CharField(max_length=9, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

class HospitalForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = ['name', 'address', 'email', 'website', 'description']
        
class AmbulanceForm(forms.ModelForm):
    class Meta:
        model = Ambulance
        fields = ['ambulance_number', 'available']
