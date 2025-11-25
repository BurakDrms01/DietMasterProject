from django import forms
from .models import DietProgram, DailyMealPlan

class DietProgramForm(forms.ModelForm):
    class Meta:
        model = DietProgram
        fields = ['title', 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Örn: 1. Hafta - Arınma Diyeti'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class DailyMealForm(forms.ModelForm):
    class Meta:
        model = DailyMealPlan
        fields = ['breakfast', 'lunch', 'dinner', 'snack_1', 'snack_2', 'snack_3']
        widgets = {
            'breakfast': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Örn: 1 Haşlanmış Yumurta...'}),
            'lunch': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'dinner': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'snack_1': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'snack_2': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'snack_3': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }