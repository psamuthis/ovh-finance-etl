from datetime import datetime
from decimal import Decimal

from models.base import Base
from sqlalchemy import DateTime, Float, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column


class ConsomptionHistory(Base):
    __tablename__ = "consomption_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    service_name: Mapped[str] = mapped_column(String)
    tenant_name: Mapped[str] = mapped_column(String)
    region: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    reference: Mapped[str] = mapped_column(String)
    ressource_id: Mapped[str] = mapped_column(String)

    _from: Mapped[datetime] = mapped_column(DateTime)
    _to: Mapped[datetime] = mapped_column(DateTime)
    last_update: Mapped[datetime] = mapped_column(DateTime)

    unit: Mapped[str] = mapped_column(String)
    value: Mapped[Decimal] = mapped_column(Float)

    stored_unit: Mapped[str] = mapped_column(String)
    stored_value: Mapped[Decimal] = mapped_column(Float)

    outgoingBandwidth_unit: Mapped[str] = mapped_column(String)
    outgoingBandwidth_value: Mapped[Decimal] = mapped_column(Float)
    incomingBandwidth_unit: Mapped[str] = mapped_column(String)
    incomingBandwidth_value: Mapped[Decimal] = mapped_column(Float)

    totalPrice: Mapped[Decimal] = mapped_column(Float)
    cost_type: Mapped[str] = mapped_column(String)
    count: Mapped[int] = mapped_column(Integer)
    priceCalculated: Mapped[int] = mapped_column(SmallInteger)
    