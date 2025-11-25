from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('list/', views.list_view, name='list'),  # BUGFIX: Added missing list view
    path('get-slots/', views.get_slots_view, name='get_slots'),
    path('create/', views.create_appointment, name='create'),
    path('<int:pk>/update_status/', views.update_status, name='update_status'),
]
