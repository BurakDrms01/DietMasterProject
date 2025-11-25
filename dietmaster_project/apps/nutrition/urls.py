from django.urls import path
from . import views

app_name = 'nutrition'

urlpatterns = [
    path('create/<int:client_id>/', views.program_create, name='program_create'),
    path('edit/<int:program_id>/', views.program_edit, name='program_edit'),
    path('clients/', views.client_list, name='client_list'),
    path('my-plan/', views.my_plan, name='my_plan'),
]