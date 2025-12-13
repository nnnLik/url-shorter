from .logging import init_logging
from .settings import Settings

settings = Settings.build()


__all__ = (
    "settings",
    "init_logging",
)
