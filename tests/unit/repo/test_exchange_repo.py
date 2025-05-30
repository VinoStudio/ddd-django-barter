from uuid import UUID
from src.apps.ads import domain as ad_domain
from src.apps.exchanges import domain as exchange_domain


def test_exchange_repo_create_and_find(exchange_repo, ad_repo, user):
    ad1 = ad_domain.Ad(
        user_id=user.id,
        title="Repo Test Ad 1",
        owner_username=user.username,
        description="First repo test ad",
        image_url="https://example.com/repo1.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    ad2 = ad_domain.Ad(
        user_id=user.id,
        title="Repo Test Ad 2",
        owner_username=user.username,
        description="Second repo test ad",
        image_url="https://example.com/repo2.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    saved_ad1 = ad_repo.create(ad1)
    saved_ad2 = ad_repo.create(ad2)

    exchange = exchange_domain.Exchange(
        ad_sender_id=saved_ad1.id,
        ad_receiver_id=saved_ad2.id,
        comment="Repo test exchange"
    )

    saved_exchange = exchange_repo.create(exchange)

    found_exchange = exchange_repo.find_by_id(saved_exchange.id)

    assert found_exchange is not None
    assert found_exchange.id == saved_exchange.id
    assert found_exchange.ad_sender_id == saved_ad1.id
    assert found_exchange.ad_receiver_id == saved_ad2.id
    assert found_exchange.comment == "Repo test exchange"
    assert found_exchange.status == exchange_domain.ExchangeStatus.PENDING


def test_exchange_repo_find_nonexistent(exchange_repo):
    non_existent_id = UUID('00000000-0000-0000-0000-000000000999')
    result = exchange_repo.find_by_id(non_existent_id)

    assert result is None


def test_exchange_repo_delete_nonexistent(exchange_repo):
    non_existent_id = UUID('00000000-0000-0000-0000-000000000999')
    result = exchange_repo.delete(non_existent_id)

    assert result is False


def test_exchange_repo_find_user_proposals_empty(exchange_repo):
    non_existent_user_id = UUID('00000000-0000-0000-0000-000000000999')
    results = exchange_repo.find_user_proposals(non_existent_user_id)

    assert isinstance(results, list)
    assert len(results) == 0


def test_ad_repo_batch_operations(user, ad_repo):
    ads_to_create = [
        ad_domain.Ad(
            user_id=user.id,
            title=f"Batch Ad {i}",
            owner_username=user.username,
            description=f"Batch ad description {i}",
            image_url=f"https://example.com/batch{i}.jpg",
            category=ad_domain.ItemCategory.ELECTRONICS,
            condition=ad_domain.ItemCondition.NEW,
            status=ad_domain.ItemStatus.ACTIVE
        ) for i in range(1, 6)
    ]

    created_ads = [ad_repo.create(ad) for ad in ads_to_create]
    assert len(created_ads) == 5

    user_ads = ad_repo.find_user_ads(user.id)
    assert len(user_ads) >= 5

    created_titles = [ad.title for ad in created_ads]
    found_titles = [ad.title for ad in user_ads]

    for title in created_titles:
        assert title in found_titles


def test_exchange_repo_update_status(exchange_repo, ad_repo, user):
    ad1 = ad_domain.Ad(
        user_id=user.id,
        title="Update Status Ad 1",
        owner_username=user.username,
        description="First update status ad",
        image_url="https://example.com/update1.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    ad2 = ad_domain.Ad(
        user_id=user.id,
        title="Update Status Ad 2",
        owner_username=user.username,
        description="Second update status ad",
        image_url="https://example.com/update2.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    saved_ad1 = ad_repo.create(ad1)
    saved_ad2 = ad_repo.create(ad2)

    exchange = exchange_domain.Exchange(
        ad_sender_id=saved_ad1.id,
        ad_receiver_id=saved_ad2.id,
        comment="Update status test"
    )

    saved_exchange = exchange_repo.create(exchange)

    saved_exchange.status = exchange_domain.ExchangeStatus.ACCEPTED
    updated_exchange = exchange_repo.update_status(saved_exchange)

    assert updated_exchange.status == exchange_domain.ExchangeStatus.ACCEPTED

    found_exchange = exchange_repo.find_by_id(saved_exchange.id)
    assert found_exchange.status == exchange_domain.ExchangeStatus.ACCEPTED