from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import IntPkMixin

if TYPE_CHECKING:
    from .link import Link


class LinkStats(Base, IntPkMixin):
    link_id: Mapped[int] = mapped_column(
        ForeignKey('link.id', ondelete='CASCADE'),
        unique=True,
        index=True,
        nullable=False,
    )
    click_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    last_click_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)

    link: Mapped['Link'] = relationship('Link', back_populates='stats')
