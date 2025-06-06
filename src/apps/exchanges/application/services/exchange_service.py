from dataclasses import dataclass
from typing import Optional

from uuid6 import UUID

from src.apps.ads.application.dto.ad import AdDTO
from src.apps.ads.application.services.ad_service import AdService
from src.apps.ads.domain import ItemStatus
from src.apps.exchanges import domain
from src.apps.ads.domain.entity import Ad
from src.apps.exchanges.application.dto.exchange import (
    CreateExchangeDTO,
    UpdateExchangeStatusDTO,
    ExchangeDTO,
)
from src.apps.exchanges.infrastructure.repository.exchange_repo import (
    ExchangeRepository,
)
from src.apps.ads.infrastructure.repository.ad_repo import AdRepository
from src.core.infrastructure.exceptions import NotFoundError
from src.core.application.exceptions import PermissionDeniedError

"""
flex - 01974431-c8e4-72a7-a420-f5c4f7dffa0d
papa - 019744d3-6508-7ce0-b009-48ac432c896f
"""


@dataclass
class ExchangeService:
    @staticmethod
    def create_proposal(proposal_data: CreateExchangeDTO) -> ExchangeDTO:
        ad_sender: Ad = AdRepository.find_by_id(proposal_data.ad_sender_id)
        if not ad_sender:
            raise NotFoundError(
                f"Ad sender with ID {proposal_data.ad_sender_id} not found"
            )

        ad_receiver: Ad = AdRepository.find_by_id(proposal_data.ad_receiver_id)
        if not ad_receiver:
            raise NotFoundError(
                f"Ad receiver with ID {proposal_data.ad_receiver_id} not found"
            )

        if ad_receiver.status.value != "active":
            raise PermissionDeniedError("Received add must be active")

        proposal = domain.Exchange(
            ad_sender_id=proposal_data.ad_sender_id,
            ad_receiver_id=proposal_data.ad_receiver_id,
            comment=proposal_data.comment,
        )

        return ExchangeDTO.from_entity(ExchangeRepository.create(proposal))

    @staticmethod
    def update_proposal_status(proposal_data: UpdateExchangeStatusDTO) -> ExchangeDTO:
        proposal = ExchangeRepository.find_by_id(proposal_data.exchange_id)
        if not proposal:
            raise NotFoundError(
                f"An exchange proposal with ID {proposal_data.exchange_id} not found"
            )

        ad_receiver = AdRepository.find_by_id(proposal.ad_receiver_id)
        if not ad_receiver:
            raise NotFoundError(
                f"Ad receiver with ID {proposal.ad_receiver_id} not found"
            )

        if not ad_receiver.is_owner(proposal_data.user_id):
            raise PermissionDeniedError(
                "Only the author of the ad receiver can update the proposal"
            )

        status = proposal_data.status.value

        if status == "accepted":
            proposal.accept()

            ad_service = AdService()
            ad_service.update_ad_status(proposal.ad_sender_id, ItemStatus.TRADED)
            ad_service.update_ad_status(proposal.ad_receiver_id, ItemStatus.TRADED)
        else:
            proposal.reject()

        return ExchangeDTO.from_entity(ExchangeRepository.update_status(proposal))

    @staticmethod
    def delete_exchange(exchange_id: UUID, user_id: UUID) -> bool:
        exchange = ExchangeRepository.find_by_id(exchange_id)
        ad_sender = AdRepository.find_by_id(exchange.ad_sender_id)

        if not exchange:
            raise NotFoundError(f"An exchange proposal with ID {exchange_id} not found")

        if not ad_sender.is_owner(user_id):
            raise PermissionDeniedError(
                "You do not have permission to cancel this exchange"
            )

        if exchange.status.value != "pending":
            raise PermissionDeniedError("Only pending exchanges can be deleted")

        return ExchangeRepository.delete(exchange_id)

    @staticmethod
    def get_exchange(exchange_id: UUID) -> Optional[ExchangeDTO]:
        exchange = ExchangeRepository.find_by_id(exchange_id)
        if not exchange:
            raise NotFoundError(f"An exchange proposal with ID {exchange_id} not found")
        return ExchangeDTO.from_entity(exchange)

    @staticmethod
    def get_user_proposals(user_id: UUID) -> Optional[list[ExchangeDTO]]:
        exchanges = ExchangeRepository.find_user_proposals(user_id)
        if not exchanges:
            raise NotFoundError(
                f"An exchange proposal with user ID {user_id} not found"
            )
        return [ExchangeDTO.from_entity(exchange) for exchange in exchanges]

    @staticmethod
    def get_proposals_by_sender_ad_id(ad_id: UUID) -> Optional[list[ExchangeDTO]]:
        exchanges = ExchangeRepository.find_by_sender_ad_id(ad_id)
        if not exchanges:
            raise NotFoundError(f"An exchange proposal with ID {ad_id} not found")
        return [ExchangeDTO.from_entity(exchange) for exchange in exchanges]

    @staticmethod
    def get_proposals_by_receiver_ad_id(ad_id: UUID) -> Optional[list[ExchangeDTO]]:
        exchanges = ExchangeRepository.find_by_receiver_ad_id(ad_id)
        if not exchanges:
            raise NotFoundError(f"An exchange proposal with ID {ad_id} not found")
        return [ExchangeDTO.from_entity(exchange) for exchange in exchanges]

    @staticmethod
    def get_proposal_data(
        exchange_id: UUID = None, user_id: UUID = None
    ) -> Optional[ExchangeDTO]:
        exchange_dto = ExchangeRepository.get_proposal_data(exchange_id, user_id)
        if not exchange_dto:
            raise NotFoundError(f"An exchange proposal with ID {exchange_id} not found")
        return exchange_dto

    @staticmethod
    def get_all_user_proposals_data(user_id: UUID) -> Optional[list[ExchangeDTO]]:
        exchange_dtos = ExchangeRepository.get_all_user_proposals_data(user_id)
        if not exchange_dtos:
            raise NotFoundError(f"An exchange proposal with ID {user_id} not found")
        return exchange_dtos

    @staticmethod
    def get_exchange_participants(exchange: ExchangeDTO, user_id: UUID):
        sender_ad = AdRepository.find_by_id(exchange.ad_sender_id)
        receiver_ad = AdRepository.find_by_id(exchange.ad_receiver_id)

        if not sender_ad.is_owner(user_id) and not receiver_ad.is_owner(user_id):
            raise PermissionDeniedError(
                "You do not have permission to view this exchange"
            )

        return AdDTO.from_entity(sender_ad), AdDTO.from_entity(receiver_ad)
