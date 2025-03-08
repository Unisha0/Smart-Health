from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import AmbulanceDriverSignupForm, AmbulanceDriverLoginForm
from .models import AmbulanceDriver
from django.contrib.auth.hashers import make_password, check_password

# View for ambulance driver signup
def ambulance_driver_signup(request):
    if request.method == 'POST':
        form = AmbulanceDriverSignupForm(request.POST)
        if form.is_valid():
            AmbulanceDriver = form.save(commit=False)
            AmbulanceDriver.password = make_password(form.cleaned_data['password'])
            AmbulanceDriver.save()
            return redirect('shea:ambulance_driver_login')  # Redirect to the login page
    else:
        form = AmbulanceDriverSignupForm()
    return render(request, 'shea/ambulance_driver_signup.html', {'form': form})


def ambulance_driver_login(request):
    if request.method == 'POST':
        form = AmbulanceDriverLoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            try:
                driver = AmbulanceDriver.objects.get(phone_number=phone_number)
                if check_password(password, driver.password):
                    request.session['Ambulancedriver_id'] = driver.id
                    return redirect('shea:ambulance_driver_dashboard')
                else:
                    form.add_error(None, 'Invalid credentials')
            except AmbulanceDriver.DoesNotExist:
                form.add_error(None, 'Ambulancedriver not found')
    else:
        form = AmbulanceDriverLoginForm()
    return render(request, 'shea/ambulance_driver_login.html', {'form': form})

def ambulance_driver_dashboard(request):
    driver = request.user  # Assuming the driver is logged in and is the user
    try:
        driver = AmbulanceDriver.objects.get(id=request.session['Ambulancedriver_id'])
    except AmbulanceDriver.DoesNotExist:
        return render(request, 'error.html', {'message': 'Driver not found'})

    return render(request, 'shea/ambulance_driver_dashboard.html', {'driver': driver})