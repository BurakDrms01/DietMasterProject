from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.users.views import register_view 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ANA SAYFA (Dashboard)
    path('', include('apps.core.urls')),
    
    # Django'nun hazır Auth sistemi (Login/Logout/Password Reset)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Kayıt Sayfası (View'ı yukarıda import ettik)
    path('register/', register_view, name='register'),

    # Uygulama URL'leri
    path('tasks/', include('apps.gamification.urls')), # Görevler
    path('diary/', include('apps.diary.urls')),        # Günlük/Yemek Fotoğrafları
    path('profiles/', include('apps.profiles.urls')),  # Sağlık Karnesi
    path('plans/', include('apps.plans.urls')),
    path('nutrition/', include('apps.nutrition.urls')), 
    path('chat/', include('apps.chatbot.urls')),
    path('users/', include('apps.users.urls')), 
    path('appointments/', include('apps.appointments.urls')), # randevu sistemi
    path('recipes/', include('apps.recipes.urls')), # tarifler
    path('leaderboard/', include('apps.leaderboard.urls')),  #Görevlere göre günlük sıralma
]

# --- MEDYA DOSYALARI AYARI (Yemek fotolarının görünmesi için şart) ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
