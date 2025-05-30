from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, eq=False)
class ItemCondition(Enum):
    NEW = "new"
    USED = "used"

    @classmethod
    def get_conditions(cls) -> list[str]:
        return [condition.value for condition in cls]

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ItemCondition):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)
