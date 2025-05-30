from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, eq=False)
class ExchangeStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

    @classmethod
    def get_exchange_statuses(cls) -> set[str]:
        return {status.value for status in cls}

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ExchangeStatus):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)
