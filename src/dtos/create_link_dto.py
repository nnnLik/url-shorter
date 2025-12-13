from datetime import datetime

import msgspec


class CreateLinkRequestDTO(msgspec.Struct):
    original_url: str
    expires_at: datetime | None = None


class CreateLinkResponseDTO(msgspec.Struct):
    short_code: str
    short_url: str
    created_at: datetime
    expires_at: datetime | None = None


class BatchCreateLinkRequestDTO(msgspec.Struct):
    original_url: str
    count: int
    expires_at: datetime | None = None


class BatchCreateLinkResponseDTO(msgspec.Struct):
    links: list[CreateLinkResponseDTO]
