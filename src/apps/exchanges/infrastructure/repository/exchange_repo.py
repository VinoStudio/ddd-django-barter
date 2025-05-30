from typing import List, Optional
from dataclasses import dataclass

from django.db.models import Q
from uuid6 import UUID
from src.apps.exchanges import domain
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
    def update_status(proposal: domain.Exchange) -> Optional[domain.Exchange]:
        proposal_model = ExchangeMapper.from_entity(proposal)

        #here we tell django that this model is not new
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
        user_ads = models.Ad.objects.filter(user_id=user_id).values_list('id', flat=True)

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



