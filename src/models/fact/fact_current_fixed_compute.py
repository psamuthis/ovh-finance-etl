from decimal import Decimal

from sqlalchemy import UUID, BigInteger, ForeignKey, Numeric, SmallInteger, Uuid
from sqlalchemy.orm import Mapped, foreign, mapped_column

from models.base import Base


class FactCurrentFixedCompute(Base):
    __tablename__ = "fact_current_fixed_compute"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fk_deployment_mode: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_deployment_mode.id"), nullable=True)
    fk_region: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_region.id"))
    fk_activation: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"), nullable=True)
    fk_resource: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_kubernetes.id"))
    fk_created_at: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    instance_id: Mapped[str] = mapped_column(UUID)
    price: Mapped[Decimal] = mapped_column(Numeric)
