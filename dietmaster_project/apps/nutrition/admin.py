from django.contrib import admin
from .models import DietProgram, DailyMealPlan

class DailyMealPlanInline(admin.StackedInline): # StackedInline: Alt alta geniş alanlar açar
    model = DailyMealPlan
    extra = 7 # Varsayılan olarak 7 günü de açsın
    max_num = 7
    ordering = ['day_of_week']
    
    fieldsets = (
        (None, {
            'fields': (('day_of_week',), ('breakfast', 'lunch', 'dinner'), ('snack_1', 'snack_2', 'snack_3'))
        }),
    )

@admin.register(DietProgram)
class DietProgramAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'start_date']
    search_fields = ['user__username', 'user__first_name', 'title']
    inlines = [DailyMealPlanInline] # Günleri programın içine gömüyoruz