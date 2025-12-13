import msgspec


class ClickEventDTO(msgspec.Struct):
    short_code: str
    timestamp: str
    ip_address: str | None = None
    user_agent: str | None = None
