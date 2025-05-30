from uuid6 import UUID
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Self

from src.apps.ads.application.helpers import create_image_url
from src.core.application.dto import DTO


@dataclass(frozen=True)
class AdDTO(DTO):
    id: Optional[UUID] = None
    user_id: UUID = None
    username: Optional[str] = None
    title: str = None
    description: str = None
    image_url: Optional[str] = None
    category: str = None
    condition: str = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_request(cls, request) -> Self:
        return cls(
            id=request.POST.get('ad_id'),
            user_id=request.user.id,
            username=request.user.username,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            image_url=request.POST.get('image_url'),
            category=request.POST.get('category'),
            condition=request.POST.get('condition')
        )


@dataclass(frozen=True)
class CreateAdDTO(DTO):
    user_id: UUID
    title: str
    description: str
    image_url: Optional[str] = None
    category: str = 'other'
    condition: str = 'used'
    status: str = 'active'

    @classmethod
    def from_request(cls, request) -> Self:
        img = request.FILES.get('image')
        return cls(
            user_id=request.user.id,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            image_url=create_image_url(img) if img else None,
            category=request.POST.get('category'),
            condition=request.POST.get('condition'),
            status=request.POST.get('status', "active")
        )

@dataclass(frozen=True)
class UpdateAdDTO(DTO):
    ad_id: UUID
    user_id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    condition: Optional[str] = None
    status: Optional[str] = None

    @classmethod
    def from_request(cls, request, ad_id) -> Self:
        img = request.FILES.get('image')
        return cls(
            ad_id=ad_id,
            user_id=request.user.id,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            image_url=create_image_url(img) if img else None,
            category=request.POST.get('category'),
            condition=request.POST.get('condition'),
            status=request.POST.get('status')
        )


@dataclass(frozen=True)
class AdFilterDTO:
    page: int = 1
    page_size: int = 12
    keyword: Optional[str] = None
    category: Optional[str] = None
    condition: Optional[str] = None
    status: Optional[str] = 'active'

