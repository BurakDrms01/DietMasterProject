from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from .models import PatientProfile, WeightHistory
from .models import DailyWaterIntake
from apps.gamification.models import Task, TaskCompletion


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Yeni bir kullanıcı oluşturulduğunda çalışır.
    Sadece Danışanlar (CLIENT) veya Adaylar (NEW_CLIENT) için profil oluşturur.
    """
    if created and instance.role in ['CLIENT', 'NEW_CLIENT']:
        # get_or_create kullanımı daha güvenlidir, çakışmayı önler.
        PatientProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """Kullanıcı kaydedildiğinde profili de tetikler."""
    # Eğer kullanıcının bir profili varsa kaydet
    if hasattr(instance, 'profile'):
        instance.profile.save()

@receiver(post_save, sender=PatientProfile)
def save_weight_history(sender, instance, created, **kwargs):
    """
    Profil güncellendiğinde, eğer kilo verisi girilmişse
    bunu tarihçeye kaydeder.
    """
    if instance.weight:
        today = timezone.now().date()
        
        # update_or_create: 
        # Eğer bugün için bu kişinin bir kilo kaydı varsa GÜNCELLE (update),
        # Yoksa YENİ OLUŞTUR (create).
        WeightHistory.objects.update_or_create(
            profile=instance,
            date=today,
            defaults={'weight': instance.weight}
        )
        
@receiver(post_save, sender=DailyWaterIntake)
def check_water_goal(sender, instance, **kwargs):
    """
    Su hedefine ulaşıldığında (>= %100), o günkü 'WATER' görevini otomatik tamamla.
    """
    if instance.current_amount >= instance.target_amount:
        today = timezone.now().date()
        user = instance.user

        # Bugünün su görevini bul
        water_task = Task.objects.filter(
            task_type=Task.TaskType.WATER,
            is_active=True,
            start_date__lte=today
        ).first()

        if water_task:
            # Zaten tamamlanmamışsa tamamla
            obj, created = TaskCompletion.objects.get_or_create(
                user=user,
                task=water_task,
                completion_date=today
            )