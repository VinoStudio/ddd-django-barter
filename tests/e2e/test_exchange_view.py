from uuid6 import UUID
from django.urls import reverse

from src.apps.exchanges import domain as exchange_domain
from src.apps.ads import domain as ad_domain
from src.core.infrastructure.database.models import User

def test_exchange_list_view_all(authenticated_client, sample_exchange, test_user_ad, second_user_ad):
    url = reverse('exchange_list')
    response = authenticated_client.get(url)

    assert response.status_code == 200
    assert b"Test Ad" in response.content

    assert bytes(test_user_ad.title, 'utf-8') in response.content
    assert bytes(second_user_ad.title, 'utf-8') in response.content


def test_exchange_list_view_filter_sent(authenticated_client, sample_exchange, test_user_ad, second_user_ad):
    url = reverse('exchange_list') + '?filter_type=sent'
    response = authenticated_client.get(url)

    assert response.status_code == 200
    assert b"Test Ad" in response.content
    assert bytes(test_user_ad.title, 'utf-8') in response.content
    assert bytes(second_user_ad.title, 'utf-8') in response.content


def test_exchange_list_view_filter_received(
    authenticated_client,
    exchange_repo,
    user,
    second_user,
    second_user_ad,
    test_user_ad
):
    exchange = exchange_domain.Exchange(
        ad_sender_id=second_user_ad.id,
        ad_receiver_id=test_user_ad.id,
        comment="Received exchange proposal"
    )
    exchange_repo.create(exchange)

    url = reverse('exchange_list') + '?filter_type=received'
    response = authenticated_client.get(url)

    assert response.status_code == 200
    assert bytes(test_user_ad.title, 'utf-8') in response.content
    assert bytes(second_user_ad.title, 'utf-8') in response.content


def test_exchange_list_view_filter_status(authenticated_client, exchange_repo, test_user_ad, second_user_ad):
    # Create exchanges with different statuses
    pending_exchange = exchange_domain.Exchange(
        ad_sender_id=test_user_ad.id,
        ad_receiver_id=second_user_ad.id,
        comment="Pending exchange",
        status=exchange_domain.ExchangeStatus.PENDING
    )

    accepted_exchange = exchange_domain.Exchange(
        ad_sender_id=test_user_ad.id,
        ad_receiver_id=second_user_ad.id,
        comment="Accepted exchange",
        status=exchange_domain.ExchangeStatus.ACCEPTED
    )

    rejected_exchange = exchange_domain.Exchange(
        ad_sender_id=test_user_ad.id,
        ad_receiver_id=second_user_ad.id,
        comment="Rejected exchange",
        status=exchange_domain.ExchangeStatus.REJECTED
    )

    exchange_repo.create(pending_exchange)
    exchange_repo.create(accepted_exchange)
    exchange_repo.create(rejected_exchange)

    # Test pending filter
    pending_url = reverse('exchange_list') + '?status=pending'
    pending_response = authenticated_client.get(pending_url)
    assert pending_response.status_code == 200
    assert bytes(test_user_ad.title, 'utf-8') in pending_response.content
    assert bytes(second_user_ad.title, 'utf-8') in pending_response.content

    # Test accepted filter
    accepted_url = reverse('exchange_list') + '?status=accepted'
    accepted_response = authenticated_client.get(accepted_url)
    assert accepted_response.status_code == 200

    assert bytes(test_user_ad.title, 'utf-8') in accepted_response.content
    assert bytes(second_user_ad.title, 'utf-8') in accepted_response.content

    # Test rejected filter
    rejected_url = reverse('exchange_list') + '?status=rejected'
    rejected_response = authenticated_client.get(rejected_url)
    assert rejected_response.status_code == 200
    assert bytes(test_user_ad.title, 'utf-8') in accepted_response.content
    assert bytes(second_user_ad.title, 'utf-8') in accepted_response.content


def test_exchange_list_view_unauthenticated(client):
    url = reverse('exchange_list')
    response = client.get(url)

    assert response.status_code == 302
    assert 'login' in response.url


def test_exchange_detail_view(authenticated_client, sample_exchange, test_user_ad, second_user_ad):
    url = reverse('exchange_detail', args=[sample_exchange.id])
    response = authenticated_client.get(url)

    assert response.status_code == 200
    assert b"Test exchange proposal" in response.content
    assert bytes(test_user_ad.title, 'utf-8') in response.content
    assert bytes(second_user_ad.title, 'utf-8') in response.content


def test_exchange_detail_view_not_found(authenticated_client):
    non_existent_id = UUID('00000000-0000-0000-0000-000000000999')
    url = reverse('exchange_detail', args=[non_existent_id])

    response = authenticated_client.get(url)
    assert response.status_code == 404


def test_exchange_detail_view_not_participant(authenticated_client, exchange_repo, ad_repo):
    # Create two users that are not the authenticated user
    user1 = User.objects.create_user(
        username='user1',
        email='user1@example.com',
        password='password123'
    )

    user2 = User.objects.create_user(
        username='user2',
        email='user2@example.com',
        password='password123'
    )

    # Create ads for these users
    ad1 = ad_domain.Ad(
        user_id=user1.id,
        title="User1 Ad",
        owner_username=user1.username,
        description="User1 description",
        image_url="https://example.com/user1.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    ad2 = ad_domain.Ad(
        user_id=user2.id,
        title="User2 Ad",
        owner_username=user2.username,
        description="User2 description",
        image_url="https://example.com/user2.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    saved_ad1 = ad_repo.create(ad1)
    saved_ad2 = ad_repo.create(ad2)

    # Create exchange between these two users
    exchange = exchange_domain.Exchange(
        ad_sender_id=saved_ad1.id,
        ad_receiver_id=saved_ad2.id,
        comment="Exchange between other users"
    )

    saved_exchange = exchange_repo.create(exchange)

    # Authenticated user tries to view this exchange
    url = reverse('exchange_detail', args=[saved_exchange.id])
    response = authenticated_client.get(url)

    # Should be forbidden
    assert response.status_code == 403


def test_exchange_create_view_get(authenticated_client, second_user_ad, test_user_ad):
    url = reverse('exchange_create', args=[second_user_ad.id])
    response = authenticated_client.get(url)

    assert response.status_code == 200
    assert b'<form' in response.content
    assert bytes(second_user_ad.title, 'utf-8') in response.content
    assert bytes(test_user_ad.title, 'utf-8') in response.content


def test_exchange_create_view_post(authenticated_client, test_user_ad, second_user_ad):
    url = reverse('exchange_create', args=[second_user_ad.id])
    data = {
        'ad_sender_id': str(test_user_ad.id),
        'comment': 'I would like to exchange my item for yours'
    }

    response = authenticated_client.post(url, data, follow=True)

    assert response.status_code == 200
    assert b"Exchange proposal sent successfully!" in response.content
    assert b"I would like to exchange my item for yours" in response.content


def test_exchange_create_view_unauthenticated(client, second_user_ad):
    url = reverse('exchange_create', args=[second_user_ad.id])
    response = client.get(url)

    assert response.status_code == 302
    assert 'login' in response.url


def test_exchange_update_view(second_authenticated_client, sample_exchange):
    url = reverse('exchange_update', args=[sample_exchange.id])
    data = {
        'status': exchange_domain.ExchangeStatus.ACCEPTED.value
    }

    response = second_authenticated_client.post(url, data, follow=True)

    assert response.status_code == 200
    assert b"Exchange status updated to accepted!" in response.content
    assert b"accepted" in response.content

    # Verify that both ads are now traded
    ad_sender_url = reverse('ad_detail', args=[sample_exchange.ad_sender_id])
    ad_receiver_url = reverse('ad_detail', args=[sample_exchange.ad_receiver_id])

    sender_response = second_authenticated_client.get(ad_sender_url)
    receiver_response = second_authenticated_client.get(ad_receiver_url)

    assert b"traded" in sender_response.content
    assert b"traded" in receiver_response.content


def test_exchange_update_view_reject(second_authenticated_client, exchange_repo, test_user_ad, second_user_ad):
    # Create a new exchange proposal
    exchange = exchange_domain.Exchange(
        ad_sender_id=test_user_ad.id,
        ad_receiver_id=second_user_ad.id,
        comment="Exchange to reject"
    )

    saved_exchange = exchange_repo.create(exchange)

    url = reverse('exchange_update', args=[saved_exchange.id])
    data = {
        'status': exchange_domain.ExchangeStatus.REJECTED.value
    }

    response = second_authenticated_client.post(url, data, follow=True)

    assert response.status_code == 200
    assert b"Exchange status updated to rejected!" in response.content
    assert b"rejected" in response.content

    # Verify that ads remain active
    ad_sender_url = reverse('ad_detail', args=[saved_exchange.ad_sender_id])
    ad_receiver_url = reverse('ad_detail', args=[saved_exchange.ad_receiver_id])

    sender_response = second_authenticated_client.get(ad_sender_url)
    receiver_response = second_authenticated_client.get(ad_receiver_url)

    assert b"active" in sender_response.content
    assert b"active" in receiver_response.content


def test_exchange_update_view_permission_denied(authenticated_client, sample_exchange):
    # First user tries to update the exchange status (should be the receiver's job)
    url = reverse('exchange_update', args=[sample_exchange.id])
    data = {
        'status': exchange_domain.ExchangeStatus.ACCEPTED.value
    }

    response = authenticated_client.post(url, data)

    # Should raise permission denied
    assert response.status_code == 403 or b"Permission denied" in response.content


def test_exchange_delete_view(authenticated_client, sample_exchange):
    url = reverse('exchange_delete', args=[sample_exchange.id])

    response = authenticated_client.post(url, follow=True)

    assert response.status_code == 200
    assert b"Exchange proposal has been cancelled" in response.content

    # Verify it's gone
    detail_url = reverse('exchange_detail', args=[sample_exchange.id])
    detail_response = authenticated_client.get(detail_url)
    assert detail_response.status_code == 404


def test_exchange_delete_view_not_sender(second_authenticated_client, sample_exchange):
    url = reverse('exchange_delete', args=[sample_exchange.id])

    response = second_authenticated_client.post(url)

    # Second user is the receiver, not the sender, so shouldn't be able to delete
    assert response.status_code == 403


def test_exchange_delete_view_unauthenticated(client, sample_exchange):
    url = reverse('exchange_delete', args=[sample_exchange.id])

    response = client.post(url)

    assert response.status_code == 302
    assert 'login' in response.url


def test_complete_exchange_journey(authenticated_client, second_authenticated_client, ad_repo, exchange_repo):
    # 1. First user creates an ad
    first_ad_url = reverse('ad_create')
    first_ad_data = {
        'title': 'First User Journey Item',
        'description': 'Item from first user for exchange journey',
        'image_url': 'https://example.com/first_journey.jpg',
        'category': ad_domain.ItemCategory.ELECTRONICS.value,
        'condition': ad_domain.ItemCondition.NEW.value,
        'status': ad_domain.ItemStatus.ACTIVE.value
    }

    first_ad_response = authenticated_client.post(first_ad_url, first_ad_data, follow=True)

    # Get the ID of the created ad (we'll need to find it in the database)
    first_user_ads = ad_repo.find_user_ads(authenticated_client.session['_auth_user_id'])
    first_ad = next((ad for ad in first_user_ads if ad.title == 'First User Journey Item'), None)
    first_ad_id = first_ad.id

    # 2. Second user creates an ad
    second_ad_url = reverse('ad_create')
    second_ad_data = {
        'title': 'Second User Journey Item',
        'description': 'Item from second user for exchange journey',
        'image_url': 'https://example.com/second_journey.jpg',
        'category': ad_domain.ItemCategory.BOOKS.value,
        'condition': ad_domain.ItemCondition.USED.value,
        'status': ad_domain.ItemStatus.ACTIVE.value
    }

    second_ad_response = second_authenticated_client.post(second_ad_url, second_ad_data, follow=True)

    # Get the ID of the created ad
    second_user_ads = ad_repo.find_user_ads(second_authenticated_client.session['_auth_user_id'])
    second_ad = next((ad for ad in second_user_ads if ad.title == 'Second User Journey Item'), None)
    second_ad_id = second_ad.id

    # 3. First user proposes an exchange
    create_exchange_url = reverse('exchange_create', args=[second_ad_id])
    exchange_data = {
        'ad_sender_id': str(first_ad_id),
        'comment': 'Complete journey exchange proposal'
    }

    exchange_response = authenticated_client.post(create_exchange_url, exchange_data, follow=True)
    assert b"Exchange proposal sent successfully!" in exchange_response.content

    # Find the created exchange
    exchanges = exchange_repo.find_by_sender_ad_id(first_ad_id)
    exchange_id = exchanges[0].id

    # 4. Second user views and accepts the exchange
    exchange_detail_url = reverse('exchange_detail', args=[exchange_id])
    detail_response = second_authenticated_client.get(exchange_detail_url)
    assert b"Complete journey exchange proposal" in detail_response.content

    # Accept the exchange
    update_url = reverse('exchange_update', args=[exchange_id])
    update_data = {
        'status': exchange_domain.ExchangeStatus.ACCEPTED.value
    }

    update_response = second_authenticated_client.post(update_url, update_data, follow=True)
    assert b"Exchange status updated to accepted!" in update_response.content

    # 5. Verify both ads are now traded
    first_ad_detail_url = reverse('ad_detail', args=[first_ad_id])
    second_ad_detail_url = reverse('ad_detail', args=[second_ad_id])

    first_ad_response = authenticated_client.get(first_ad_detail_url)
    second_ad_response = second_authenticated_client.get(second_ad_detail_url)

    assert b"traded" in first_ad_response.content
    assert b"traded" in second_ad_response.content


def test_rejected_exchange_journey(authenticated_client, second_authenticated_client, ad_repo, exchange_repo):
    # Similar to the complete exchange journey, but with rejection

    # 1. First user creates an ad
    first_ad = ad_domain.Ad(
        user_id=UUID(authenticated_client.session['_auth_user_id']),
        title="Rejected Journey Item",
        owner_username="testuser",
        description="Item for rejection test",
        image_url="https://example.com/reject_journey.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    # 2. Second user creates an ad
    second_ad = ad_domain.Ad(
        user_id=UUID(second_authenticated_client.session['_auth_user_id']),
        title="Reject Receiver Item",
        owner_username="seconduser",
        description="Item that will reject exchange",
        image_url="https://example.com/reject_receiver.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    saved_first_ad = ad_repo.create(first_ad)
    saved_second_ad = ad_repo.create(second_ad)

    # 3. First user proposes an exchange
    create_exchange_url = reverse('exchange_create', args=[saved_second_ad.id])
    exchange_data = {
        'ad_sender_id': str(saved_first_ad.id),
        'comment': 'Exchange that will be rejected'
    }

    exchange_response = authenticated_client.post(create_exchange_url, exchange_data, follow=True)
    assert b"Exchange proposal sent successfully!" in exchange_response.content

    # Find the created exchange
    exchanges = exchange_repo.find_by_sender_ad_id(saved_first_ad.id)
    exchange_id = exchanges[0].id

    # 4. Second user views and rejects the exchange
    exchange_detail_url = reverse('exchange_detail', args=[exchange_id])
    detail_response = second_authenticated_client.get(exchange_detail_url)
    assert b"Exchange that will be rejected" in detail_response.content

    # Reject the exchange
    update_url = reverse('exchange_update', args=[exchange_id])
    update_data = {
        'status': exchange_domain.ExchangeStatus.REJECTED.value
    }

    update_response = second_authenticated_client.post(update_url, update_data, follow=True)
    assert b"Exchange status updated to rejected!" in update_response.content

    # 5. Verify both ads are still active
    first_ad_detail_url = reverse('ad_detail', args=[saved_first_ad.id])
    second_ad_detail_url = reverse('ad_detail', args=[saved_second_ad.id])

    first_ad_response = authenticated_client.get(first_ad_detail_url)
    second_ad_response = second_authenticated_client.get(second_ad_detail_url)

    assert b"active" in first_ad_response.content
    assert b"active" in second_ad_response.content