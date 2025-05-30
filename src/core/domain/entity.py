from abc import ABC
from dataclasses import dataclass, field
from datetime import UTC, datetime

from uuid6 import uuid7, UUID


@dataclass
class BaseEntity(ABC):
    id: UUID = field(default_factory=lambda: uuid7(), kw_only=True)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
        kw_only=True,
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(UTC), kw_only=True
    )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)