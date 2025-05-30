from django.apps import AppConfig


class AdsConfig(AppConfig):
    name = 'src.apps.ads.infrastructure.database'
    label = 'ad'
    default_auto_field = 'django.db.models.BigAutoField'