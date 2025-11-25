from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Projenin ana adresi (yani 'http://127.0.0.1:8000/')
    # views.py dosyasındaki 'dashboard' fonksiyonuna yönlendirilecek.
    # Bu URL'ye 'dashboard' ismini veriyoruz.
    path('', views.dashboard, name='dashboard'),
]