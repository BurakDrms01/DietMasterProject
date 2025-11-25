from django.db import models
from django.conf import settings  # User modeli için gerekli

class DietPlan(models.Model):
    name = models.CharField("Paket Adı", max_length=100) 
    price = models.DecimalField("Fiyat", max_digits=10, decimal_places=2)
    currency = models.CharField("Para Birimi", max_length=3, default="₺")
    duration_days = models.PositiveIntegerField("Süre (Gün)", default=30)
    description = models.TextField("Kısa Açıklama", blank=True)
    
    # Görsel Ayarlar
    is_popular = models.BooleanField("En Popüler", default=False)
    icon_class = models.CharField("İkon Class", max_length=50, default="bi-star", help_text="Bootstrap Icon")
    color_theme = models.CharField("Renk Teması", max_length=20, default="primary", help_text="primary, success, warning vb.")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class PlanFeature(models.Model):
    """Paketin özelliklerini madde madde tutar"""
    plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE, related_name="features")
    title = models.CharField("Özellik", max_length=255)
    is_included = models.BooleanField("Dahil mi?", default=True)

    def __str__(self):
        return self.title

class PlanRequest(models.Model):
    """Kullanıcının paket taleplerini tutar"""
    STATUS_CHOICES = [
        ('pending', 'Onay Bekliyor'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="plan_requests")
    plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    admin_note = models.TextField("Admin Notu", blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.plan} ({self.get_status_display()})"