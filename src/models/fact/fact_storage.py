from decimal import Decimal

from models.base import Base
from sqlalchemy import BigInteger, ForeignKey, Numeric, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column


class FactCurrentStorage(Base):
    __tablename__ = "fact_current_dynamic_storage"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fk_storage: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_storage.id"))

    fk_period_from: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    fk_period_to: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    fk_created_at: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))

    fk_in_bandwidth_unit: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_unit.id"))
    in_bandwidth_value: Mapped[Decimal] = mapped_column(Numeric)
    in_bandwidth_price: Mapped[Decimal] = mapped_column(Numeric, nullable=True)
    fk_in_internal_bandwidth_unit: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_unit.id"), nullable=True)
    in_internal_bandwidth_value: Mapped[Decimal] = mapped_column(Numeric, nullable=True)
    in_internal_bandwidth_price: Mapped[Decimal] = mapped_column(Numeric, nullable=True)

    fk_out_bandwidth_unit: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_unit.id"), nullable=True)
    out_bandwidth_value: Mapped[Decimal] = mapped_column(Numeric)
    out_bandwidth_price: Mapped[Decimal] = mapped_column(Numeric, nullable=True)
    fk_out_internal_bandwidth_unit: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_unit.id"), nullable=True)
    out_internal_bandwidth_value: Mapped[Decimal] = mapped_column(Numeric, nullable=True)
    out_internal_bandwidth_price: Mapped[Decimal] = mapped_column(Numeric, nullable=True)

    fk_retrieval_fees_unit: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_unit.id"), nullable=True)
    retrieval_fees_value: Mapped[Decimal] = mapped_column(Numeric, nullable=True)
    retrieval_fees_price: Mapped[Decimal] = mapped_column(Numeric, nullable=True)

    fk_stored_unit: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_unit.id"))
    stored_value: Mapped[Decimal] = mapped_column(Numeric)
    stored_price: Mapped[Decimal] = mapped_column(Numeric)

    fk_tenant: Mapped[int] = mapped_column(SmallInteger)