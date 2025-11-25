from django.urls import path
from . import views

# BU SATIR ÇOK ÖNEMLİ (Namespace hatası almamak için)
app_name = 'gamification'

urlpatterns = [
    # Danışanın görevi tamamlaması için (Mevcut olan)
    path('toggle/<int:task_id>/', views.toggle_task_completion, name='toggle_task'),
    
    # Diyetisyenin görev yönetimi paneli için (Eksik olan bu satırdı)
    path('yonetim/', views.task_manager, name='manager'),

    
    # YENİ EKLENEN: Görev Silme Yolu
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),

        # YENİ EKLENEN: Düzenleme Yolu
    path('edit/<int:task_id>/', views.edit_task, name='edit_task'),
]
