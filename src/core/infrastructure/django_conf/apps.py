from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'src.core.infrastructure.database'
    label = 'user'
    default_auto_field = 'django.db.models.BigAutoField'
