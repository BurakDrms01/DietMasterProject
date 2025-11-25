from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Diyetisyen (Admin)"
        STAFF = "STAFF", "Stajyer"
        CLIENT = "CLIENT", "Danışan"
        NEW_CLIENT = "NEW_CLIENT", "Yeni Üye (Potansiyel)"

    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.NEW_CLIENT,
        verbose_name="Kullanıcı Rolü"
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Telefon Numarası"
    )

    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True,
        verbose_name="Profil Fotoğrafı"
    )

    def save(self, *args, **kwargs):
        if self.role == self.Role.ADMIN:
            self.is_superuser = True
            self.is_staff = True
        elif self.role == self.Role.STAFF:
            self.is_staff = True

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
