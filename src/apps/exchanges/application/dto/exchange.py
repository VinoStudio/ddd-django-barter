from dataclasses import dataclass
from datetime import datetime
from typing import Any, Self

from uuid6 import UUID

from src.apps.exchanges.domain import ExchangeStatus
from src.core.application.dto import DTO


@dataclass(frozen=True)
class ExchangeProposalDTO(DTO):
    id: UUID
    ad_sender_id: UUID
    ad_receiver_id: UUID
    comment: str
    status: str
    created_at: datetime

    @classmethod
    def from_request(cls, request: Any) -> Self:
        return cls(
            id=request.POST.get('id'),
            ad_sender_id=request.POST.get('ad_sender_id'),
            ad_receiver_id=request.POST.get('ad_receiver_id'),
            comment=request.POST.get('comment'),
            status=request.POST.get('status'),
            created_at=request.POST.get('created_at'),
        )


@dataclass(frozen=True)
class CreateExchangeDTO(DTO):
    ad_sender_id: UUID
    ad_receiver_id: UUID
    user_id: UUID
    comment: str = None

    @classmethod
    def from_request(cls, request: Any) -> Self:
        return cls(
            ad_sender_id=request.POST.get('ad_sender_id'),
            ad_receiver_id=request.POST.get('ad_receiver_id'),
            user_id=request.user.id,
            comment=request.POST.get('comment'),
        )


@dataclass(frozen=True)
class UpdateExchangeStatusDTO(DTO):
    exchange_id: UUID
    user_id: UUID
    status: ExchangeStatus

    @classmethod
    def from_request(cls, request: Any) -> Self:
        return cls(
            exchange_id=request.POST.get('exchange_id'),
            user_id=request.user.id,
            status=ExchangeStatus(request.POST.get('status')),
        )
