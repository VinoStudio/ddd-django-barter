import pytest
from uuid6 import UUID
from src.apps.exchanges import domain as exchange_domain


def test_exchange_domain_creation():
    exchange = exchange_domain.Exchange(
        ad_sender_id=UUID('00000000-0000-0000-0000-000000000001'),
        ad_receiver_id=UUID('00000000-0000-0000-0000-000000000002'),
        comment="Test exchange comment"
    )

    assert exchange.ad_sender_id == UUID('00000000-0000-0000-0000-000000000001')
    assert exchange.ad_receiver_id == UUID('00000000-0000-0000-0000-000000000002')
    assert exchange.comment == "Test exchange comment"
    assert exchange.status == exchange_domain.ExchangeStatus.PENDING


def test_exchange_domain_methods():
    sender_id = UUID('00000000-0000-0000-0000-000000000001')
    receiver_id = UUID('00000000-0000-0000-0000-000000000002')
    other_id = UUID('00000000-0000-0000-0000-000000000003')

    exchange = exchange_domain.Exchange(
        ad_sender_id=sender_id,
        ad_receiver_id=receiver_id,
        comment="Testing methods"
    )

    assert exchange.is_sender(sender_id) is True
    assert exchange.is_sender(receiver_id) is False
    assert exchange.is_sender(other_id) is False

    assert exchange.is_receiver(receiver_id) is True
    assert exchange.is_receiver(sender_id) is False
    assert exchange.is_receiver(other_id) is False

    assert exchange.status == exchange_domain.ExchangeStatus.PENDING

    exchange.accept()
    assert exchange.status == exchange_domain.ExchangeStatus.ACCEPTED

    exchange2 = exchange_domain.Exchange(
        ad_sender_id=sender_id,
        ad_receiver_id=receiver_id,
        comment="Testing reject"
    )

    exchange2.reject()
    assert exchange2.status == exchange_domain.ExchangeStatus.REJECTED


def test_exchange_status_enum():
    pending = exchange_domain.ExchangeStatus("pending")
    accepted = exchange_domain.ExchangeStatus("accepted")
    rejected = exchange_domain.ExchangeStatus("rejected")

    assert pending == exchange_domain.ExchangeStatus.PENDING
    assert accepted ==exchange_domain. ExchangeStatus.ACCEPTED
    assert rejected == exchange_domain.ExchangeStatus.REJECTED

    with pytest.raises(ValueError):
        exchange_domain.ExchangeStatus("invalid_status")


def test_exchange_domain_equality():
    exchange1 = exchange_domain.Exchange(
        id=UUID('00000000-0000-0000-0000-000000000001'),
        ad_sender_id=UUID('00000000-0000-0000-0000-000000000002'),
        ad_receiver_id=UUID('00000000-0000-0000-0000-000000000003'),
        comment="Test comment",
        status=exchange_domain.ExchangeStatus.PENDING
    )

    exchange2 = exchange_domain.Exchange(
        id=UUID('00000000-0000-0000-0000-000000000001'),
        ad_sender_id=UUID('00000000-0000-0000-0000-000000000002'),
        ad_receiver_id=UUID('00000000-0000-0000-0000-000000000003'),
        comment="Different comment",
        status=exchange_domain.ExchangeStatus.ACCEPTED
    )

    exchange3 = exchange_domain.Exchange(
        id=UUID('00000000-0000-0000-0000-000000000004'),
        ad_sender_id=UUID('00000000-0000-0000-0000-000000000002'),
        ad_receiver_id=UUID('00000000-0000-0000-0000-000000000003'),
        comment="Test comment",
        status=exchange_domain.ExchangeStatus.PENDING
    )

    assert exchange1 == exchange2
    assert exchange1 != exchange3
def test_exchange_domain_validation():
    valid_exchange = exchange_domain.Exchange(
        ad_sender_id=UUID('00000000-0000-0000-0000-000000000001'),
        ad_receiver_id=UUID('00000000-0000-0000-0000-000000000002'),
        comment="Valid comment",
        status=exchange_domain.ExchangeStatus.PENDING
    )

    assert valid_exchange.ad_sender_id == UUID('00000000-0000-0000-0000-000000000001')

    with pytest.raises(ValueError):
        invalid_exchange = exchange_domain.Exchange(
            ad_sender_id=UUID('00000000-0000-0000-0000-000000000001'),
            ad_receiver_id=UUID('00000000-0000-0000-0000-000000000002'),
            comment="Valid comment",
            status=exchange_domain.ExchangeStatus("INVALID_STATUS")
        )


def test_exchange_domain_immutability():
    """Test that changing an exchange's attributes doesn't affect others with the same ID"""
    # Create original exchange
    original_exchange = exchange_domain.Exchange(
        id=UUID('00000000-0000-0000-0000-000000000001'),
        ad_sender_id=UUID('00000000-0000-0000-0000-000000000002'),
        ad_receiver_id=UUID('00000000-0000-0000-0000-000000000003'),
        comment="Original comment",
        status=exchange_domain.ExchangeStatus.PENDING
    )

    # Create a copy with the same ID but different attributes
    modified_exchange = exchange_domain.Exchange(
        id=UUID('00000000-0000-0000-0000-000000000001'),
        ad_sender_id=UUID('00000000-0000-0000-0000-000000000002'),
        ad_receiver_id=UUID('00000000-0000-0000-0000-000000000003'),
        comment="Modified comment",
        status=exchange_domain.ExchangeStatus.ACCEPTED
    )

    # Verify that changing attributes doesn't affect the original
    assert original_exchange.id == modified_exchange.id  # IDs are equal
    assert original_exchange.comment == "Original comment"  # Original comment unchanged
    assert modified_exchange.comment == "Modified comment"  # Modified comment is different
    assert original_exchange.status == exchange_domain.ExchangeStatus.PENDING
    assert modified_exchange.status == exchange_domain.ExchangeStatus.ACCEPTED

    # Changing status on one doesn't affect the other
    original_exchange.reject()
    assert original_exchange.status == exchange_domain.ExchangeStatus.REJECTED
    assert modified_exchange.status == exchange_domain.ExchangeStatus.ACCEPTED  # Remains unchanged