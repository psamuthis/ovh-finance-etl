from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    SmallInteger,
    TIMESTAMP,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from src.models.dimension.dim_region import DimRegion


class DimTime(DeclarativeBase):
    __tablename__ = "dim_time"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    year: Mapped[int] = mapped_column(SmallInteger)
    month: Mapped[int] = mapped_column(SmallInteger)
    day: Mapped[int] = mapped_column(SmallInteger)
    quarter: Mapped[int] = mapped_column(SmallInteger)

    @staticmethod
    def parse_iso_date(date_str: str) -> datetime:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))

    @staticmethod
    def get_or_create(db: Session, timestamp: datetime) -> int:
        existing_record: DimTime | None = (
            db.query(DimTime).filter_by(timestamp=timestamp).first()
        )

        if existing_record is None:
            new_record: DimTime = DimTime(
                timestamp=timestamp,
                year=timestamp.year,
                month=timestamp.month,
                day=timestamp.day,
                quarter=(timestamp.month - 1) // 3 + 1,
            )
            db.add(new_record)
            db.flush()
            return new_record.id

        return existing_record.id
