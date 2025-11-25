from django.contrib import admin
from .models import Task, TaskCompletion

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task_type', 'points', 'is_active', 'start_date', 'end_date']
    list_filter = ['task_type', 'is_active', 'is_for_everyone']
    search_fields = ['title', 'description']
    filter_horizontal = ['assigned_users'] # Çoklu seçim kutusunu güzelleştirir

@admin.register(TaskCompletion)
class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'completion_date']
    list_filter = ['completion_date', 'user']