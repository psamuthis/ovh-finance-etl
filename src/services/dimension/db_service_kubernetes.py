from typing import Any, Optional

from sqlalchemy.orm import Session

from models.dimension.dim_kubernetes import DimKubernetes
from src.services.dimension.api_service_kubernetes import APIServiceKubernetes
from src.services.dimension.dim_db_service import DIMDBService
from src.services.dimension.service_time import ServiceTime


class DBServiceKubernetes(DIMDBService[DimKubernetes]):
    def __init__(self, db: Session):
        super().__init__(db, DimKubernetes)

    def create_record(self, service_id: str, node_id: str) -> Optional[DimKubernetes]:
        api_kube_service: APIServiceKubernetes = APIServiceKubernetes(service_id)
        time_service: ServiceTime = ServiceTime(self.db)

        node_data: Optional[dict[str, Any]] = api_kube_service.get_node_data(node_id)
        if node_data is None:
            return None

        fk_created_at: int = time_service.get_or_create(
            time_service.parse_iso_date(node_data["createdAt"])
        )
        fk_updated_at: int = time_service.get_or_create(
            time_service.parse_iso_date(node_data["updatedAt"])
        )
        fk_deployed_at: int = time_service.get_or_create(
            time_service.parse_iso_date(node_data["deployedAt"])
        )

        return DimKubernetes(
            fk_created_at=fk_created_at,
            fk_updated_at=fk_updated_at,
            fk_deployed_at=fk_deployed_at,
            fk_deleted_at=None,
            cluster_id=api_kube_service.get_node_cluster(node_id),
            nodepool_id=node_data["nodePoolId"],
            instance_id=node_data["instanceId"],
            tenant_name=api_kube_service.get_tenant(),
            flavor=node_data["flavor"],
            status=node_data["status"],
            version=node_data["version"],
        )
