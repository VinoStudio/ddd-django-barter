from src.apps.ads import domain
from src.apps.ads.infrastructure.database import models

class AdMapper:
    @staticmethod
    def to_entity(instance: models.Ad) -> domain.Ad:
        return domain.Ad(
            id=instance.id,
            user_id=instance.user.id,
            owner_username=instance.user.username,
            title=instance.title,
            description=instance.description,
            image_url=instance.image_url,
            category=domain.ItemCategory(instance.category),
            condition=domain.ItemCondition(instance.condition),
            status=domain.ItemStatus(instance.status),
            created_at=instance.created_at,
            updated_at=instance.updated_at
        )

    @staticmethod
    def from_entity(instance: domain.Ad) -> models.Ad:
        return models.Ad(
            id=instance.id,
            user_id=instance.user_id,
            title=instance.title,
            description=instance.description,
            image_url=instance.image_url,
            category=str(instance.category),
            condition=str(instance.condition),
            status=str(instance.status),
            created_at=instance.created_at,
            updated_at=instance.updated_at,
        )
