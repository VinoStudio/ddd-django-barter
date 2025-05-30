from dataclasses import dataclass, field
from typing import Optional
from uuid6 import UUID

from src.apps.ads.domain.values.category import ItemCategory
from src.apps.ads.domain.values.condition import ItemCondition
from src.apps.ads.domain.values.status import ItemStatus
from src.core.domain.entity import BaseEntity


@dataclass(eq=False)
class Ad(BaseEntity):
    user_id: UUID
    title: str
    description: str
    owner_username: Optional[str] = field(default=None)
    category: ItemCategory = field(default=ItemCategory.OTHER)
    status: ItemStatus = field(default=ItemStatus.ACTIVE)
    condition: ItemCondition = field(default=ItemCondition.USED)
    image_url: Optional[str] = field(default=None)

    def is_owner(self, user_id: UUID) -> bool:
        return self.user_id == user_id

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'owner_username': self.owner_username,
            'title': self.title,
            'description': self.description,
            'image_url': self.image_url,
            'category': str(self.category),
            'condition': str(self.condition),
            'status': str(self.status),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }