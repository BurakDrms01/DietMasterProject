from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Q
from .models import MealPhoto
from apps.gamification.models import Task, TaskCompletion

@receiver(post_save, sender=MealPhoto)
def check_photo_tasks(sender, instance, created, **kwargs):
    """
    Yemek fotoğrafı yüklendiğinde:
    1. O gün için geçerli olan,
    2. 'Fotoğraf Yükleme' tipinde olan,
    3. VE YÜKLENEN YEMEK TİPİYLE EŞLEŞEN (Örn: Sadece Öğle Yemeği)
    görevleri bulur ve tamamlar.
    """
    if created:
        user = instance.user
        today = timezone.now().date()
        
        # 1. Filtreleme: Sadece ilgili öğün tipindeki görevleri çek
        photo_tasks = Task.objects.filter(
            task_type=Task.TaskType.PHOTO,
            related_meal_type=instance.meal_type,  # <-- İŞTE ÇÖZÜM BURADA: Tipe göre filtrele
            is_active=True,
            start_date__lte=today
        ).filter(
            Q(end_date__gte=today) | Q(end_date__isnull=True)
        )

        # 2. Yetki ve Tamamlama Kontrolü
        for task in photo_tasks:
            # Görev herkese açıksa VEYA kullanıcıya özel atanmışsa
            if task.is_for_everyone or user in task.assigned_users.all():
                
                # Zaten tamamlanmış mı kontrol et
                already_completed = TaskCompletion.objects.filter(
                    user=user,
                    task=task,
                    completion_date=today
                ).exists()
                
                if not already_completed:
                    # Görevi tamamla
                    TaskCompletion.objects.create(
                        user=user,
                        task=task,
                        meal_photo=instance
                    )