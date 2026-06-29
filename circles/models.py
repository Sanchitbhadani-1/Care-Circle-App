from django.db import models
from django.conf import settings


class CareCircle(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_circles",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
