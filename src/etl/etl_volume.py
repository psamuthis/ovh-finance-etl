from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from connector.postgres_connection import WarehouseSessionLocal
from models.dimension.dim_deployment_mode import DimDeploymentMode
from models.dimension.dim_kubernetes import DimKubernetes
from models.dimension.dim_region import DimRegion
from models.dimension.dim_storage_type import DimStorageType
from models.dimension.dim_volume import DimVolume
from src.services.api_service_kubernetes import APIServiceKubernetes
from src.services.db_service_kubernetes import DBServiceKubernetes
from src.services.service_deployment_mode import ServiceDeploymentMode
from src.services.service_region import ServiceRegion
from src.services.service_storage_type import ServiceStorageType
from src.services.service_time import ServiceTime
from src.services.service_volume import ServiceVolume

from .shared import Quantity
from .etl_interface import ETLInterface


@dataclass
class VolumeDetails:
    quantity: Quantity
    resource_id: str
    total_price: float
    volume_uuid: str


@dataclass
class Volume:
    deployment_mode: str = ""
    details: list[VolumeDetails] = field(default_factory=list)
    region: str = ""
    type: str = ""


class ETLVolume(ETLInterface):

    def __init__(self, service_id: str):
        self.volumes: list[Volume] = []
        self.service_id = service_id

    def extract_data(self, raw_data: list[dict[str, Any]]) -> None:
        for volume_group in raw_data:
            volume = Volume()
            volume.deployment_mode = volume_group["deploymentMode"]
            volume.region = volume_group["region"]
            volume.type = volume_group["type"]

            for volume_details in volume_group["details"]:
                quantity = Quantity(
                    unit=volume_details["quantity"]["unit"],
                    value=volume_details["quantity"]["value"],
                )

                details = VolumeDetails(
                    quantity=quantity,
                    resource_id=volume_details["resourceId"],
                    total_price=volume_details["totalPrice"],
                    volume_uuid=volume_details["volumeId"],
                )

                volume.details.append(details)
            self.volumes.append(volume)

    def load_data(self) -> None:

        for volume in self.volumes:
            with WarehouseSessionLocal() as db:
                dep_mode_id: int = ServiceDeploymentMode(db).get_or_create(
                    volume.deployment_mode
                )
                region_id: int = ServiceRegion(db).get_or_create(volume.region)
                type_id: int = ServiceStorageType(db).get_or_create(volume.type)

                for details in volume.details:
                    dim_volume: DimVolume = DimVolume(
                        volume_uuid=details.volume_uuid,
                        deployment_mode_fk=dep_mode_id,
                        region_fk=region_id,
                        type_id=type_id,
                    )

                    api_kube_service: APIServiceKubernetes = APIServiceKubernetes(
                        self.service_id
                    )
                    time_service: ServiceTime = ServiceTime(db)

                    node_id: str = details.resource_id
                    node_data: dict[str, Any] = api_kube_service.get_node_data(node_id)
                    cluster_id: str = api_kube_service.get_node_cluster(node_id)
                    tenant_name: str = api_kube_service.get_tenant()

                    dim_kubernetes: DimKubernetes = DimKubernetes(
                        created_at_fk=time_service.get_or_create(
                            time_service.parse_iso_date(node_data["createdAt"])
                        ),
                        updated_at_fk=time_service.get_or_create(
                            time_service.parse_iso_date(node_data["updatedAt"])
                        ),
                        deployed_at_fk=time_service.get_or_create(
                            time_service.parse_iso_date(node_data["deployedAt"])
                        ),
                        deleted_at_fk=None,
                        cluster_id=cluster_id,
                        nodepool_id=node_data["nodePoolId"],
                        instance_id=node_data["instanceId"],
                        flavor=node_data["flavor"],
                        status=node_data["status"],
                        version=node_data["version"],
                        tenant_name=tenant_name,
                    )

                    DBServiceKubernetes(db).insert_one(dim_kubernetes)
                    ServiceVolume(db).insert_one(dim_volume)
