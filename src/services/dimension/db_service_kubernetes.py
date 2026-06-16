import json

from dateutil import parser
from typing import Any, Optional

from services.dimension.service_tenant import ServiceTenant
from sqlalchemy.orm import Session

from models.dimension.dim_kubernetes import DimKubernetes
from services.dimension.api_service_kubernetes import APIServiceKubernetes
from services.db_service import DBService
from services.dimension.service_time import ServiceTime


class DBServiceKubernetes(DBService[DimKubernetes]):
    def __init__(self, db: Session):
        super().__init__(db, DimKubernetes)

    def create_record(self, fk_tenant: int, node_data: dict[str, Any]) -> DimKubernetes:
        fk_deployed_at: Optional[int] = None

        if node_data["deployedAt"] is not None:
            fk_deployed_at = ServiceTime(self.db).get_or_create(parser.parse(node_data["deployedAt"]))

        return DimKubernetes(
            fk_created_at=ServiceTime(self.db).get_or_create(parser.parse(node_data["createdAt"])),
            fk_updated_at=ServiceTime(self.db).get_or_create(parser.parse(node_data["updatedAt"])),
            fk_deployed_at=fk_deployed_at,
            fk_deleted_at=None,
            fk_tenant=fk_tenant,
            cluster_id=node_data["clusterId"],
            nodepool_id=node_data["nodePoolId"],
            instance_id=node_data["instanceId"],
            flavor=node_data["flavor"],
            status=node_data["status"],
            version=node_data["version"]
        )