from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, String, Text, event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapped, Mapper, mapped_column, relationship

from .base import Base
from .mixins import CreatedAtMixin, IntPkMixin

if TYPE_CHECKING:
    from .link_stats import LinkStats


class Link(Base, IntPkMixin, CreatedAtMixin):
    short_code: Mapped[str] = mapped_column(String(8), unique=True, index=True, nullable=False)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)

    stats: Mapped['LinkStats'] = relationship(
        'LinkStats',
        back_populates='link',
        uselist=False,
        cascade='all, delete-orphan',
    )


@event.listens_for(Link, 'after_insert')
def create_link_stats(
    _: Mapper,
    connection: Connection,
    target: Link,
) -> None:
    from .link_stats import LinkStats

    connection.execute(
        LinkStats.__table__.insert().values(
            link_id=target.id,
            click_count=0,
            last_click_at=None,
        )
    )
