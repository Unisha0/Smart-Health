from django.contrib import admin
from .models import Patient, Advertisement, PatientHistory, HelpTopic, UserAccountSettings, AmbulanceRequest

class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone_number', 'latitude', 'longitude', 'created_at')
    readonly_fields = ('password',)  # Prevent direct editing of hashed passwords

    def id(self, obj):
        return list(Patient.objects.all()).index(obj) + 1  # Auto-generate SN
    
    id.short_description = "ID"

admin.site.register(Patient, PatientAdmin)

@admin.register(AmbulanceRequest)
class AmbulanceRequestAdmin(admin.ModelAdmin):
    list_display = ('patient', 'hospital', 'requested_at', 'status', 'reason')
    list_filter = ('status',)
    actions = ['mark_accepted', 'mark_rejected']

    def mark_accepted(self, request, queryset):
        queryset.update(status='Accepted')
        for request in queryset:
            request.send_patient_notification('Accepted')
    mark_accepted.short_description = "Mark selected requests as Accepted"

    def mark_rejected(self, request, queryset):
        queryset.update(status='Rejected')
        for request in queryset:
            request.send_patient_notification('Rejected')
    mark_rejected.short_description = "Mark selected requests as Rejected"