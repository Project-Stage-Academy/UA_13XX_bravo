from django.db import models
from users.models import User

TYPE_CHOICES = [
    ("new_follower", "New Follower"),
    ("new_comment", "New Comment"),
    ("new_like", "New Like"),
    ("new_post", "New Post"),
    ("new_message", "New Message"),
    ("new_report", "New Report"),
    ("new_request", "New Request"),
    ("new_connection", "New Connection"),
    ("new_recommendation", "New Recommendation"),
    ("new_system_notification", "New System Notification"),
]


class Type(models.Model):
    name = models.CharField(
        max_length=200, choices=TYPE_CHOICES, blank=False, null=False
    )

    def __str__(self):
        return self.name


class Entity(models.Model):
    name = models.CharField(max_length=200)


class Notification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        blank=False,
        null=False,
    )
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="notifications",
        blank=True,
        null=True,
    )
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.type} - {self.content}"

    class Meta:
        verbose_name_plural = "Notification"
        unique_together = ("user", "type", "entity")


class NotificationPreference(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
        blank=False,
        null=False,
    )
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.type} - {self.enabled}"
