from django.apps import AppConfig

class NutritionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Burası sadece 'nutrition' değil, 'apps.nutrition' olmalı
    name = 'apps.nutrition'