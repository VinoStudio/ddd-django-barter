from dataclasses import dataclass
from src.core.exceptions import AppError


@dataclass(frozen=True)
class DomainError(AppError):
    @property
    def message(self):
        return "Domain error occurred"
