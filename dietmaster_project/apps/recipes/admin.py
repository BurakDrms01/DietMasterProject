from django.contrib import admin
from .models import Category, Recipe

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)} # İsim yazarken slug otomatik dolar

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'calories', 'prep_time', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'ingredients')