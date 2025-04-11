from django.db import models

class BotActionLog(models.Model):
    action_type = models.CharField(max_length=50)
    target = models.TextField(blank=True)
    status = models.CharField(max_length=20)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
