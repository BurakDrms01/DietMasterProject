from django.contrib import admin
from .models import Appointment, DietitianAvailability

@admin.register(DietitianAvailability)
class DietitianAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('dietitian', 'weekday', 'start_time', 'end_time', 'slot_length_minutes')
    list_filter = ('weekday', 'dietitian')
    ordering = ('weekday', 'start_time')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'date')
    search_fields = ('client__username', 'client__email', 'notes')
    date_hierarchy = 'date'
