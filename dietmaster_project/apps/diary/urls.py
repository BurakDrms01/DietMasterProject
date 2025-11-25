from django.urls import path
from . import views

app_name = 'diary'
urlpatterns = [
    path('upload/', views.upload_meal_photo, name='upload_meal_photo'),
]