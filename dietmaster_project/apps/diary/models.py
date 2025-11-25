from django.db import models
from django.conf import settings  # GÜNCELLENDİ: User modelini buradan alacağız
from PIL import Image  # Resim işleme için
import os

class MealPhoto(models.Model):
    # Seçenekleri dışarıdan erişilebilir kılıyoruz
    class MealType(models.TextChoices):
        BREAKFAST = 'kahvalti', 'Kahvaltı'
        LUNCH = 'ogle', 'Öğle Yemeği'
        DINNER = 'aksam', 'Akşam Yemeği'
        SNACK = 'araogun', 'Ara Öğün'

    # GÜNCELLENDİ: settings.AUTH_USER_MODEL kullanıldı
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='meal_photos'
    )
    
    photo = models.ImageField(upload_to='meal_photos/%Y/%m/%d/', verbose_name="Fotoğraf")
    meal_type = models.CharField("Öğün Tipi", max_length=20, choices=MealType.choices)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.get_meal_type_display()}"

    def save(self, *args, **kwargs):
        # 1. Önce normal kaydetme işlemini yap
        super().save(*args, **kwargs)

        # 2. Fotoğrafı aç ve optimize et
        if self.photo:
            try:
                img_path = self.photo.path
                # Dosyanın varlığını kontrol et
                if os.path.exists(img_path):
                    with Image.open(img_path) as img:
                        # Eğer resim çok büyükse küçült (Örn: Max 800x800)
                        if img.height > 800 or img.width > 800:
                            output_size = (800, 800)
                            img.thumbnail(output_size)
                            # Kaliteyi optimize ederek aynı yere kaydet
                            img.save(img_path, optimize=True, quality=70)
            except Exception as e:
                # Resim işleme hatası olursa logla ama akışı bozma
                print(f"Resim optimize edilirken hata: {e}")
    
    # NOT: delete() metodunu sildik, çünkü bu işi Sinyaller yapacak!