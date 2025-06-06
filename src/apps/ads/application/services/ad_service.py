from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Optional, Iterable

from uuid6 import UUID

from src.apps.ads import domain
from src.apps.ads.infrastructure.repository.ad_repo import AdRepository
from src.apps.ads.infrastructure.database import models
from src.apps.ads.application.dto.ad import CreateAdDTO, UpdateAdDTO, AdFilterDTO, AdDTO
from src.core.infrastructure.exceptions import NotFoundError
from src.core.application.exceptions import PermissionDeniedError


@dataclass
class AdService:
    @staticmethod
    def create_ad(ad_dto: CreateAdDTO) -> AdDTO:
        ad = domain.Ad(
            user_id=ad_dto.user_id,
            title=ad_dto.title,
            description=ad_dto.description,
            image_url=ad_dto.image_url,
            category=domain.ItemCategory(ad_dto.category),
            condition=domain.ItemCondition(ad_dto.condition),
            status=domain.ItemStatus(ad_dto.status),
        )

        return AdDTO.from_entity(AdRepository.create(ad))

    @staticmethod
    def update_ad(ad_dto: UpdateAdDTO) -> AdDTO:
        existing_ad: domain.Ad = AdRepository.find_by_id(ad_dto.ad_id)
        if not existing_ad:
            raise NotFoundError(str(ad_dto.ad_id))

        if not existing_ad.is_owner(ad_dto.user_id):
            raise PermissionDeniedError("Only the author of the ad can update it")

        updated_ad = domain.Ad(
            id=existing_ad.id,
            user_id=existing_ad.user_id,
            title=ad_dto.title or existing_ad.title,
            owner_username=existing_ad.owner_username,
            description=ad_dto.description or existing_ad.description,
            image_url=ad_dto.image_url or existing_ad.image_url,
            category=domain.ItemCategory(ad_dto.category or existing_ad.category),
            condition=domain.ItemCondition(ad_dto.condition or existing_ad.condition),
            created_at=existing_ad.created_at,
            updated_at=datetime.now(UTC),
        )

        return AdDTO.from_entity(AdRepository.update(updated_ad))

    @staticmethod
    def update_ad_status(ad_id: UUID, status: domain.ItemStatus) -> AdDTO:
        existing_ad: domain.Ad = AdRepository.find_by_id(ad_id)
        if not existing_ad:
            raise NotFoundError(str(ad_id))

        existing_ad.status = status

        return AdDTO.from_entity(AdRepository.update(existing_ad))

    @staticmethod
    def delete_ad(ad_id: UUID, user_id: UUID) -> bool:
        existing_ad = AdRepository.find_by_id(ad_id)
        if not existing_ad:
            raise NotFoundError(f"Ad with ID {ad_id} not found")

        if not existing_ad.is_owner(user_id):
            raise PermissionDeniedError("Only the author of the ad can update it")

        return AdRepository.delete(ad_id)

    @staticmethod
    def get_ad(ad_id: UUID) -> Optional[AdDTO]:
        ad = AdRepository.find_by_id(ad_id)
        if not ad:
            raise NotFoundError(f"Ad with ID {ad_id} not found")
        return AdDTO.from_entity(ad)

    @staticmethod
    def get_user_ads(user_id: UUID) -> list[AdDTO]:
        user_ads = AdRepository.find_user_ads(user_id=user_id)
        if not user_ads:
            raise NotFoundError(f"Ads with user ID {user_id} not found")
        return [AdDTO.from_entity(ad) for ad in user_ads]

    @staticmethod
    def list_ads(filter: AdFilterDTO) -> dict:
        ads_query: Iterable[models.Ad] = AdRepository.search(
            category=filter.category,
            condition=filter.condition,
            status=filter.status,
            keyword=filter.keyword,
            user_id=filter.user_id,
        )

        start = (filter.page - 1) * filter.page_size
        end = start + filter.page_size

        paginated_ads = ads_query[start:end]

        total_items = ads_query.count()
        total_pages = (total_items + filter.page_size - 1) // filter.page_size

        ads = [
            AdDTO(
                id=ad.id,
                user_id=ad.user.id,
                username=ad.user.username,
                title=ad.title,
                description=ad.description,
                image_url=ad.image_url,
                status=ad.status,
                category=ad.category,
                condition=ad.condition,
                created_at=ad.created_at,
            )
            for ad in paginated_ads
        ]

        return {
            "ads": ads,
            "page_size": filter.page_size,
            "total_items": total_items,
            "total_pages": total_pages,
        }
