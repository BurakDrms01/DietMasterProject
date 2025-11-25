from django import forms
from .models import Recipe

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['category', 'title', 'image', 'calories', 'prep_time', 'ingredients', 'instructions']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select rounded-pill'}),
            'title': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Örn: Avokadolu Tost'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control rounded-pill'}),
            'prep_time': forms.NumberInput(attrs={'class': 'form-control rounded-pill'}),
            'ingredients': forms.Textarea(attrs={'class': 'form-control rounded-4', 'rows': 4, 'placeholder': '1 adet yumurta\n2 dilim ekmek...'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control rounded-4', 'rows': 4, 'placeholder': 'Yumurtayı haşlayın...'}),
            'image': forms.FileInput(attrs={'class': 'form-control rounded-pill'}),
        }