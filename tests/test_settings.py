from src.core.settings import *
import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'src.apps.ads.infrastructure.django_conf.apps.AdsConfig',
    'src.apps.exchanges.infrastructure.django_conf.apps.ExchangesConfig',
    'src.core.infrastructure.django_conf.apps.UserConfig',
]

AUTH_USER_MODEL = 'user.User'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_TEST_DB'),
        'USER': env('POSTGRES_TEST_USER'),
        'PASSWORD': env('POSTGRES_TEST_PASSWORD'),
        'HOST': env('POSTGRES_TEST_HOST'),
        'PORT': env('POSTGRES_TEST_PORT'),
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
