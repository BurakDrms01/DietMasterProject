from django import forms
from .models import MealPhoto

class MealPhotoForm(forms.ModelForm):
    class Meta:
        model = MealPhoto
        fields = ['photo', 'meal_type']
        widgets = {
            'meal_type': forms.HiddenInput(), # Öğün tipini gizli bir alanda tutacağız
        }