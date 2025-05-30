from uuid6 import UUID
import pytest

from src.apps.ads import domain as ad_domain
from src.apps.exchanges import domain as exchange_domain
from src.apps.exchanges.application.dto.exchange import CreateExchangeDTO, UpdateExchangeStatusDTO
from src.core.application.exceptions import PermissionDeniedError

from src.core.infrastructure.database.models import User
from src.core.infrastructure.exceptions import NotFoundError


def test_create_exchange_proposal(user, receiver_user, ad_service, ad_repo, exchange_service):
    # Create two ads to exchange
    sender_ad = ad_domain.Ad(
        user_id=user.id,
        title="Sender Ad",
        owner_username=user.username,
        description="Item to exchange",
        image_url="https://example.com/sender.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    receiver_ad = ad_domain.Ad(
        user_id=receiver_user.id,
        title="Receiver Ad",
        owner_username=receiver_user.username,
        description="Item wanted",
        image_url="https://example.com/receiver.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    saved_sender_ad = ad_repo.create(sender_ad)
    saved_receiver_ad = ad_repo.create(receiver_ad)

    # Create exchange proposal
    proposal_dto = CreateExchangeDTO(
        user_id=user.id,
        ad_sender_id=saved_sender_ad.id,
        ad_receiver_id=saved_receiver_ad.id,
        comment="Interested in exchanging"
    )

    exchange = exchange_service.create_proposal(proposal_dto)

    assert exchange is not None
    assert exchange.ad_sender_id == saved_sender_ad.id
    assert exchange.ad_receiver_id == saved_receiver_ad.id
    assert exchange.comment == "Interested in exchanging"
    assert exchange.status == exchange_domain.ExchangeStatus.PENDING


def test_create_exchange_invalid_ad(user, ad_service, ad_repo, exchange_service):
    # Create a valid ad
    valid_ad = ad_domain.Ad(
        user_id=user.id,
        title="Valid Ad",
        owner_username=user.username,
        description="Valid item",
        image_url="https://example.com/valid.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )
    saved_valid_ad = ad_repo.create(valid_ad)

    # Create a proposal with non-existent receiver ad
    non_existent_id = UUID('00000000-0000-0000-0000-000000000999')
    proposal_dto = CreateExchangeDTO(
        user_id=user.id,
        ad_sender_id=saved_valid_ad.id,
        ad_receiver_id=non_existent_id,
        comment="This should fail"
    )

    with pytest.raises(NotFoundError):
        exchange_service.create_proposal(proposal_dto)


def test_update_proposal_status_accept(receiver_user, sender_user, ad_service, ad_repo, exchange_service, exchange_repo):
    # Create two users and their ads

    sender_ad = ad_domain.Ad(
        user_id=sender_user.id,
        title="Sender Ad",
        owner_username=sender_user.username,
        description="Offering item",
        image_url="https://example.com/sender.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    receiver_ad = ad_domain.Ad(
        user_id=receiver_user.id,
        title="Receiver Ad",
        owner_username=receiver_user.username,
        description="Wanted item",
        image_url="https://example.com/receiver.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    saved_sender_ad = ad_repo.create(sender_ad)
    saved_receiver_ad = ad_repo.create(receiver_ad)

    # Create exchange proposal
    exchange = exchange_domain.Exchange(
        ad_sender_id=saved_sender_ad.id,
        ad_receiver_id=saved_receiver_ad.id,
        comment="Exchange proposal"
    )
    saved_exchange = exchange_repo.create(exchange)

    # Accept the proposal
    update_dto = UpdateExchangeStatusDTO(
        exchange_id=saved_exchange.id,
        user_id=receiver_user.id,
        status=exchange_domain.ExchangeStatus.ACCEPTED
    )

    updated_exchange = exchange_service.update_proposal_status(update_dto)

    assert updated_exchange.status == exchange_domain.ExchangeStatus.ACCEPTED

    # Check that both ads are now marked as traded
    updated_sender_ad = ad_repo.find_by_id(saved_sender_ad.id)
    updated_receiver_ad = ad_repo.find_by_id(saved_receiver_ad.id)

    assert updated_sender_ad.status == ad_domain.ItemStatus.TRADED
    assert updated_receiver_ad.status == ad_domain.ItemStatus.TRADED


def test_update_proposal_status_reject(receiver_user,sender_user, ad_service, ad_repo, exchange_service, exchange_repo):

    sender_ad = ad_domain.Ad(
        user_id=sender_user.id,
        title="Sender Ad 2",
        owner_username=sender_user.username,
        description="Offering item 2",
        image_url="https://example.com/sender2.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    receiver_ad = ad_domain.Ad(
        user_id=receiver_user.id,
        title="Receiver Ad 2",
        owner_username=receiver_user.username,
        description="Wanted item 2",
        image_url="https://example.com/receiver2.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    saved_sender_ad = ad_repo.create(sender_ad)
    saved_receiver_ad = ad_repo.create(receiver_ad)

    # Create exchange proposal
    exchange = exchange_domain.Exchange(
        ad_sender_id=saved_sender_ad.id,
        ad_receiver_id=saved_receiver_ad.id,
        comment="Exchange proposal 2"
    )
    saved_exchange = exchange_repo.create(exchange)

    # Reject the proposal
    update_dto = UpdateExchangeStatusDTO(
        exchange_id=saved_exchange.id,
        user_id=receiver_user.id,
        status=exchange_domain.ExchangeStatus.REJECTED
    )

    updated_exchange = exchange_service.update_proposal_status(update_dto)

    assert updated_exchange.status == exchange_domain.ExchangeStatus.REJECTED

    # Check that ads remain active
    updated_sender_ad = ad_repo.find_by_id(saved_sender_ad.id)
    updated_receiver_ad = ad_repo.find_by_id(saved_receiver_ad.id)

    assert updated_sender_ad.status == ad_domain.ItemStatus.ACTIVE
    assert updated_receiver_ad.status == ad_domain.ItemStatus.ACTIVE


def test_update_proposal_permission_denied(receiver_user, sender_user, exchange_service, exchange_repo, ad_repo):
    # Third user who shouldn't have permission
    third_user = User.objects.create_user(
        username='third',
        email='third@example.com',
        password='password123'
    )

    # Create ads for the exchange
    sender_ad = ad_domain.Ad(
        user_id=sender_user.id,
        title="Sender Ad 3",
        owner_username=sender_user.username,
        description="Offering item 3",
        image_url="https://example.com/sender3.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    receiver_ad = ad_domain.Ad(
        user_id=receiver_user.id,
        title="Receiver Ad 3",
        owner_username=receiver_user.username,
        description="Wanted item 3",
        image_url="https://example.com/receiver3.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    saved_sender_ad = ad_repo.create(sender_ad)
    saved_receiver_ad = ad_repo.create(receiver_ad)

    # Create exchange proposal
    exchange = exchange_domain.Exchange(
        ad_sender_id=saved_sender_ad.id,
        ad_receiver_id=saved_receiver_ad.id,
        comment="Exchange proposal 3"
    )
    saved_exchange = exchange_repo.create(exchange)

    # Third user attempts to update the proposal
    update_dto = UpdateExchangeStatusDTO(
        exchange_id=saved_exchange.id,
        user_id=third_user.id,
        status=exchange_domain.ExchangeStatus.ACCEPTED
    )

    with pytest.raises(PermissionDeniedError):
        exchange_service.update_proposal_status(update_dto)


def test_delete_exchange(exchange_service, exchange_repo, ad_repo, user):
    # Create ads for the exchange
    sender_ad = ad_domain.Ad(
        user_id=user.id,
        title="Sender Ad for Delete",
        owner_username=user.username,
        description="Item to delete",
        image_url="https://example.com/delete.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    receiver_user = User.objects.create_user(
        username='receiver_delete',
        email='receiver_delete@example.com',
        password='password123'
    )

    receiver_ad = ad_domain.Ad(
        user_id=receiver_user.id,
        title="Receiver Ad for Delete",
        owner_username=receiver_user.username,
        description="Wanted item for delete",
        image_url="https://example.com/delete_receiver.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    saved_sender_ad = ad_repo.create(sender_ad)
    saved_receiver_ad = ad_repo.create(receiver_ad)

    # Create exchange proposal
    exchange = exchange_domain.Exchange(
        ad_sender_id=saved_sender_ad.id,
        ad_receiver_id=saved_receiver_ad.id,
        comment="Exchange to delete"
    )
    saved_exchange = exchange_repo.create(exchange)

    # Delete the exchange
    exchange_service.delete_exchange(saved_exchange.id)

    # Verify it's gone
    deleted_exchange = exchange_repo.find_by_id(saved_exchange.id)
    assert deleted_exchange is None


def test_delete_non_pending_exchange(exchange_service, exchange_repo, ad_repo, user, receiver_user):
    # Create ads for the exchange
    sender_ad = ad_domain.Ad(
        user_id=user.id,
        title="Sender Ad Non-pending",
        owner_username=user.username,
        description="Item for non-pending test",
        image_url="https://example.com/non_pending.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    receiver_ad = ad_domain.Ad(
        user_id=receiver_user.id,
        title="Receiver Ad Non-pending",
        owner_username=receiver_user.username,
        description="Wanted item for non-pending test",
        image_url="https://example.com/non_pending_receiver.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    saved_sender_ad = ad_repo.create(sender_ad)
    saved_receiver_ad = ad_repo.create(receiver_ad)

    # Create exchange proposal that is already accepted
    exchange = exchange_domain.Exchange(
        ad_sender_id=saved_sender_ad.id,
        ad_receiver_id=saved_receiver_ad.id,
        comment="Non-pending exchange",
        status=exchange_domain.ExchangeStatus.ACCEPTED
    )
    saved_exchange = exchange_repo.create(exchange)

    # Attempt to delete the non-pending exchange should fail
    with pytest.raises(PermissionDeniedError):
        exchange_service.delete_exchange(saved_exchange.id)


def test_get_user_proposals(exchange_service, exchange_repo, ad_repo):

    first_user = User.objects.create_user(
        username='first_user',
        email='first@example.com',
        password='password123'
    )

    # Create a second user
    second_user = User.objects.create_user(
        username='second_user',
        email='second@example.com',
        password='password123'
    )

    # Create ads for both users
    user_ad = ad_domain.Ad(
        user_id=first_user.id,
        title="User Ad",
        owner_username=first_user.username,
        description="User's item",
        image_url="https://example.com/user_ad.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    second_user_ad = ad_domain.Ad(
        user_id=second_user.id,
        title="Second User Ad",
        owner_username=second_user.username,
        description="Second user's item",
        image_url="https://example.com/second_user.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    saved_user_ad = ad_repo.create(user_ad)
    saved_second_user_ad = ad_repo.create(second_user_ad)

    # Create exchanges in both directions
    user_is_sender = exchange_domain.Exchange(
        ad_sender_id=saved_user_ad.id,
        ad_receiver_id=saved_second_user_ad.id,
        comment="User is sender"
    )

    user_is_receiver = exchange_domain.Exchange(
        ad_sender_id=saved_second_user_ad.id,
        ad_receiver_id=saved_user_ad.id,
        comment="User is receiver"
    )

    exchange_repo.create(user_is_sender)
    exchange_repo.create(user_is_receiver)

    # Get user proposals
    user_proposals = exchange_service.get_user_proposals(first_user.id)

    # User should see both proposals
    assert len(user_proposals) == 2

    # Check proposal details
    sender_comments = [p.comment for p in user_proposals]
    assert "User is sender" in sender_comments
    assert "User is receiver" in sender_comments


def test_get_proposals_by_ad_id(user, exchange_service, exchange_repo, ad_repo):
    # Create multiple ads
    ad1 = ad_domain.Ad(
        user_id=user.id,
        title="Ad One",
        owner_username=user.username,
        description="First ad",
        image_url="https://example.com/ad1.jpg",
        category=ad_domain.ItemCategory.ELECTRONICS,
        condition=ad_domain.ItemCondition.NEW,
        status=ad_domain.ItemStatus.ACTIVE
    )

    ad2 = ad_domain.Ad(
        user_id=user.id,
        title="Ad Two",
        owner_username=user.username,
        description="Second ad",
        image_url="https://example.com/ad2.jpg",
        category=ad_domain.ItemCategory.BOOKS,
        condition=ad_domain.ItemCondition.USED,
        status=ad_domain.ItemStatus.ACTIVE
    )

    saved_ad1 = ad_repo.create(ad1)
    saved_ad2 = ad_repo.create(ad2)

    # Create multiple exchanges with these ads
    exchange1 = exchange_domain.Exchange(
        ad_sender_id=saved_ad1.id,
        ad_receiver_id=saved_ad2.id,
        comment="Exchange 1 to 2"
    )

    exchange2 = exchange_domain.Exchange(
        ad_sender_id=saved_ad2.id,
        ad_receiver_id=saved_ad1.id,
        comment="Exchange 2 to 1"
    )

    exchange_repo.create(exchange1)
    exchange_repo.create(exchange2)

    # Test finding by sender ad id
    sender_proposals = exchange_service.get_proposals_by_sender_ad_id(saved_ad1.id)
    assert len(sender_proposals) == 1
    assert sender_proposals[0].comment == "Exchange 1 to 2"

    # Test finding by receiver ad id
    receiver_proposals = exchange_service.get_proposals_by_receiver_ad_id(saved_ad1.id)
    assert len(receiver_proposals) == 1
    assert receiver_proposals[0].comment == "Exchange 2 to 1"