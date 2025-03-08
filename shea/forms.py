from django import forms
from .models import AmbulanceDriver

class AmbulanceDriverSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = AmbulanceDriver
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'license_number', 'hospital','password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


class AmbulanceDriverLoginForm(forms.Form):
    phone_number = forms.CharField(
        max_length=10,
        label="Phone Number",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),
        label="Password"
    )
