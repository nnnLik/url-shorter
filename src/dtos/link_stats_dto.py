from datetime import datetime

import msgspec


class LinkStatsResponseDTO(msgspec.Struct):
    short_code: str
    original_url: str
    click_count: int
    last_click_at: datetime | None = None


class TopLinkDTO(msgspec.Struct):
    original_url: str
    short_url: str
    click_count: int


class AppStatsResponseDTO(msgspec.Struct):
    total_links: int
    total_clicks: int
    active_links: int
    top_links: list[TopLinkDTO]
