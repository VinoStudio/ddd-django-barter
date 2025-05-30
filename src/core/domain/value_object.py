from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

VT = TypeVar("VT", bound=Any)


@dataclass(frozen=True, slots=True, eq=True, unsafe_hash=True)
class ValueObject(ABC, Generic[VT]):

    @abstractmethod
    def _validate(self) -> None:
        raise NotImplementedError

    def __post_init__(self) -> None:
        self._validate()

    @abstractmethod
    def to_raw(self) -> str:
        raise NotImplementedError