from django.db import models
from uuid6 import uuid7
from src.core.infrastructure.database.models import TimedBaseModel
from src.apps.ads.infrastructure.database.models import Ad


class Exchange(TimedBaseModel):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    ad_sender = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='exchange_sender',
    )
    ad_receiver = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='exchange_receiver',
    )
    comment = models.TextField(null=True)
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('accepted', 'accepted'),
        ('rejected', 'rejected'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    class Meta:
        app_label = 'exchange'
        db_table = 'exchange'
        verbose_name = 'Exchange'
        verbose_name_plural = 'Exchanges'
        ordering = ['-created_at']