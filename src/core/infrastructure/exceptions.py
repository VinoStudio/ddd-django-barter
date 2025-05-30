from src.core.domain.exceptions import AppError
from dataclasses import dataclass


@dataclass(frozen=True)
class RepositoryError(AppError):
    pass


@dataclass(frozen=True)
class NotFoundError(RepositoryError):
    value: str

    @property
    def message(self) -> str:
        return self.value