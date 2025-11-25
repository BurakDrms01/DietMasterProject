from django.db import models
from django.conf import settings

class ChatMessage(models.Model):
    SENDER_TYPES = [
        ('client', 'Danışan'),
        ('dietitian', 'Diyetisyen'),
        ('ai', 'AI Asistan'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages")
    sender_type = models.CharField(max_length=20, choices=SENDER_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to='chat_images/', blank=True, null=True) 

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.sender_type}: {self.message[:20]}"