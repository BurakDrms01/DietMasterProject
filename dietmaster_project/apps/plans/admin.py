from django.contrib import admin
from .models import DietPlan, PlanFeature, PlanRequest

class FeatureInline(admin.TabularInline):
    model = PlanFeature
    extra = 3

@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_days', 'is_popular']
    inlines = [FeatureInline]

@admin.register(PlanRequest)
class PlanRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email']
    list_editable = ['status']