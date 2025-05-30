from dataclasses import dataclass
from uuid6 import UUID

from src.apps.ads.application.services.ad_service import AdService
from src.apps.ads.domain import ItemStatus
from src.apps.exchanges import domain
from src.apps.ads.domain.entity import Ad
from src.apps.exchanges.application.dto.exchange import CreateExchangeDTO, UpdateExchangeStatusDTO
from src.apps.exchanges.infrastructure.repository.exchange_repo import ExchangeRepository
from src.apps.ads.infrastructure.repository.ad_repo import AdRepository
from src.core.infrastructure.exceptions import NotFoundError
from src.core.application.exceptions import PermissionDeniedError

@dataclass
class ExchangeService:
    @staticmethod
    def create_proposal(proposal_data: CreateExchangeDTO) -> domain.Exchange:
        ad_sender: Ad = AdRepository.find_by_id(proposal_data.ad_sender_id)
        if not ad_sender:
            raise NotFoundError(f"Ad sender with ID {proposal_data.ad_sender_id} not found")

        ad_receiver: Ad = AdRepository.find_by_id(proposal_data.ad_receiver_id)
        if not ad_receiver:
            raise NotFoundError(f"Ad receiver with ID {proposal_data.ad_receiver_id} not found")

        if ad_receiver.status.value != 'active':
            raise PermissionDeniedError("Received add must be active")

        proposal = domain.Exchange(
            ad_sender_id=proposal_data.ad_sender_id,
            ad_receiver_id=proposal_data.ad_receiver_id,
            comment=proposal_data.comment,
        )

        return ExchangeRepository.create(proposal)

    @staticmethod
    def update_proposal_status(proposal_data: UpdateExchangeStatusDTO) -> domain.Exchange:
        proposal = ExchangeRepository.find_by_id(proposal_data.exchange_id)
        if not proposal:
            raise NotFoundError(f"An exchange proposal with ID {proposal_data.exchange_id} not found")

        ad_receiver = AdRepository.find_by_id(proposal.ad_receiver_id)
        if not ad_receiver:
            raise NotFoundError(f"Ad receiver with ID {proposal.ad_receiver_id} not found")

        if not ad_receiver.is_owner(proposal_data.user_id):
            raise PermissionDeniedError("Only the author of the ad receiver can update the proposal")

        status = proposal_data.status.value

        if status== 'accepted':
            proposal.accept()

            ad_service = AdService()
            ad_service.update_ad_status(proposal.ad_sender_id, ItemStatus.TRADED)
            ad_service.update_ad_status(proposal.ad_receiver_id, ItemStatus.TRADED)
        else:
            proposal.reject()

        return ExchangeRepository.update_status(proposal)

    @staticmethod
    def delete_exchange(exchange_id: UUID) -> bool:
        exchange = ExchangeRepository.find_by_id(exchange_id)
        if not exchange:
            raise NotFoundError(f"An exchange proposal with ID {exchange_id} not found")

        if exchange.status.value != 'pending':
            raise PermissionDeniedError("Only pending exchanges can be deleted")

        return ExchangeRepository.delete(exchange_id)

    @staticmethod
    def get_exchange(exchange_id: UUID) -> domain.Exchange:
        return ExchangeRepository.find_by_id(exchange_id)

    @staticmethod
    def get_user_proposals(user_id: UUID) -> list[domain.Exchange]:
        return ExchangeRepository.find_user_proposals(user_id)

    @staticmethod
    def get_proposals_by_sender_ad_id(ad_id: UUID) -> list[domain.Exchange]:
        return ExchangeRepository.find_by_sender_ad_id(ad_id)

    @staticmethod
    def get_proposals_by_receiver_ad_id(ad_id: UUID) -> list[domain.Exchange]:
        return ExchangeRepository.find_by_receiver_ad_id(ad_id)