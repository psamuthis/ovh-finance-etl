from uuid import UUID
from sqlalchemy import (
    BigInteger,
    ForeignKey,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column


class DimKubernetes(DeclarativeBase):
    __tablename__ = "dim_kubernetes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    created_at_fk: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    updated_at_fk: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    deployed_at_fk: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))
    deleted_at_fk: Mapped[int] = mapped_column(BigInteger, ForeignKey("dim_time.id"))

    cluster_id: Mapped[UUID] = mapped_column(Uuid)
    nodepool_id: Mapped[UUID] = mapped_column(Uuid)
    instance_id: Mapped[UUID] = mapped_column(Uuid)
    flavor: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    version: Mapped[str] = mapped_column(String)
    tenant_name: Mapped[str] = mapped_column(String)
