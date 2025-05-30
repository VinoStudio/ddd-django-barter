from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, eq=False)
class ItemStatus(Enum):
    ACTIVE = "active"
    TRADED = "traded"
    ARCHIVED = "archived"

    @classmethod
    def get_statuses(cls) -> list[str]:
        return [status.value for status in cls]

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ItemStatus):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)
