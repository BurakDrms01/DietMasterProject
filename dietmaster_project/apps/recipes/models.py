from django.db import models
from django.urls import reverse
from django.conf import settings # User modeli için

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    slug = models.SlugField(unique=True, verbose_name="Slug")

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"

    def __str__(self):
        return self.name

class Recipe(models.Model):
    # DURUM SEÇENEKLERİ
    STATUS_CHOICES = (
        ('PENDING', 'Onay Bekliyor'),
        ('APPROVED', 'Yayında'),
        ('REJECTED', 'Reddedildi'),
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Ekleyen"
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='recipes', verbose_name="Kategori")
    title = models.CharField(max_length=200, verbose_name="Tarif Başlığı")
    image = models.ImageField(upload_to='recipes/', verbose_name="Kapak Fotoğrafı")
    
    ingredients = models.TextField(verbose_name="Malzemeler", help_text="Her malzemeyi yeni bir satıra yazın.")
    instructions = models.TextField(verbose_name="Hazırlanışı", help_text="Her adımı yeni bir satıra yazın.")
    
    calories = models.PositiveIntegerField(verbose_name="Kalori (kcal)")
    prep_time = models.PositiveIntegerField(verbose_name="Hazırlama Süresi (dk)")
    
    # YENİ ALAN: Durum
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='APPROVED', verbose_name="Durum")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tarif"
        verbose_name_plural = "Tarifler"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('recipes:detail', kwargs={'pk': self.pk})

    @property
    def ingredient_list(self):
        return [x.strip() for x in self.ingredients.split('\n') if x.strip()]

    @property
    def instruction_list(self):
        return [x.strip() for x in self.instructions.split('\n') if x.strip()]