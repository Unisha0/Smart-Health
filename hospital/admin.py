from django.contrib import admin
from .models import Hospital, Hospitaldb, Ambulance

class HospitalAdmin(admin.ModelAdmin):
    # Display fields after merging with Hospitaldb
    list_display = (
          # Display hospital_id
        'name',
        'email',
        'pan_number',
        'website',
        'created_at', 
        'updated_at'
    )
    
    # Make password readonly
    readonly_fields = ('password',)  # Prevent direct password editing

    # Enable search for certain fields
    search_fields = ('name', 'email', 'pan_number')

    # Set ordering by created_at in descending order
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        """Ensure passwords are hashed before saving."""
        if form.cleaned_data.get("password") and not obj.pk:  # Only hash if new
            obj.set_password(form.cleaned_data["password"])

# Register the Hospital model with the customized admin
admin.site.register(Hospital, HospitalAdmin)

class HospitaldbAdmin(admin.ModelAdmin):
    # Display fields related to Hospitaldb
    list_display = ('name', 'speciality', 'contact', 'address', 'latitude', 'longitude')
    
    # Enable search for name, speciality, and contact
    search_fields = ('name', 'speciality', 'contact')

# Register the Hospitaldb model with the customized admin
admin.site.register(Hospitaldb, HospitaldbAdmin)

class AmbulanceAdmin(admin.ModelAdmin):
    # Display fields for Ambulance
    list_display = ('hospital', 'ambulance_number', 'available')

    # Add a filter for availability
    list_filter = ('available',)

# Register the Ambulance model with the customized admin
admin.site.register(Ambulance, AmbulanceAdmin)