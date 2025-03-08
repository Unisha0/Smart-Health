from django.contrib import admin
from .models import AmbulanceDriver, Ambulance
from django.utils.html import format_html

# Custom Admin for AmbulanceDriver model
class AmbulanceDriverAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number', 'email', 'license_number', 'hospital', 'get_password', 'date_created')
    search_fields = ('first_name', 'last_name', 'phone_number', 'email')
    list_filter = ('hospital',)

    # Optional: Display password hash as '****' to prevent exposing it
    def get_password(self, obj):
        return format_html('****')  # or any custom logic you want for password display
    get_password.short_description = 'Password'

    # Optional: Show the creation date (if you want to track when drivers were added)
    def date_created(self, obj):
        # Ensure the model has a 'created_at' field
        return obj.created_at if hasattr(obj, 'created_at') else 'N/A'
    date_created.short_description = 'Date Created'

# Register AmbulanceDriver model with custom admin
admin.site.register(AmbulanceDriver, AmbulanceDriverAdmin)

# Register Ambulance model (if you want to manage ambulance information)
admin.site.register(Ambulance)
