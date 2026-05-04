from typing import Any
from uuid import UUID
import ovh
from sqlalchemy import (
    BigInteger,
    ForeignKey,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column

from connector.ovh_connection import OVHConnector
from models.dimension.dim_time import DimTime
from services.service_kubernetes import ServiceKubernetes


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

    @classmethod
    def from_raw_data(cls, service_id: str, node_id: str) -> "DimKubernetes":
        kube_service: ServiceKubernetes = ServiceKubernetes(service_id)
        tenant_name: str = kube_service.get_tenant()
        cluster_id: str = kube_service.get_node_cluster(node_id)
        node_response: dict[str, Any] = kube_service.get_node_data(node_id)

        created_at_fk: int = DimTime.get_or_create()
