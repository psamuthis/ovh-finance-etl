from decimal import Decimal

from sqlalchemy import UUID, BigInteger, ForeignKey, Numeric, SmallInteger, Uuid
from sqlalchemy.orm import Mapped, foreign, mapped_column

from models.base import Base


class FactCurrentDynamicCompute(Base):
    __tablename__ = "fact_current_dynamic_compute"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    instance_id: Mapped[str] = mapped_column(UUID)

    fk_period_from: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    fk_period_to: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    fk_created_at: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    fk_tenant: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_tenant.id"))
    fk_region: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_region.id"))
    fk_deployment_mode: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("dim_deployment_mode.id")
    )
    fk_resource: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_kubernetes.id"))
    fk_usage_unit: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_unit.id"))

    usage_value: Mapped[Decimal] = mapped_column(Numeric)
    usage_price: Mapped[Decimal] = mapped_column(Numeric)
