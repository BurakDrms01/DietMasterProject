from django.db import models
from django.conf import settings

class DietProgram(models.Model):
    """Bir danışana atanan haftalık/aylık program başlığı"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="diet_programs",
        limit_choices_to={'role': 'CLIENT'} # Sadece Danışanlar seçilebilsin
    )
    title = models.CharField("Program Adı", max_length=100, help_text="Örn: 1. Hafta - Detoks Listesi")
    start_date = models.DateField("Başlangıç Tarihi")
    end_date = models.DateField("Bitiş Tarihi")
    is_active = models.BooleanField("Aktif Program mı?", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"

class DailyMealPlan(models.Model):
    """Programın içindeki günler"""
    DAYS_OF_WEEK = [
        (0, 'Pazartesi'),
        (1, 'Salı'),
        (2, 'Çarşamba'),
        (3, 'Perşembe'),
        (4, 'Cuma'),
        (5, 'Cumartesi'),
        (6, 'Pazar'),
    ]

    program = models.ForeignKey(DietProgram, on_delete=models.CASCADE, related_name="daily_plans")
    day_of_week = models.IntegerField("Gün", choices=DAYS_OF_WEEK)
    
    # Öğünler (Diyetisyen buraya serbest metin yazar)
    breakfast = models.TextField("Kahvaltı", blank=True)
    lunch = models.TextField("Öğle Yemeği", blank=True)
    dinner = models.TextField("Akşam Yemeği", blank=True)
    
    # Ara Öğünler
    snack_1 = models.TextField("Ara Öğün 1 (Kuşluk)", blank=True)
    snack_2 = models.TextField("Ara Öğün 2 (İkindi)", blank=True)
    snack_3 = models.TextField("Ara Öğün 3 (Gece)", blank=True)
    
    class Meta:
        ordering = ['day_of_week']
        unique_together = ('program', 'day_of_week') # Aynı programa aynı günden 2 tane eklenemesin

    def __str__(self):
        return f"{self.program.title} - {self.get_day_of_week_display()}"