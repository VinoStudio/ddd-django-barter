from dataclasses import dataclass
from src.core.domain.exceptions import AppError


@dataclass(frozen=True)
class ApplicationError(AppError):
    value: str

    @property
    def message(self):
        return "Application error occurred"


@dataclass(frozen=True)
class AuthenticationError(ApplicationError):
    pass


@dataclass(frozen=True)
class AuthorizationError(ApplicationError):
    pass


@dataclass(frozen=True)
class PermissionDeniedError(AuthenticationError):
    value: str

    @property
    def message(self) -> str:
        return self.value