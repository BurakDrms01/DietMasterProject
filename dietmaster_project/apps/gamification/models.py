from django.db import models
from django.utils import timezone
from django.conf import settings  # GÜNCELLENDİ: User modelini settings'den alacağız
from apps.diary.models import MealPhoto

class Task(models.Model):
    class TaskType(models.TextChoices):
        MANUAL = 'MANUAL', 'Manuel'
        PHOTO = 'PHOTO', 'Fotoğraf'
        WATER = 'WATER', 'Su'

    title = models.CharField("Görev Başlığı", max_length=200)
    description = models.TextField("Açıklama", blank=True)
    points = models.IntegerField("Puan Değeri", default=10)
    task_type = models.CharField("Görev Tipi", max_length=20, choices=TaskType.choices, default=TaskType.MANUAL)
    
    # MealPhoto modelindeki MealType'a erişim
    related_meal_type = models.CharField("İlişkili Öğün", max_length=50, choices=MealPhoto.MealType.choices, blank=True, null=True)
    
    is_active = models.BooleanField("Aktif mi?", default=True)
    is_for_everyone = models.BooleanField("Tüm Danışanlara Ata", default=False)
    
    # GÜNCELLENDİ: User yerine settings.AUTH_USER_MODEL kullanıldı
    assigned_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        blank=True, 
        related_name='assigned_tasks'
    )

    # --- ZAMANLAMA ALANLARI ---
    start_date = models.DateField("Başlangıç Tarihi", default=timezone.now)
    end_date = models.DateField("Bitiş Tarihi", null=True, blank=True, help_text="Boş bırakılırsa süresiz olur.")

    def __str__(self):
        return f"{self.title} ({self.start_date} - {self.end_date or 'Süresiz'})"

class TaskCompletion(models.Model):
    # GÜNCELLENDİ: User yerine settings.AUTH_USER_MODEL kullanıldı
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="task_completions"
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    completion_date = models.DateField("Tamamlanma Tarihi", auto_now_add=True)
    meal_photo = models.ForeignKey(MealPhoto, on_delete=models.SET_NULL, null=True, blank=True)


    class Meta:
        unique_together = ('user', 'task', 'completion_date')
    
    def __str__(self):
        return f"{self.user} - {self.task}"