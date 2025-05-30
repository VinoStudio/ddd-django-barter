from src.apps.exchanges import domain
from src.apps.exchanges.infrastructure.database import models

class ExchangeMapper:
    @staticmethod
    def to_entity(instance: models.Exchange) -> domain.Exchange:
        return domain.Exchange(
            id=instance.id,
            ad_sender_id=instance.ad_sender.id,
            ad_receiver_id=instance.ad_receiver.id,
            comment=instance.comment,
            created_at=instance.created_at,
            status=domain.ExchangeStatus(instance.status)
        )

    @staticmethod
    def from_entity(entity: domain.Exchange) -> models.Exchange:
        return models.Exchange(
            id=entity.id,
            ad_sender_id=entity.ad_sender_id,
            ad_receiver_id=entity.ad_receiver_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            comment=entity.comment,
            status=entity.status.value
        )
