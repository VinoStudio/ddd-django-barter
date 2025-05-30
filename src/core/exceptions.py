from dataclasses import dataclass
from abc import ABC

@dataclass(frozen=True)
class AppError(Exception, ABC):
    value: str

    @property
    def message(self):
        return "Application error occurred"