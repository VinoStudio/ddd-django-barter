import os
import django
import sys
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.test_settings')
django.setup()


from django.db import connection
from django.contrib.auth.models import Permission, Group, ContentType
from django.contrib.sessions.models import Session
from src.apps.ads.infrastructure.database.models import Ad
from src.apps.exchanges.infrastructure.database.models import Exchange
from src.apps.ads.infrastructure.repository.ad_repo import AdRepository
from src.core.infrastructure.database.models import User
from src.apps.ads.application.services.ad_service import AdService
from src.apps.exchanges import domain as exchange_domain
from src.apps.ads import domain as ad_domain
from src.apps.exchanges.application.services.exchange_service import ExchangeService
from src.apps.exchanges.infrastructure.repository.exchange_repo import ExchangeRepository
from django.test import Client


@pytest.fixture(scope='session', autouse=True)
def create_test_db():
    models = [User, Permission, Group, Session, ContentType, Ad, Exchange]

    with connection.schema_editor() as schema_editor:
        for model in models:
            schema_editor.create_model(model)

    yield

    with connection.schema_editor() as schema_editor:
        for model in models:
            schema_editor.delete_model(model)


@pytest.fixture(scope='session', autouse=True)
def test_user():
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpassword123'
    )
    return user

@pytest.fixture
def user():
    return User.objects.get(username='testuser')

@pytest.fixture
def ad_service():
    return AdService()

@pytest.fixture
def ad_repo():
    return AdRepository()

@pytest.fixture
def exchange_service():
    return ExchangeService()

@pytest.fixture
def exchange_repo():
    return ExchangeRepository

@pytest.fixture(scope='session', autouse=True)
def sender_user_create():
    return User.objects.create_user(username='sender', password='password')

@pytest.fixture
def sender_user():
    return User.objects.get(username='sender')

@pytest.fixture(scope='session', autouse=True)
def receiver_user_create():
    return User.objects.create_user(username='receiver', password='password')


@pytest.fixture
def receiver_user():
    return User.objects.get(username='receiver')


@pytest.fixture
def client():
    return Client()

@pytest.fixture
def authenticated_client(client, user):
    client.force_login(user)
    return client

@pytest.fixture(scope='session', autouse=True)
def second_user_create():
    user = User.objects.create_user(
        username='seconduser',
        email='second@example.com',
        password='password123'
    )
    return user

@pytest.fixture
def second_user():
    return User.objects.get(username='seconduser')

@pytest.fixture
def second_authenticated_client(client, second_user):
    client.force_login(second_user)
    return client


@pytest.fixture
def test_user_ad(user, ad_repo):
    ad = ad_domain.Ad(
        user_id=user.id,
        title="Test Ad",
        owner_username=user.username,
        description="This is a test ad for edge-to-edge testing",
        image_url="https://example.com/test.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )
    return ad_repo.create(ad)

@pytest.fixture
def second_user_ad(second_user, ad_repo):
    ad = ad_domain.Ad(
        user_id=second_user.id,
        title="Second User Ad",
        owner_username=second_user.username,
        description="This is a test ad from the second user",
        image_url="https://example.com/second.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )
    return ad_repo.create(ad)

@pytest.fixture
def sample_exchange(test_user_ad, second_user_ad, exchange_repo):
    exchange = exchange_domain.Exchange(
        ad_sender_id=test_user_ad.id,
        ad_receiver_id=second_user_ad.id,
        comment="Test exchange proposal"
    )
    return exchange_repo.create(exchange)