from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class ClientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="Adınız", required=True)
    last_name = forms.CharField(label="Soyadınız", required=True)
    email = forms.EmailField(label="E-posta Adresi", required=True)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email')

    def __init__(self, *args, **kwargs):
        super(ClientRegistrationForm, self).__init__(*args, **kwargs)
        
        # Tüm alanlara Bootstrap 'form-control' ve 'placeholder' ekliyoruz.
        # Placeholder, Floating Label için teknik bir zorunluluktur.
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
            
            # Kullanıcı adı yardım metnini temizleyelim
            if field_name == 'username':
                field.help_text = None