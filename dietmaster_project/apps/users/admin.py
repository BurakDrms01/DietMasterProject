from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # Listeleme ekranında görünecek sütunlar
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff']
    
    # Filtreleme seçenekleri
    list_filter = ['role', 'is_staff', 'is_active']
    
    # Kullanıcı düzenleme ekranına 'role' alanını ekliyoruz
    fieldsets = UserAdmin.fieldsets + (
        ('Rol Bilgisi', {'fields': ('role',)}),
    )
    
    # Kullanıcı ekleme ekranına da 'role' alanını ekliyoruz
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Rol Bilgisi', {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)