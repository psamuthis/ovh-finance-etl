from decimal import Decimal
from sqlalchemy import BigInteger, ForeignKey, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class FactDynamicInstanceOption(Base):
    __tablename__ = "fact_current_dynamic_instance_option"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fk_deployment_mode: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_deployment_mode.id"))
    fk_region: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_region.id"))
    fk_unit: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_unit.id"))
    value: Mapped[Decimal] = mapped_column(Numeric)
    price: Mapped[Decimal] = mapped_column(Numeric)
    flavor: Mapped[str] = mapped_column(String)
