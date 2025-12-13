from datetime import datetime
from typing import TYPE_CHECKING, Self

import msgspec

if TYPE_CHECKING:
    from models.link import Link


class LinkDTO(msgspec.Struct):
    id: int
    short_code: str
    original_url: str
    created_at: datetime
    expires_at: datetime | None = None

    @classmethod
    def from_model(cls, model: 'Link') -> Self:
        return cls(
            id=model.id,
            short_code=model.short_code,
            original_url=model.original_url,
            created_at=model.created_at,
            expires_at=model.expires_at,
        )
