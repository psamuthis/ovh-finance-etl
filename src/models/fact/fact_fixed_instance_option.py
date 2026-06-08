from decimal import Decimal

from models.base import Base
from sqlalchemy import BigInteger, ForeignKey, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column


class FactFixedInstanceOption(Base):
    __tablename__ = "fact_current_fixed_instance_option"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fk_deployment_mode: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_deployment_mode.id"))
    fk_region: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_region.id"))
    price: Mapped[Decimal] = mapped_column(Numeric)
    flavor: Mapped[str] = mapped_column(String)
