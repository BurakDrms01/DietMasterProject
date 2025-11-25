from django.urls import path
from . import views

app_name = 'plans'

urlpatterns = [
    path('pricing/', views.pricing_page, name='pricing'),
    
    # --- EKSİK OLAN SATIR BU ---
    path('select/<int:plan_id>/', views.create_plan_request, name='select_plan'),
    path('manage/<int:request_id>/', views.manage_request, name='manage_request'),
]