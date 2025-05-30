import pytest
from uuid6 import UUID

from src.apps.ads import domain as ad_domain
from src.apps.ads.application.dto.ad import CreateAdDTO, UpdateAdDTO, AdFilterDTO

from src.core.application.exceptions import PermissionDeniedError
from src.core.infrastructure.exceptions import NotFoundError


def test_create_ad(user, ad_service):
    ad_dto = CreateAdDTO(
        user_id=user.id,
        title="New Test Ad",
        description="Testing ad creation",
        image_url="https://example.com/image.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS.value,
        condition=ad_domain.ItemCondition.NEW.value,
        status=ad_domain.ItemStatus.ACTIVE.value
    )

    created_ad = ad_service.create_ad(ad_dto)

    assert created_ad.id is not None
    assert created_ad.user_id == user.id
    assert created_ad.title == "New Test Ad"
    assert created_ad.description == "Testing ad creation"
    assert created_ad.category == ad_domain.ItemCategory.ELECTRONICS
    assert created_ad.condition == ad_domain.ItemCondition.NEW
    assert created_ad.status == ad_domain.ItemStatus.ACTIVE


def test_update_ad(user, ad_service, ad_repo):
    ad = ad_domain.Ad(
        user_id=user.id,
        title="Original Title",
        owner_username=user.username,
        description="Original description",
        image_url="https://example.com/old.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )
    saved_ad = ad_repo.create(ad)

    update_dto = UpdateAdDTO(
        ad_id=saved_ad.id,
        user_id=user.id,
        title="Updated Title",
        description="Updated description",
        image_url=None,
        category=ad_domain.ItemCategory.CLOTHES.value,
        condition=None
    )

    updated_ad = ad_service.update_ad(update_dto)

    assert updated_ad.id == saved_ad.id
    assert updated_ad.title == "Updated Title"
    assert updated_ad.description == "Updated description"
    assert updated_ad.image_url == "https://example.com/old.jpg"
    assert updated_ad.category == ad_domain.ItemCategory.CLOTHES
    assert updated_ad.condition == ad_domain.ItemCondition.NEW


def test_update_ad_permission_denied(user, ad_service, ad_repo):
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

    other_user_id = UUID('00000000-0000-0000-0000-000000000001')
    update_dto = UpdateAdDTO(
        ad_id=saved_ad.id,
        user_id=other_user_id,
        title="Hacked Title",
        description=None,
        image_url=None,
        category=None,
        condition=None
    )

    with pytest.raises(PermissionDeniedError):
        ad_service.update_ad(update_dto)


def test_update_ad_status(user, ad_service, ad_repo):
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

    updated_ad = ad_service.update_ad_status(
        saved_ad.id,
        ad_domain.ItemStatus.TRADED
    )

    assert updated_ad.id == saved_ad.id
    assert updated_ad.status == ad_domain.ItemStatus.TRADED
    assert updated_ad.title == "Test Ad"

def test_delete_ad(user, ad_service, ad_repo):
    ad = ad_domain.Ad(
        user_id=user.id,
        title="Hello",
        owner_username=user.username,
        description="Test description you",
        image_url="https://example.com/test.jpg",
        category=ad_domain.ItemCategory.CLOTHES,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )
    saved_ad = ad_service.create_ad(ad)

    result = ad_service.delete_ad(saved_ad.id, user.id)

    assert result is True

    with pytest.raises(NotFoundError):
        ad_service.get_ad(saved_ad.id)


def test_delete_ad_wrong_user(user, ad_service, ad_repo):
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

    other_user_id = UUID('00000000-0000-0000-0000-000000000001')

    with pytest.raises(PermissionDeniedError):
        ad_service.delete_ad(saved_ad.id, other_user_id)


def test_get_user_ads(user, ad_service, ad_repo):
    ad1 = ad_domain.Ad(
        user_id=user.id,
        title="Test Ad 1",
        owner_username=user.username,
        description="Test description 1",
        image_url="https://example.com/test1.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )
    ad2 = ad_domain.Ad(
        user_id=user.id,
        title="Test Ad 2",
        owner_username=user.username,
        description="Test description 2",
        image_url="https://example.com/test2.jpg",
        category=ad_domain.ItemCategory.CLOTHES,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    ad_repo.create(ad1)
    ad_repo.create(ad2)

    user_ads = ad_service.get_user_ads(user.id)

    assert len(user_ads) >= 2
    assert any(ad.title == "Test Ad 1" for ad in user_ads)
    assert any(ad.title == "Test Ad 2" for ad in user_ads)


def test_list_ads_with_filters(user, ad_service, ad_repo):
    ad1 = ad_domain.Ad(
        user_id=user.id,
        title="iPhone X",
        owner_username=user.username,
        description="Used iPhone in good condition",
        image_url="https://example.com/iphone.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )
    ad2 = ad_domain.Ad(
        user_id=user.id,
        title="Winter Jacket",
        owner_username=user.username,
        description="New winter jacket",
        image_url="https://example.com/jacket.jpg",
        category=ad_domain.ItemCategory.CLOTHES,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )
    ad3 = ad_domain.Ad(
        user_id=user.id,
        title="Old Book",
        owner_username=user.username,
        description="Vintage book",
        image_url="https://example.com/book.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.TRADED
    )

    ad_repo.create(ad1)
    ad_repo.create(ad2)
    ad_repo.create(ad3)

    filter_category = AdFilterDTO(
        category=ad_domain.ItemCategory.ELECTRONICS.value,
        condition=None,
        status=None,
        keyword=None,
        page=1,
        page_size=10
    )
    category_results = ad_service.list_ads(filter_category)
    assert all(ad.category == ad_domain.ItemCategory.ELECTRONICS for ad in category_results)

    filter_condition = AdFilterDTO(
        category=None,
        condition=ad_domain.ItemCondition.NEW.value,
        status=None,
        keyword=None,
        page=1,
        page_size=10
    )
    condition_results = ad_service.list_ads(filter_condition)
    assert all(ad.condition == ad_domain.ItemCondition.NEW for ad in condition_results)

    filter_status = AdFilterDTO(
        category=None,
        condition=None,
        status=ad_domain.ItemStatus.TRADED.value,
        keyword=None,
        page=1,
        page_size=10
    )
    status_results = ad_service.list_ads(filter_status)
    assert all(ad.status == ad_domain.ItemStatus.TRADED for ad in status_results)

    filter_keyword = AdFilterDTO(
        category=None,
        condition=None,
        status=None,
        keyword="iPhone",
        page=1,
        page_size=10
    )
    keyword_results = ad_service.list_ads(filter_keyword)
    assert any("iPhone" in ad.title for ad in keyword_results)