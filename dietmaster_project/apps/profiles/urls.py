from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('karnem/', views.my_profile, name='detail'),
    # Yeni su ekleme linki (int:amount -> kaç ml ekleneceğini url'den alacak)
    path('add-water/<int:amount>/', views.add_water, name='add_water'),
    path('onboarding/', views.onboarding_wizard, name='onboarding_wizard'),
]