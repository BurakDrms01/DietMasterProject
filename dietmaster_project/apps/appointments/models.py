from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class AppointmentQuerySet(models.QuerySet):
    """Custom queryset for Appointment model"""
    
    def active(self):
        """Return only active appointments (pending or approved)"""
        # BUGFIX: Centralize active appointment logic - cancelled/rejected don't block slots
        return self.filter(status__in=['pending', 'approved'])
    
    def for_date(self, date_obj):
        """Return appointments for a specific date"""
        return self.filter(date=date_obj)

class AppointmentManager(models.Manager):
    """Custom manager for Appointment model"""
    
    def get_queryset(self):
        return AppointmentQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def for_date(self, date_obj):
        return self.get_queryset().for_date(date_obj)

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Beklemede')),
        ('approved', _('Onaylandı')),
        ('cancelled', _('İptal Edildi')),
        ('rejected', _('Reddedildi')),
    ]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('Danışan')
    )
    date = models.DateField(_('Tarih'))
    time = models.TimeField(_('Saat'))
    status = models.CharField(
        _('Durum'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    duration = models.PositiveIntegerField(_('Süre (Dakika)'), default=60)
    notes = models.TextField(_('Notlar'), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Custom manager for active appointment queries
    objects = AppointmentManager()

    class Meta:
        ordering = ['-date', '-time']
        verbose_name = _('Randevu')
        verbose_name_plural = _('Randevular')

    def __str__(self):
        return f"{self.client} - {self.date} {self.time}"
    
    def is_active(self):
        """
        Check if this appointment is active (blocks slots).
        
        Returns:
            bool: True if appointment is pending or approved, False otherwise
        """
        # BUGFIX: Centralized logic for determining if appointment blocks slots
        return self.status in ['pending', 'approved']
    
    def is_past(self):
        """
        Check if this appointment is in the past.
        
        Returns:
            bool: True if appointment date is before today
        """
        from datetime import date
        return self.date < date.today()
    
    def should_auto_cancel(self):
        """
        Check if this past appointment should be auto-cancelled.
        
        Returns:
            bool: True if appointment is past and still active
        """
        return self.is_past() and self.is_active()

class DietitianAvailability(models.Model):
    WEEKDAYS = [
        (0, _('Pazartesi')),
        (1, _('Salı')),
        (2, _('Çarşamba')),
        (3, _('Perşembe')),
        (4, _('Cuma')),
        (5, _('Cumartesi')),
        (6, _('Pazar')),
    ]
    
    dietitian = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='availabilities',
        verbose_name=_('Diyetisyen')
    )
    weekday = models.IntegerField(_('Gün'), choices=WEEKDAYS)
    start_time = models.TimeField(_('Başlangıç Saati'))
    end_time = models.TimeField(_('Bitiş Saati'))
    slot_length_minutes = models.PositiveIntegerField(_('Randevu Süresi (Dk)'), default=60)

    class Meta:
        verbose_name = _('Çalışma Saati')
        verbose_name_plural = _('Çalışma Saatleri')
        ordering = ['weekday', 'start_time']
        unique_together = ['dietitian', 'weekday', 'start_time']

    def __str__(self):
        return f"{self.get_weekday_display()} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"
