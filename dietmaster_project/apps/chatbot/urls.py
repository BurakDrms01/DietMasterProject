from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_room, name='room'),
    path('send/', views.send_message, name='send_message'),
    path('clear/', views.clear_history, name='clear_history'),
    path('download/', views.download_history, name='download_history'),
]