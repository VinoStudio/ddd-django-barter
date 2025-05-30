from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any

@dataclass(frozen=True)
class DTO(ABC):

    @abstractmethod
    def from_request(self, *args, **kwargs):
        raise NotImplementedError
