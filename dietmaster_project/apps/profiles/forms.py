from django import forms
from .models import PatientProfile

# 1. Mevcut Profil Güncelleme Formu (Dashboard için)
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['height', 'weight', 'goal_weight', 'activity_level', 
                  'chronic_diseases', 'allergies', 'medications']
        
        widgets = {
            'chronic_diseases': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'medications': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'goal_weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'activity_level': forms.Select(attrs={'class': 'form-select'}),
        }

# 2. Yeni Sihirbaz Formu (Onboarding için - Eksik Olan Bu)
class OnboardingForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = [
            'birth_date', 'gender', 'height', 'weight', 'goal_weight',
            'daily_activity', 'diet_preference', 'disliked_foods', 
            'chronic_diseases', 'allergies', 'medications'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'disliked_foods': forms.Textarea(attrs={'class': 'form-control bg-light border-0', 'rows': 4, 'placeholder': 'Örn: Süt ürünleri, acı biber...'}),
            'chronic_diseases': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Yoksa boş bırakın'}),
            'allergies': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Yoksa boş bırakın'}),
            'medications': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Kullandığınız ilaçlar'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'daily_activity': forms.Select(attrs={'class': 'form-select'}),
            'diet_preference': forms.Select(attrs={'class': 'form-select'}),
            'height': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'goal_weight': forms.NumberInput(attrs={'class': 'form-control form-control-lg text-center fw-bold', 'placeholder': '00.0'}),
        }