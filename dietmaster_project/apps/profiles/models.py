from django.db import models
from django.conf import settings
from datetime import date
from django.utils import timezone

class PatientProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Erkek'),
        ('F', 'Kadın'),
    ]

    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', 'Hareketsiz (Masa başı)'),
        ('light', 'Az Hareketli (Haftada 1-3 gün spor)'),
        ('moderate', 'Orta Hareketli (Haftada 3-5 gün spor)'),
        ('active', 'Çok Hareketli (Haftada 6-7 gün spor)'),
        ('athlete', 'Profesyonel Sporcu'),
    ]
    
    # Su İçme Alışkanlığı
    WATER_HABIT_CHOICES = [
        ('bad', 'Çok az içiyorum (<1L)'),
        ('medium', 'Ortalama (1.5L - 2L)'),
        ('good', 'Çok iyi (>2.5L)'),
    ]

    # Beslenme Tipi
    DIET_PREFERENCE_CHOICES = [
        ('standard', 'Her şeyi yerim'),
        ('vegan', 'Vegan'),
        ('vegetarian', 'Vejetaryen'),
        ('ketogenic', 'Ketojenik'),
        ('gluten_free', 'Glutensiz'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    
    # Fiziksel Özellikler
    birth_date = models.DateField("Doğum Tarihi", null=True, blank=True)
    gender = models.CharField("Cinsiyet", max_length=1, choices=GENDER_CHOICES, default='F')
    height = models.PositiveIntegerField("Boy (cm)", help_text="Örn: 175", null=True, blank=True)
    weight = models.DecimalField("Kilo (kg)", max_digits=5, decimal_places=1, help_text="Örn: 70.5", null=True, blank=True)
    
    # Sağlık Bilgileri
    chronic_diseases = models.TextField("Kronik Rahatsızlıklar", blank=True, help_text="Örn: Diyabet Tip 2, Haşimato")
    allergies = models.TextField("Alerjiler & İntoleranslar", blank=True, help_text="Örn: Gluten, Laktoz")
    medications = models.TextField("Kullanılan İlaçlar", blank=True, help_text="Düzenli kullanılan ilaçlar.")
    
    # Hedef ve Yaşam Tarzı (Sihirbazdan Gelenler)
    activity_level = models.CharField("Aktivite Seviyesi", max_length=20, choices=ACTIVITY_LEVEL_CHOICES, default='sedentary')
    daily_activity = models.CharField("Günlük Hareket", max_length=50, choices=ACTIVITY_LEVEL_CHOICES, default='sedentary') 
    water_habit = models.CharField("Su İçme Alışkanlığı", max_length=50, choices=WATER_HABIT_CHOICES, default='medium')
    
    goal_weight = models.DecimalField("Hedef Kilo", max_digits=5, decimal_places=1, null=True, blank=True)
    target_date = models.DateField("Hedef Tarih", null=True, blank=True, help_text="Bu kiloya ne zaman ulaşmak istiyorsun?")
    motivation_level = models.IntegerField("Motivasyon Seviyesi (1-10)", default=5)
    
    # Beslenme Tercihleri
    diet_preference = models.CharField("Beslenme Tipi", max_length=50, choices=DIET_PREFERENCE_CHOICES, default='standard')
    disliked_foods = models.TextField("Sevmediği Besinler", blank=True, help_text="Örn: Brokoli, Mantar...")
    
    # Durum Kontrolü
    is_onboarding_complete = models.BooleanField("Sihirbaz Tamamlandı mı?", default=False)
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} Profili"

    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    @property
    def bmi(self):
        if self.height and self.weight:
            height_in_meters = self.height / 100
            return round(float(self.weight) / (height_in_meters ** 2), 1)
        return None

    @property
    def bmi_status(self):
        bmi = self.bmi
        if not bmi: return "Belirsiz"
        if bmi < 18.5: return "Zayıf"
        if 18.5 <= bmi < 25: return "Normal"
        if 25 <= bmi < 30: return "Fazla Kilolu"
        return "Obez"
    
    @property
    def weight_difference(self):
        if self.weight and self.goal_weight:
            return self.weight - self.goal_weight
        return None

    @property
    def weight_status_text(self):
        diff = self.weight_difference
        if diff is None: return "Hedef Belirlenmedi"
        if diff > 0: return f"Hedefe {abs(diff)} kg kaldı (Verilecek)"
        elif diff < 0: return f"Hedefe {abs(diff)} kg kaldı (Alınacak)"
        else: return "Tebrikler! Hedef kilonuzdasınız. 🎉"
        
        
class WeightHistory(models.Model):
    profile = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='weight_history')
    weight = models.DecimalField(max_digits=5, decimal_places=1)
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.profile.user} - {self.weight}kg ({self.date})"

class DailyWaterIntake(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='water_intakes'
    )
    date = models.DateField(default=timezone.now) 
    current_amount = models.PositiveIntegerField(default=0)
    target_amount = models.PositiveIntegerField(default=2500)

    class Meta:
        unique_together = ('user', 'date')

    @property
    def progress_percent(self):
        if self.target_amount == 0: return 0
        percent = (self.current_amount / self.target_amount) * 100
        return min(percent, 100)

    def __str__(self):
        return f"{self.user} - {self.current_amount}/{self.target_amount}ml"