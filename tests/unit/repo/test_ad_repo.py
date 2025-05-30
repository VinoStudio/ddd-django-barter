import pytest
from uuid6 import UUID
from django.contrib.auth import get_user_model

from src.apps.ads.infrastructure.database.models import Ad
from src.apps.ads import domain as ad_domain


def test_save_and_get_ad(user, ad_repo):
    # Создаем объект обмена
    ad = ad_domain.Ad(
        user_id=user.id,
        title="Test Ad",
        owner_username=user.username,
        description="This is a test ad",
        image_url="https://example.com/test.jpg",
        category=ad_domain.ItemCategory.CARS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    # Сохраняем объект в репозитории
    saved_ad = ad_repo.create(ad)

    # Получаем из репозитория
    retrieved_ad = ad_repo.find_by_id(saved_ad.id)

    assert retrieved_ad.user_id == user.id
    assert retrieved_ad.title == "Test Ad"
    assert retrieved_ad.description == "This is a test ad"
    assert retrieved_ad.image_url == "https://example.com/test.jpg"
    assert retrieved_ad.category == ad_domain.ItemCategory.CARS
    assert retrieved_ad.condition == ad_domain.ItemCondition.NEW


def test_ad_repo_search_with_multiple_criteria(user, ad_repo):
    # Create ads with various combinations of properties
    ad1 = ad_domain.Ad(
        user_id=user.id,
        title="New Gaming Laptop",
        owner_username=user.username,
        description="High-end gaming laptop, barely used",
        image_url="https://example.com/gaming_laptop.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    ad2 = ad_domain.Ad(
        user_id=user.id,
        title="Used Gaming Console",
        owner_username=user.username,
        description="Previous generation gaming console",
        image_url="https://example.com/console.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    ad3 = ad_domain.Ad(
        user_id=user.id,
        title="New Fiction Book",
        owner_username=user.username,
        description="Bestseller fiction book, brand new",
        image_url="https://example.com/book.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    ad_repo.create(ad1)
    ad_repo.create(ad2)
    ad_repo.create(ad3)

    # Test search with multiple criteria - should match ad1
    results = ad_repo.search(
        category=ad_domain.ItemCategory.ELECTRONICS.value,
        condition=ad_domain.ItemCondition.NEW.value,
        status=ad_domain.ItemStatus.ACTIVE.value,
        keyword="gaming",
        page=1,
        page_size=10
    )

    assert len(results) == 1
    assert results[0].title == "New Gaming Laptop"

    # Test search with broader criteria - should match ad1 and ad2
    results = ad_repo.search(
        category=ad_domain.ItemCategory.ELECTRONICS.value,
        condition=None,
        status=ad_domain.ItemStatus.ACTIVE.value,
        keyword="gaming",
        page=1,
        page_size=10
    )

    assert len(results) == 2
    titles = [ad.title for ad in results]
    assert "New Gaming Laptop" in titles
    assert "Used Gaming Console" in titles

    # Test search for new items across categories
    results = ad_repo.search(
        category=None,
        condition=ad_domain.ItemCondition.NEW.value,
        status=ad_domain.ItemStatus.ACTIVE.value,
        keyword="new",
        page=1,
        page_size=10
    )

    assert len(results) >= 2
    titles = [ad.title for ad in results]
    assert "New Gaming Laptop" in titles
    assert "New Fiction Book" in titles


def test_repo_find_by_id(user, ad_repo):
    ad = ad_domain.Ad(
        user_id=user.id,
        title="Test Ad",
        owner_username=user.username,
        description="Test description",
        image_url="https://example.com/test.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )
    saved_ad = ad_repo.create(ad)

    found_ad = ad_repo.find_by_id(saved_ad.id)

    assert found_ad is not None
    assert found_ad.id == saved_ad.id
    assert found_ad.title == saved_ad.title


def test_repo_find_nonexistent_ad(ad_repo):
    non_existent_id = UUID('00000000-0000-0000-0000-000000000999')
    found_ad = ad_repo.find_by_id(non_existent_id)

    assert found_ad is None


def test_repo_find_user_ads(user, ad_repo):
    # Clear existing ads
    Ad.objects.filter(user_id=user.id).delete()

    # Create ads for the user
    ad1 = ad_domain.Ad(
        user_id=user.id,
        title="User Ad 1",
        owner_username=user.username,
        description="User's first ad",
        image_url="https://example.com/user1.jpg",
        category=ad_domain.ItemCategory.OTHER,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )
    ad2 = ad_domain.Ad(
        user_id=user.id,
        title="User Ad 2",
        owner_username=user.username,
        description="User's second ad",
        image_url="https://example.com/user2.jpg",
        category=ad_domain.ItemCategory.CLOTHES,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    ad_repo.create(ad1)
    ad_repo.create(ad2)

    # Create ad for another user\
    User = get_user_model()
    User.objects.create_user(username="otheruser", password="password")
    other_user_id = User.objects.get(username="otheruser").id

    other_ad = ad_domain.Ad(
        user_id=other_user_id,
        title="Other User Ad",
        owner_username="otheruser",
        description="Other user's ad",
        image_url="https://example.com/other.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )
    ad_repo.create(other_ad)

    # Find user ads
    user_ads = ad_repo.find_user_ads(user.id)

    assert len(user_ads) == 2
    assert all(ad.user_id == user.id for ad in user_ads)
    assert "User Ad 1" in [ad.title for ad in user_ads]
    assert "User Ad 2" in [ad.title for ad in user_ads]
    assert "Other User Ad" not in [ad.title for ad in user_ads]


def test_repo_search(user, ad_repo):
    # Create test ads with various properties
    ad_repo.create(ad_domain.Ad(
        user_id=user.id,
        title="Macbook Pro",
        owner_username=user.username,
        description="Apple laptop",
        image_url="https://example.com/mac.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    ))

    ad_repo.create(ad_domain.Ad(
        user_id=user.id,
        title="Dell Laptop",
        owner_username=user.username,
        description="Windows laptop",
        image_url="https://example.com/dell.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    ))

    ad_repo.create(ad_domain.Ad(
        user_id=user.id,
        title="Vintage Table",
        owner_username=user.username,
        description="Antique wooden table",
        image_url="https://example.com/table.jpg",
        category=ad_domain.ItemCategory.CLOTHES,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ARCHIVED
    ))

    # Test search by category
    electronics_results = ad_repo.search(
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=None,
        status=None,
        keyword=None,
        page=1,
        page_size=10
    )

    assert len(electronics_results) == 2
    assert all(ad.category == ad_domain.ItemCategory.ELECTRONICS for ad in electronics_results)

    # Test search by condition
    new_results = ad_repo.search(
        category=None,
        condition=ad_domain.ItemCondition.NEW.value,
        status=None,
        keyword=None,
        page=1,
        page_size=10
    )

    assert len(new_results) >= 1
    assert all(ad.condition == ad_domain.ItemCondition.NEW for ad in new_results)

    # Test search by keyword
    laptop_results = ad_repo.search(
        category=None,
        condition=None,
        status=None,
        keyword="laptop",
        page=1,
        page_size=10
    )

    assert len(laptop_results) >= 2
    assert any("Macbook" in ad.title for ad in laptop_results)
    assert any("Dell" in ad.title for ad in laptop_results)

    # Test combined search
    specific_results = ad_repo.search(
        category=ad_domain.ItemCategory.ELECTRONICS.value,
        condition=ad_domain.ItemCondition.USED.value,
        status=ad_domain.ItemStatus.ACTIVE.value,
        keyword="Apple",
        page=1,
        page_size=10
    )

    assert all(ad.category == ad_domain.ItemCategory.ELECTRONICS for ad in specific_results)
    assert all(ad.condition == ad_domain.ItemCondition.USED for ad in specific_results)
    assert all(ad.status == ad_domain.ItemStatus.ACTIVE for ad in specific_results)