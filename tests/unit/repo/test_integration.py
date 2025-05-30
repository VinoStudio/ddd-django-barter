


def test_exchange_repo_find_by_sender_ad_id(user, exchange_repo, ad_repo):
    # Create multiple ads
    ad1 = ad_domain.Ad(
        user_id=user.id,
        title="Sender Test 1",
        owner_username=user.username,
        description="First sender test",
        image_url="https://example.com/sender_test1.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    ad2 = ad_domain.Ad(
        user_id=user.id,
        title="Sender Test 2",
        owner_username=user.username,
        description="Second sender test",
        image_url="https://example.com/sender_test2.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    ad3 = ad_domain.Ad(
        user_id=user.id,
        title="Receiver Test",
        owner_username=user.username,
        description="Receiver test",
        image_url="https://example.com/receiver_test.jpg",
        category=ad_domain.ItemCategory.CLOTHING,
        condition=ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    saved_ad1 = ad_repo.create(ad1)
    saved_ad2 = ad_repo.create(ad2)
    saved_ad3 = ad_repo.create(ad3)

    # Create multiple exchanges with the same sender
    exchange1 = domain.Exchange(
        ad_sender_id=saved_ad1.id,
        ad_receiver_id=saved_ad3.id,
        comment="Exchange 1 to 3"
    )

    exchange2 = domain.Exchange(
        ad_sender_id=saved_ad1.id,
        ad_receiver_id=saved_ad3.id,
        comment="Another 1 to 3"
    )

    exchange3 = domain.Exchange(
        ad_sender_id=saved_ad2.id,
        ad_receiver_id=saved_ad3.id,
        comment="2 to 3"
    )

    exchange_repo.create(exchange1)
    exchange_repo.create(exchange2)
    exchange_repo.create(exchange3)

    # Find exchanges by sender ad id
    exchanges_from_ad1 = exchange_repo.find_by_sender_ad_id(saved_ad1.id)

    assert len(exchanges_from_ad1) == 2
    assert all(ex.ad_sender_id == saved_ad1.id for ex in exchanges_from_ad1)

    # Find exchanges by another sender ad id
    exchanges_from_ad2 = exchange_repo.find_by_sender_ad_id(saved_ad2.id)

    assert len(exchanges_from_ad2) == 1
    assert exchanges_from_ad2[0].ad_sender_id == saved_ad2.id


def test_exchange_repo_find_by_receiver_ad_id(user, exchange_repo, ad_repo):
    # Create multiple ads
    ad1 = ad_domain.Ad(
        user_id=user.id,
        title="Receiver Repo Test 1",
        owner_username=user.username,
        description="First receiver repo test",
        image_url="https://example.com/receiver_repo1.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    ad2 = ad_domain.Ad(
        user_id=user.id,
        title="Sender Repo Test",
        owner_username=user.username,
        description="Sender repo test",
        image_url="https://example.com/sender_repo.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    ad3 = ad_domain.Ad(
        user_id=user.id,
        title="Receiver Repo Test 2",
        owner_username=user.username,
        description="Second receiver repo test",
        image_url="https://example.com/receiver_repo2.jpg",
        category=ad_domain.ItemCategory.CLOTHING,
        condition=ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    saved_ad1 = ad_repo.create(ad1)
    saved_ad2 = ad_repo.create(ad2)
    saved_ad3 = ad_repo.create(ad3)

    # Create multiple exchanges with different receivers
    exchange1 = domain.Exchange(
        ad_sender_id=saved_ad2.id,
        ad_receiver_id=saved_ad1.id,
        comment="Sender to Receiver 1"
    )

    exchange2 = domain.Exchange(
        ad_sender_id=saved_ad2.id,
        ad_receiver_id=saved_ad1.id,
        comment="Another to Receiver 1"
    )

    exchange3 = domain.Exchange(
        ad_sender_id=saved_ad2.id,
        ad_receiver_id=saved_ad3.id,
        comment="Sender to Receiver 2"
    )

    exchange_repo.create(exchange1)
    exchange_repo.create(exchange2)
    exchange_repo.create(exchange3)

    # Find exchanges by receiver ad id
    exchanges_to_ad1 = exchange_repo.find_by_receiver_ad_id(saved_ad1.id)

    assert len(exchanges_to_ad1) == 2
    assert all(ex.ad_receiver_id == saved_ad1.id for ex in exchanges_to_ad1)

    # Find exchanges by another receiver ad id
    exchanges_to_ad3 = exchange_repo.find_by_receiver_ad_id(saved_ad3.id)

    assert len(exchanges_to_ad3) == 1
    assert exchanges_to_ad3[0].ad_receiver_id == saved_ad3.id



