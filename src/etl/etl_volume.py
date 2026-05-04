from dataclasses import dataclass, field
from typing import Any

from src.connector.postgres_connection import WarehouseSessionLocal
from src.models.dimension.dim_deployment_mode import DimDeploymentMode
from src.models.dimension.dim_kubernetes import DimKubernetes
from src.models.dimension.dim_region import DimRegion
from src.models.dimension.dim_storage_type import DimStorageType
from src.models.dimension.dim_volume import DimVolume
from src.services.service_kubernetes import ServiceKubernetes

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
                dep_mode_id: int = DimDeploymentMode.get_or_create(
                    db, volume.deployment_mode
                )
                region_id: int = DimRegion.get_or_create(db, volume.region)
                type_id: int = DimStorageType.get_or_create(db, volume.type)

                for details in volume.details:
                    dim_volume: DimVolume = DimVolume(
                        volume_uuid=details.volume_uuid,
                        deployment_mode_fk=dep_mode_id,
                        region_fk=region_id,
                        type_id=type_id,
                    )

                    dim_kubernetes: DimKubernetes = DimKubernetes.from_raw_data(
                        self.service_id, details.resource_id
                    )
                    # find cluster id
                    # retrieve node data
                    # get tenant from /cloud/project/{service_id}
