from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.recipe_list, name='list'),
    path('<int:pk>/', views.recipe_detail, name='detail'),
    path('add/', views.add_recipe, name='add'),
    # Onaylama/Reddetme URL'i (HTMX için)
    path('review/<int:pk>/<str:action>/', views.review_recipe, name='review'),
]