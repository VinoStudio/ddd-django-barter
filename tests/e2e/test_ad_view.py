from uuid6 import UUID
from django.urls import reverse
from src.apps.ads import domain as ad_domain

def test_ad_list_view(client, test_user_ad):
    url = reverse('ad_list')
    response = client.get(url)

    assert response.status_code == 200
    assert b"Test Ad" in response.content
    assert b"electronics" in response.content


def test_ad_list_view_with_filters(client, ad_repo, user):
    electronics_ad = ad_domain.Ad(
        user_id=user.id,
        title="Electronics Item",
        owner_username=user.username,
        description="Electronics description",
        image_url="https://example.com/electronics.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    book_ad = ad_domain.Ad(
        user_id=user.id,
        title="Book Item",
        owner_username=user.username,
        description="Book description",
        image_url="https://example.com/book.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    sold_ad = ad_domain.Ad(
        user_id=user.id,
        title="Sold Item",
        owner_username=user.username,
        description="Sold description",
        image_url="https://example.com/sold.jpg",
        category=ad_domain.ItemCategory.CLOTHES,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.TRADED
    )

    ad_repo.create(electronics_ad)
    ad_repo.create(book_ad)
    ad_repo.create(sold_ad)

    url = reverse('ad_list') + '?category=electronics'
    response = client.get(url)
    assert response.status_code == 200
    assert b"Electronics Item" in response.content
    assert b"Book Item" not in response.content

    url = reverse('ad_list') + '?condition=used'
    response = client.get(url)
    assert response.status_code == 200
    assert b"Book Item" in response.content
    assert b"Electronics Item" not in response.content

    url = reverse('ad_list') + '?status=traded'
    response = client.get(url)
    assert response.status_code == 200
    assert b"Sold Item" in response.content
    assert b"Electronics Item" not in response.content

    url = reverse('ad_list') + '?search=electronics'
    response = client.get(url)
    assert response.status_code == 200
    assert b"Electronics Item" in response.content
    assert b"Book Item" not in response.content


def test_ad_detail_view(client, test_user_ad):
    url = reverse('ad_detail', args=[test_user_ad.id])
    response = client.get(url)

    assert response.status_code == 200
    assert b"Test Ad" in response.content
    assert b"This is a test ad for edge-to-edge testing" in response.content


def test_ad_detail_view_not_found(client):
    non_existent_id = UUID('00000000-0000-0000-0000-000000000999')
    url = reverse('ad_detail', args=[non_existent_id])

    response = client.get(url)
    assert response.status_code == 404


def test_ad_detail_view_owner_check(authenticated_client, test_user_ad, second_user_ad):
    url = reverse('ad_detail', args=[test_user_ad.id])
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert b"Edit" in response.content

    url = reverse('ad_detail', args=[second_user_ad.id])
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert b"Edit" not in response.content


def test_ad_create_view_get(authenticated_client):
    url = reverse('ad_create')
    response = authenticated_client.get(url)

    assert response.status_code == 200
    assert b'<form' in response.content
    assert b'method="post"' in response.content


def test_ad_create_view_post(authenticated_client, user):
    url = reverse('ad_create')
    data = {
        'user_id': str(user.id),
        'title': 'New Test Ad',
        'description': 'This is a new test ad',
        'image_url': 'https://example.com/new.jpg',
        'category': ad_domain.ItemCategory.ELECTRONICS.value,
        'condition': ad_domain.ItemCondition.NEW.value,
        'status': ad_domain.ItemStatus.ACTIVE.value
    }

    response = authenticated_client.post(url, data, follow=True)

    assert response.status_code == 200
    assert b"Ad created successfully!" in response.content
    assert b"New Test Ad" in response.content
    assert b"This is a new test ad" in response.content


def test_ad_create_view_unauthenticated(client):
    url = reverse('ad_create')
    response = client.get(url)

    assert response.status_code == 302
    assert 'login' in response.url


def test_ad_update_view_get(authenticated_client, test_user_ad):
    url = reverse('ad_update', args=[test_user_ad.id])
    response = authenticated_client.get(url)

    assert response.status_code == 200
    assert b'<form' in response.content
    assert b'Test Ad' in response.content
    assert b'This is a test ad for edge-to-edge testing' in response.content


def test_ad_update_view_post(authenticated_client, test_user_ad):
    url = reverse('ad_update', args=[test_user_ad.id])
    data = {
        'title': 'Updated Test Ad',
        'description': 'This is an updated test ad',
        'image_url': 'https://example.com/updated.jpg',
        'category': ad_domain.ItemCategory.BOOKS.value,
        'condition': ad_domain.ItemCondition.USED.value,
        'status': ad_domain.ItemStatus.ACTIVE.value
    }

    response = authenticated_client.post(url, data, follow=True)

    assert response.status_code == 200
    assert b"Ad updated successfully!" in response.content
    assert b"Updated Test Ad" in response.content
    assert b"This is an updated test ad" in response.content


def test_ad_update_view_not_owner(second_authenticated_client, test_user_ad):
    url = reverse('ad_update', args=[test_user_ad.id])
    response = second_authenticated_client.get(url)

    assert response.status_code == 403


def test_ad_update_view_unauthenticated(client, test_user_ad):
    url = reverse('ad_update', args=[test_user_ad.id])
    response = client.get(url)

    assert response.status_code == 302
    assert 'login' in response.url


def test_ad_delete_view(authenticated_client, test_user_ad):
    url = reverse('ad_delete', args=[test_user_ad.id])
    response = authenticated_client.post(url, follow=True)

    assert response.status_code == 200
    assert b"Ad deleted successfully!" in response.content

    # Check that we can't access the ad detail anymore
    detail_url = reverse('ad_detail', args=[test_user_ad.id])
    detail_response = authenticated_client.get(detail_url)
    assert detail_response.status_code == 404


def test_ad_delete_view_not_owner(second_authenticated_client, test_user_ad):
    url = reverse('ad_delete', args=[test_user_ad.id])
    response = second_authenticated_client.post(url)

    assert response.status_code == 403


def test_ad_delete_view_unauthenticated(client, test_user_ad):
    url = reverse('ad_delete', args=[test_user_ad.id])
    response = client.post(url)

    assert response.status_code == 302
    assert 'login' in response.url


def test_complete_ad_journey(authenticated_client, user, ad_repo):
    create_url = reverse('ad_create')
    create_data = {
        'title': 'Journey Test Ad',
        'description': 'This is an ad for the journey test',
        'image_url': 'https://example.com/journey.jpg',
        'category': ad_domain.ItemCategory.ELECTRONICS.value,
        'condition': ad_domain.ItemCondition.NEW.value,
        'status': ad_domain.ItemStatus.ACTIVE.value
    }

    create_response = authenticated_client.post(create_url, create_data, follow=True)
    assert create_response.status_code == 200
    assert b"Ad created successfully!" in create_response.content


    import re
    url_pattern = r'/ads/([a-f0-9-]+)/'
    match = re.search(url_pattern, create_response.redirect_chain[-1][0])
    ad_id = match.group(1)

    if not match:
        user_ads = ad_repo.find_user_ads(user.id)
        for ad in user_ads:
            if ad.title == 'Journey Test Ad':
                ad_id = ad.id
                break

    detail_url = reverse('ad_detail', args=[ad_id])
    detail_response = authenticated_client.get(detail_url)
    assert detail_response.status_code == 200
    assert b"Journey Test Ad" in detail_response.content


    update_url = reverse('ad_update', args=[ad_id])
    update_data = {
        'title': 'Updated Journey Ad',
        'description': 'This ad has been updated',
        'image_url': 'https://example.com/updated_journey.jpg',
        'category': ad_domain.ItemCategory.BOOKS.value,
        'condition': ad_domain.ItemCondition.USED.value,
        'status': ad_domain.ItemStatus.ACTIVE.value
    }

    update_response = authenticated_client.post(update_url, update_data, follow=True)
    assert update_response.status_code == 200
    assert b"Ad updated successfully!" in update_response.content
    assert b"Updated Journey Ad" in update_response.content

    delete_url = reverse('ad_delete', args=[ad_id])
    delete_response = authenticated_client.post(delete_url, follow=True)
    assert delete_response.status_code == 200
    assert b"Ad deleted successfully!" in delete_response.content

    detail_response = authenticated_client.get(detail_url)
    assert detail_response.status_code == 404
