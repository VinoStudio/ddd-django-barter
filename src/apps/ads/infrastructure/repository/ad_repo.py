from typing import List, Optional
from logging import getLogger
from uuid6 import UUID
from dataclasses import dataclass
from django.db.models import Q
from src.apps.ads.domain.entity import Ad
from src.apps.ads import domain
from src.apps.ads.infrastructure.database import models
from src.apps.ads.infrastructure.repository.mapper import AdMapper
from src.core.infrastructure.exceptions import NotFoundError


@dataclass
class AdRepository:
    @staticmethod
    def create(ad: domain.Ad) -> domain.Ad:
        ad_model: models.Ad = AdMapper.from_entity(ad)
        ad_model.save()
        return AdRepository.find_by_id(ad.id)

    @staticmethod
    def update(ad: domain.Ad) -> domain.Ad:
        updated_model: models.Ad = AdMapper.from_entity(ad)

        #here we tell django that this model is not new
        updated_model._state.adding = False
        updated_model.save()
        return AdRepository.find_by_id(ad.id)

    @staticmethod
    def delete(ad_id: UUID) -> bool:
        try:
            ad_model = models.Ad.objects.get(id=ad_id)
            ad_model.delete()
            return True
        except models.Ad.DoesNotExist:
            raise NotFoundError(f"Ad with ID {ad_id} not found")

    @staticmethod
    def find_by_id(ad_id: UUID) -> Optional[domain.Ad]:
        try:
            ad_model = models.Ad.objects.get(id=ad_id)
            return AdMapper.to_entity(ad_model)
        except models.Ad.DoesNotExist:
            return None

    @staticmethod
    def find_user_ads(user_id: UUID) -> List[domain.Ad]:
        ad_models = models.Ad.objects.filter(user_id=user_id)
        return [AdMapper.to_entity(model) for model in ad_models]

    @staticmethod
    def search(
        keyword: str,
        category: str,
        status: str,
        condition: str,
        page: int = 1,
        page_size: int = 10
    )-> List[Ad]:
        queryset = models.Ad.objects.all()

        if keyword:
            queryset = queryset.filter(Q(title__icontains=keyword) |
                                       Q(description__icontains=keyword))
        if category:
            queryset = queryset.filter(category=category)

        if condition:
            queryset = queryset.filter(condition=condition)

        if status:
            queryset = queryset.filter(status=status)

        start = (page - 1) * page_size
        end = start + page_size

        ad_models = queryset[start:end]
        return [AdMapper.to_entity(model) for model in ad_models]