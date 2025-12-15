from pydantic import BaseModel


class ClickEventDTO(BaseModel):
    short_code: str
    timestamp: str
    ip_address: str | None = None
    user_agent: str | None = None
