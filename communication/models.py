from django.db import models
from core.models import BaseModel
from users.models import User

class Message(BaseModel):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['-created_at']

class Notification(BaseModel):
    NOTIFICATION_TYPE_CHOICES = [('info', 'Info'), ('warning', 'Warning'), ('success', 'Success')]
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

class Announcement(BaseModel):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    target_audience = models.CharField(max_length=20, choices=[('all', 'All'), ('students', 'Students'), ('teachers', 'Teachers')], default='all')
    is_published = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"
