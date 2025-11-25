from django.urls import path
from . import views

app_name = 'leaderboard'

urlpatterns = [
    # Ana Liderlik Tablosu Sayfası (http://.../leaderboard/)
    path('', views.leaderboard_view, name='ranking'),
]