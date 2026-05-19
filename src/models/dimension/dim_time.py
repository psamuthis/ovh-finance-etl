from datetime import datetime

from sqlalchemy import (
    BigInteger,
    SmallInteger,
    TIMESTAMP,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from models.base import Base


class DimTime(Base):
    __tablename__ = "dim_time"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    timestamptz: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    year: Mapped[int] = mapped_column(SmallInteger)
    month: Mapped[int] = mapped_column(SmallInteger)
    day: Mapped[int] = mapped_column(SmallInteger)
    quarter: Mapped[int] = mapped_column(SmallInteger)
