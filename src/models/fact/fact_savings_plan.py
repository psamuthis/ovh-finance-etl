from decimal import Decimal

from sqlalchemy import BigInteger, ForeignKey, Integer, Numeric, SmallInteger, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column


class FactSavingsPlan:
    __tablename__ = "fact_current_savings_plan"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    fk_period_from: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    fk_period_to: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    size: Mapped[int] = mapped_column(Integer)
    flavor: Mapped[str] = mapped_column(Integer)
    currency_code: Mapped[str] = mapped_column(String)
    price: Mapped[Decimal] = mapped_column(Numeric)
    plan_id: Mapped[str] = mapped_column(Uuid)
    fk_over_quota_unit: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_unit.id"))
    over_quota_value: Mapped[int] = mapped_column(Numeric)
    over_quota_price: Mapped[int] = mapped_column(Numeric)