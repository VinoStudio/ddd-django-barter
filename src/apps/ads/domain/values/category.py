from enum import Enum
from dataclasses import dataclass


@dataclass(frozen=True, eq=False)
class ItemCategory(Enum):
    ELECTRONICS = "electronics"
    CLOTHES = "clothes"
    TOYS = "toys"
    BOOKS = "books"
    GAMES = "games"
    CARS = "cars"
    HOME = "home"
    OTHER = "other"

    @classmethod
    def get_categories(cls) -> list[str]:
        return [category.value for category in cls]

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ItemCategory):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)