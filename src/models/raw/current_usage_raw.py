from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import DateTime, BigInteger, Numeric, String
from sqlalchemy.orm import Mapped, Session, declarative_base, mapped_column
from sqlalchemy.dialects.postgresql import JSONB


from models.base import Base


class CurrentUsageRaw(Base):
    __tablename__ = "current_usage_raw"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    service_id: Mapped[str] = mapped_column(String)
    period_from: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    period_to: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    call_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_update: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    total_price: Mapped[float] = mapped_column(Numeric(20, 6))
    total_price_currency: Mapped[str] = mapped_column(String)
    full_response_json: Mapped[dict[str, Any]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    @staticmethod
    def retrieve_latest_record(db: Session) -> Optional["CurrentUsageRaw"]:
        return (
            db.query(CurrentUsageRaw)
            .order_by(CurrentUsageRaw.created_at.desc())
            .first()
        )
