from typing import List, Optional
from dataclasses import dataclass

from django.db.models import Q
from uuid6 import UUID
from src.apps.exchanges import domain
from src.apps.exchanges.application.dto.exchange import ExchangeDTO
from src.apps.exchanges.infrastructure.database import models
from src.apps.exchanges.infrastructure.repository.mapper import ExchangeMapper


@dataclass
class ExchangeRepository:
    @staticmethod
    def create(exchange: domain.Exchange) -> domain.Exchange:
        proposal_model = ExchangeMapper.from_entity(exchange)
        proposal_model.save()
        return exchange

    @staticmethod
    def update_status(proposal: domain.Exchange) -> domain.Exchange:
        proposal_model = ExchangeMapper.from_entity(proposal)

        # here we tell django that this model is not new
        proposal_model._state.adding = False
        proposal_model.save()
        return ExchangeRepository.find_by_id(proposal.id)

    @staticmethod
    def delete(exchange_id: UUID) -> bool:
        try:
            exchange_model = models.Exchange.objects.get(id=exchange_id)
            exchange_model.delete()
            return True
        except models.Exchange.DoesNotExist:
            return False

    @staticmethod
    def find_by_id(exchange_id: UUID) -> Optional[domain.Exchange]:
        try:
            ad_model = models.Exchange.objects.get(id=exchange_id)
            return ExchangeMapper.to_entity(ad_model)
        except models.Exchange.DoesNotExist:
            return None

    @staticmethod
    def find_user_proposals(user_id: UUID) -> list[domain.Exchange]:
        user_ads = models.Ad.objects.filter(user_id=user_id).values_list(
            "id", flat=True
        )

        proposal_models = models.Exchange.objects.filter(
            Q(ad_sender_id__in=user_ads) | Q(ad_receiver_id__in=user_ads)
        )

        return [ExchangeMapper.to_entity(model) for model in proposal_models]

    @staticmethod
    def find_by_sender_ad_id(ad_id: UUID) -> list[domain.Exchange]:
        proposal_models = models.Exchange.objects.filter(ad_sender_id=ad_id)
        return [ExchangeMapper.to_entity(model) for model in proposal_models]

    @staticmethod
    def find_by_receiver_ad_id(ad_id: UUID) -> list[domain.Exchange]:
        proposal_models = models.Exchange.objects.filter(ad_receiver_id=ad_id)
        return [ExchangeMapper.to_entity(model) for model in proposal_models]

    @staticmethod
    def get_proposal_data(
        exchange_id: UUID = None, user_id: UUID = None
    ) -> Optional[ExchangeDTO]:
        if exchange_id is None and user_id is None:
            return None

        filter_condition = (
            Q(id=exchange_id)
            if exchange_id is not None
            else Q(ad_sender__user_id=user_id)
        )

        exchange = (
            models.Exchange.objects.filter(filter_condition)
            .select_related(
                "ad_sender", "ad_receiver", "ad_sender__user", "ad_receiver__user"
            )
            .first()
        )

        if not exchange:
            return None

        return ExchangeDTO(
            id=exchange.id,
            ad_sender_id=exchange.ad_sender.id,
            ad_receiver_id=exchange.ad_receiver.id,
            comment=exchange.comment,
            status=exchange.status.value,
            created_at=exchange.created_at,
            sender_username=exchange.ad_sender.user.username,
            receiver_username=exchange.ad_receiver.user.username,
            sender_item=exchange.ad_sender.title,
            receiver_item=exchange.ad_receiver.title,
        )

    @staticmethod
    def get_all_user_proposals_data(user_id: UUID) -> list[ExchangeDTO]:
        exchanges = (
            models.Exchange.objects.filter(
                Q(ad_sender__user_id=user_id) | Q(ad_receiver__user_id=user_id)
            )
            .select_related(
                "ad_sender", "ad_receiver", "ad_sender__user", "ad_receiver__user"
            )
            .all()
        )

        return [
            ExchangeDTO(
                id=exchange.id,
                ad_sender_id=exchange.ad_sender.id,
                ad_receiver_id=exchange.ad_receiver.id,
                comment=exchange.comment,
                status=exchange.status,
                created_at=exchange.created_at,
                sender_username=exchange.ad_sender.user.username,
                receiver_username=exchange.ad_receiver.user.username,
                sender_item=exchange.ad_sender.title,
                receiver_item=exchange.ad_receiver.title,
            )
            for exchange in exchanges
        ]

    @staticmethod
    def get_exchanges() -> list[ExchangeDTO]:
        exchanges = models.Exchange.objects.all().select_related(
            "ad_sender", "ad_receiver", "ad_sender__user", "ad_receiver__user"
        )

        return [
            ExchangeDTO(
                id=exchange.id,
                ad_sender_id=exchange.ad_sender.id,
                ad_receiver_id=exchange.ad_receiver.id,
                comment=exchange.comment,
                status=exchange.status.value,
                created_at=exchange.created_at,
                sender_username=exchange.ad_sender.user.username,
                receiver_username=exchange.ad_receiver.user.username,
                sender_item=exchange.ad_sender.title,
                receiver_item=exchange.ad_receiver.title,
            )
            for exchange in exchanges
        ]
