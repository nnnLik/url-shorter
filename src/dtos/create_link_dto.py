from datetime import datetime

from pydantic import BaseModel


class CreateLinkRequestDTO(BaseModel):
    original_url: str
    expires_at: datetime | None = None


class CreateLinkResponseDTO(BaseModel):
    short_code: str
    short_url: str
    created_at: datetime
    expires_at: datetime | None = None


class BatchCreateLinkRequestDTO(BaseModel):
    original_url: str
    count: int
    expires_at: datetime | None = None


class BatchCreateLinkResponseDTO(BaseModel):
    links: list[CreateLinkResponseDTO]
