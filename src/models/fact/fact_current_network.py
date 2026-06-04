from decimal import Decimal

from sqlalchemy import BigInteger, ForeignKey, Numeric, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class FactCurrentNetwork(Base):
    __tablename__ = "fact_current_network"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fk_deployment_mode: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("dim_deployment_mode.id")
    )
    fk_region: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_region.id"))
    fk_incoming_unit: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_unit.id"))
    fk_outgoing_unit: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_unit.id"))
    incoming_value: Mapped[Decimal] = mapped_column(Numeric)
    outgoing_value: Mapped[Decimal] = mapped_column(Numeric)
    incoming_price: Mapped[Decimal] = mapped_column(Numeric)
    outgoing_price: Mapped[Decimal] = mapped_column(Numeric)
