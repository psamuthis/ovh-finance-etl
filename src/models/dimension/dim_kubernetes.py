from uuid import UUID
from sqlalchemy import (
    BigInteger,
    ForeignKey,
    SmallInteger,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class DimKubernetes(Base):
    __tablename__ = "dim_kubernetes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    fk_created_at: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    fk_updated_at: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    fk_deployed_at: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    fk_deleted_at: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    fk_tenant: Mapped[int] = mapped_column(SmallInteger, ForeignKey("dim_tenant.id"))

    cluster_id: Mapped[UUID] = mapped_column(Uuid)
    cluster_name: Mapped[str] = mapped_column(String)
    nodepool_id: Mapped[UUID] = mapped_column(Uuid)
    instance_id: Mapped[UUID] = mapped_column(Uuid)
    flavor: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    version: Mapped[str] = mapped_column(String)
