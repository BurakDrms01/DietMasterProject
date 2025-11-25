from django.contrib import admin
from .models import MealPhoto

@admin.register(MealPhoto)
class MealPhotoAdmin(admin.ModelAdmin):
    list_display = ['user', 'meal_type', 'uploaded_at']
    list_filter = ['meal_type', 'uploaded_at']
    search_fields = ['user__username', 'user__first_name'] # İlişkili tablodan arama