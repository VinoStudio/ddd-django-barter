from uuid6 import uuid7
from django.contrib.auth.models import AbstractUser
from django.db import models


class TimedBaseModel(models.Model):
    created_at = models.DateTimeField(
        verbose_name='Created at',
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name='Updated at',
        auto_now=True,
    )

    class Meta:
        abstract = True


class User(AbstractUser, TimedBaseModel):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)

    def __str__(self):
        return self.username

    class Meta:
        app_label = 'user'
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'