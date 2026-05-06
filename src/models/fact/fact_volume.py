from sqlalchemy import (
    BigInteger,
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
    period_from_fk: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    period_to_fk: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    created_at_fk: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time"))
    volume_fk: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_volume.id"))
    resource_fk: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("dim_kubernetes.id")
    )
    deployment_fk: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("dim_deployment_mode")
    )
    region_fk: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_region.id"))
    type_fk: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_storage_type"))
    unit_fk: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_unit.id"))
    value: Mapped[float] = mapped_column(Numeric)
    price: Mapped[float] = mapped_column(Numeric)
