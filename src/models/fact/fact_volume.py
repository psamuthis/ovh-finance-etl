from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Integer,
    SmallInteger,
    String,
    Numeric,
    ForeignKey,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from models.base import Base


class FactVolume(Base):
    __tablename__ = "fact_current_dynamic_volume"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fk_period_from: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    fk_period_to: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    fk_created_at: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    fk_volume: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_volume.id"))
    fk_unit: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_unit.id"))
    value: Mapped[int] = mapped_column(Integer)
    price: Mapped[Decimal] = mapped_column(Numeric)
