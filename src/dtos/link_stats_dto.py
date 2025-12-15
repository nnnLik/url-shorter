from datetime import datetime

from pydantic import BaseModel


class LinkStatsResponseDTO(BaseModel):
    short_code: str
    original_url: str
    click_count: int
    last_click_at: datetime | None = None


class TopLinkDTO(BaseModel):
    original_url: str
    short_url: str
    click_count: int


class AppStatsResponseDTO(BaseModel):
    total_links: int
    total_clicks: int
    active_links: int
    top_links: list[TopLinkDTO]
