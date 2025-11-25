from django.urls import path
from . import views

# --- KRİTİK SATIR: NAMESPACE TANIMI ---
app_name = 'users' 
# --------------------------------------

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
]