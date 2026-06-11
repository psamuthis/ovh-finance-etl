from decimal import Decimal

from models.base import Base
from sqlalchemy import BigInteger, ForeignKey, Integer, Numeric, SmallInteger, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column


class DimSavingsPlan(Base):
    __tablename__ = "dim_current_savings_plan"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    fk_period_from: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    fk_period_to: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    size: Mapped[int] = mapped_column(Integer)
    flavor: Mapped[str] = mapped_column(Integer)
    currency_code: Mapped[str] = mapped_column(String)
    price: Mapped[Decimal] = mapped_column(Numeric)
    plan_id: Mapped[str] = mapped_column(Uuid)