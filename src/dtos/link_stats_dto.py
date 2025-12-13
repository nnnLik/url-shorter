from datetime import datetime

import msgspec


class LinkStatsResponseDTO(msgspec.Struct):
    """Статистика по конкретной ссылке."""
    short_code: str
    original_url: str
    click_count: int
    last_click_at: datetime | None = None


class AppStatsResponseDTO(msgspec.Struct):
    """Общая статистика приложения."""
    total_links: int
    total_clicks: int
    active_links: int  # Ссылки, которые не истекли

