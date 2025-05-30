from dataclasses import dataclass, field
from typing import Optional
from uuid6 import UUID

from src.apps.exchanges.domain.values.status import ExchangeStatus
from src.core.domain.entity import BaseEntity


@dataclass(eq=False)
class Exchange(BaseEntity):
    ad_sender_id: UUID
    ad_receiver_id: UUID
    comment: Optional[str] = field(default=None)
    status: ExchangeStatus = field(default=ExchangeStatus.PENDING)

    def is_sender(self, user_id: UUID) -> bool:
        return self.ad_sender_id == user_id

    def is_receiver(self, user_id: UUID) -> bool:
        return self.ad_receiver_id == user_id

    def accept(self) -> None:
        self.status = ExchangeStatus.ACCEPTED

    def reject(self) -> None:
        self.status = ExchangeStatus.REJECTED

    def to_dict(self):
        return {
            "id": self.id,
            "ad_sender_id": self.ad_sender_id,
            "ad_receiver_id": self.ad_receiver_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "comment": self.comment,
            "status": str(self.status),
        }