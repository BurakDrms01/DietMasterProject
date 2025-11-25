from django.contrib import admin
from .models import PatientProfile, WeightHistory, DailyWaterIntake

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'age', 'bmi_status', 'goal_weight']
    search_fields = ['user__username', 'user__first_name', 'chronic_diseases']

@admin.register(WeightHistory)
class WeightHistoryAdmin(admin.ModelAdmin):
    list_display = ['profile', 'weight', 'date']
    list_filter = ['date']

@admin.register(DailyWaterIntake)
class DailyWaterIntakeAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_amount', 'target_amount', 'progress_percent', 'date']
    list_filter = ['date']