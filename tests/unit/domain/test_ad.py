import pytest
from uuid6 import UUID

from src.apps.ads import domain as ad_domain

def test_ad_domain_creation():
    ad = ad_domain.Ad(
        user_id=UUID('00000000-0000-0000-0000-000000000001'),
        title="Test Ad",
        owner_username="testuser",
        description="Test description",
        image_url="https://example.com/test.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    assert ad.title == "Test Ad"
    assert ad.user_id == UUID('00000000-0000-0000-0000-000000000001')
    assert ad.owner_username == "testuser"
    assert ad.category == ad_domain.ItemCategory.ELECTRONICS
    assert ad.condition == ad_domain.ItemCondition.NEW
    assert ad.status == ad_domain.ItemStatus.ACTIVE


def test_ad_domain_is_owner():
    owner_id = UUID('00000000-0000-0000-0000-000000000001')
    other_id = UUID('00000000-0000-0000-0000-000000000002')

    ad = ad_domain.Ad(
        user_id=owner_id,
        title="Test Ad",
        owner_username="testuser",
        description="Test description",
        image_url="https://example.com/test.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    assert ad.is_owner(owner_id) is True
    assert ad.is_owner(other_id) is False


def test_item_category_validation():
    # Valid category
    valid_category = ad_domain.ItemCategory.ELECTRONICS
    assert valid_category == ad_domain.ItemCategory.ELECTRONICS

    # Test creation from string value
    from_string = ad_domain.ItemCategory("electronics")
    assert from_string == ad_domain.ItemCategory.ELECTRONICS

    # Invalid category should raise ValueError
    with pytest.raises(ValueError):
        ad_domain.ItemCategory("invalid_category")


def test_item_status_transitions():
    ad = ad_domain.Ad(
        user_id=UUID('00000000-0000-0000-0000-000000000001'),
        title="Test Ad",
        owner_username="testuser",
        description="Test description",
        image_url="https://example.com/test.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    assert ad.status == ad_domain.ItemStatus.ACTIVE

    # Test changing status
    ad.status = ad_domain.ItemStatus.TRADED
    assert ad.status == ad_domain.ItemStatus.TRADED

    # Test creation from string
    ad.status = ad_domain.ItemStatus("archived")
    assert ad.status == ad_domain.ItemStatus.ARCHIVED


def test_ad_domain_equality():
    ad1 = ad_domain.Ad(
        id=UUID('00000000-0000-0000-0000-000000000001'),
        user_id=UUID('00000000-0000-0000-0000-000000000002'),
        title="Test Ad",
        owner_username="testuser",
        description="Test description",
        image_url="https://example.com/test.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    # Same ad with same ID
    ad2 = ad_domain.Ad(
        id=UUID('00000000-0000-0000-0000-000000000001'),
        user_id=UUID('00000000-0000-0000-0000-000000000002'),
        title="Different Title",  # Different title shouldn't matter for equality
        owner_username="testuser",
        description="Different description",
        image_url="https://example.com/different.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    # Different ID
    ad3 = ad_domain.Ad(
        id=UUID('00000000-0000-0000-0000-000000000003'),
        user_id=UUID('00000000-0000-0000-0000-000000000002'),
        title="Test Ad",
        owner_username="testuser",
        description="Test description",
        image_url="https://example.com/test.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    # Test equality is based on ID
    assert ad1 == ad2  # Same ID should be equal regardless of other attributes
    assert ad1 != ad3  # Different ID should not be equal


def test_ad_domain_validation():
    # Test with valid data
    valid_ad = ad_domain.Ad(
        user_id=UUID('00000000-0000-0000-0000-000000000001'),
        title="Valid Ad",
        owner_username="testuser",
        description="Valid description",
        image_url="https://example.com/valid.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    assert valid_ad.title == "Valid Ad"

    # Test with invalid category (should raise ValueError)
    with pytest.raises(ValueError):
        invalid_ad = ad_domain.Ad(
            user_id=UUID('00000000-0000-0000-0000-000000000001'),
            title="Invalid Category Ad",
            owner_username="testuser",
            description="Valid description",
            image_url="https://example.com/valid.jpg",
            category=ad_domain.ItemCategory("INVALID_CATEGORY"),  # This should cause an error
            condition=ad_domain.ItemCondition.NEW,
            status=ad_domain.ItemStatus.ACTIVE
        )

    # Test with invalid condition (should raise ValueError)
    with pytest.raises(ValueError):
        invalid_ad = ad_domain.Ad(
            user_id=UUID('00000000-0000-0000-0000-000000000001'),
            title="Invalid Condition Ad",
            owner_username="testuser",
            description="Valid description",
            image_url="https://example.com/valid.jpg",
            category=ad_domain.ItemCategory.ELECTRONICS,
            condition=ad_domain.ItemCondition("INVALID_CONDITION"),  # This should cause an error
            status=ad_domain.ItemStatus.ACTIVE
        )

    # Test with invalid status (should raise ValueError)
    with pytest.raises(ValueError):
        invalid_ad = ad_domain.Ad(
            user_id=UUID('00000000-0000-0000-0000-000000000001'),
            title="Invalid Status Ad",
            owner_username="testuser",
            description="Valid description",
            image_url="https://example.com/valid.jpg",
            category=ad_domain.ItemCategory.ELECTRONICS,
            condition=ad_domain.ItemCondition.NEW,
            status=ad_domain.ItemStatus("INVALID_STATUS")  # This should cause an error
        )


def test_ad_domain_immutability():
    """Test that changing an ad's attributes doesn't affect other ads with the same ID"""
    original_ad = ad_domain.Ad(
        id=UUID('00000000-0000-0000-0000-000000000001'),
        user_id=UUID('00000000-0000-0000-0000-000000000002'),
        title="Original Title",
        owner_username="testuser",
        description="Original description",
        image_url="https://example.com/original.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    modified_ad = ad_domain.Ad(
        id=UUID('00000000-0000-0000-0000-000000000001'),
        user_id=UUID('00000000-0000-0000-0000-000000000002'),
        title="Modified Title",
        owner_username="testuser",
        description="Modified description",
        image_url="https://example.com/modified.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    assert original_ad.id == modified_ad.id
    assert original_ad.title == "Original Title"
    assert modified_ad.title == "Modified Title"

    # Changing status on one doesn't affect the other
    original_ad.status = ad_domain.ItemStatus.TRADED
    assert original_ad.status == ad_domain.ItemStatus.TRADED
    assert modified_ad.status == ad_domain.ItemStatus.ACTIVE