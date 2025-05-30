from django.db import models
from uuid6 import uuid7
from src.core.infrastructure.database.models import TimedBaseModel, User


class Ad(TimedBaseModel):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')
    title = models.CharField(max_length=200)
    description = models.TextField(null=True)
    image_url = models.URLField(blank=True, null=True)
    category_choices = [
        ('electronics', 'electronics'),
        ('clothes', 'clothes'),
        ('toys', 'toys'),
        ('books', 'books'),
        ('games', 'games'),
        ('cars', 'cars'),
        ('home', 'home'),
        ('other', 'other'),
    ]
    category = models.CharField(
        max_length=50,
        choices=category_choices,
        default='other',
    )
    condition_choices = [
        ('new', 'new'),
        ('used', 'used'),
    ]
    condition = models.CharField(
        max_length=20,
        choices=condition_choices,
        default='used',
    )
    status_choices = [
        ("active", "active"),
        ("traded","traded"),
        ("archived","archived"),
    ]

    status = models.CharField(
        max_length=20,
        choices=status_choices,
        default='active',
    )

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'ad'
        app_label = 'ad'
        verbose_name = 'Ad'
        verbose_name_plural = 'Ads'
        ordering = ['-created_at']
