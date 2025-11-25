from django import forms
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model # GÜNCELLENDİ: Model importu yerine bunu kullanıyoruz
from .models import Task

# Aktif kullanıcı modelini alıyoruz
User = get_user_model()

class AdminTaskForm(forms.ModelForm):
    # Tarih seçtirmek yerine "Süre" seçtirelim
    DURATION_CHOICES = [
        ('1', 'Sadece Bugün (Tek Seferlik)'),
        ('7', '1 Hafta Boyunca'),
        ('30', '1 Ay Boyunca'),
        ('forever', 'Sürekli (Sınırsız)'),
    ]
    
    duration = forms.ChoiceField(
        choices=DURATION_CHOICES, 
        label="Ne Kadar Sürecek?",
        initial='7', # Varsayılan 1 hafta
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    assigned_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(), # Başlangıçta boş, __init__ içinde dolduracağız (Hata önleyici)
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Özel Olarak Ata"
    )

    class Meta:
        model = Task
        # start_date ve end_date'i formda göstermiyoruz, arkada hesaplayacağız
        fields = ['title', 'description', 'points', 'task_type', 'related_meal_type', 'is_for_everyone', 'assigned_users']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Örn: Yürüyüş yap'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'points': forms.NumberInput(attrs={'class': 'form-control'}),
            'task_type': forms.Select(attrs={'class': 'form-select'}),
            'related_meal_type': forms.Select(attrs={'class': 'form-select'}),
            'is_for_everyone': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # QuerySet'i burada tanımlamak en güvenli yöntemdir (Import hatalarını önler)
        # Sadece 'CLIENT' rolündeki kullanıcıları getir
        self.fields['assigned_users'].queryset = User.objects.filter(role='CLIENT')

    def save(self, commit=True):
        # Form kaydedilirken süreyi hesapla
        task = super().save(commit=False)
        
        duration = self.cleaned_data.get('duration')
        task.start_date = timezone.now().date()
        
        if duration == 'forever':
            task.end_date = None # Süresiz
        else:
            days = int(duration)
            # Bugün dahil olması için days-1 ekliyoruz
            task.end_date = task.start_date + timedelta(days=days - 1) 

        if commit:
            task.save()
            self.save_m2m() # ManyToMany (assigned_users) kaydı için şart
            
        return task