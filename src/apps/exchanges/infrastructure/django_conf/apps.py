from django.apps import AppConfig


class ExchangesConfig(AppConfig):
    name = 'src.apps.exchanges.infrastructure.database'
    label = 'exchange'
    default_auto_field = 'django.db.models.BigAutoField'