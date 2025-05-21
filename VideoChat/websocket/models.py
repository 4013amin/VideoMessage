from django.db import models
from django.utils import timezone

class CallSession(models.Model):
    caller = models.CharField(max_length=100)
    receiver = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.caller} → {self.receiver} ({'Active' if self.is_active else 'Ended'})"
