from decimal import Decimal

from models.base import Base
from sqlalchemy import BigInteger, ForeignKey, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column


class FactSavingsPlanOverQuota(Base):
    __tablename__ = "fact_savings_plan_over_quota"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fk_unit: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_unit.id"))
    fk_created_at: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    value: Mapped[Decimal] = mapped_column(Numeric)
    price: Mapped[Decimal] = mapped_column(Numeric)
    flavor: Mapped[str] = mapped_column(String)