from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from connector.postgres_connection import WarehouseSessionLocal
from models.dimension.dim_deployment_mode import DimDeploymentMode
from models.dimension.dim_kubernetes import DimKubernetes
from models.dimension.dim_region import DimRegion
from models.dimension.dim_storage_type import DimStorageType
from models.dimension.dim_volume import DimVolume
from services.api_service_kubernetes import APIServiceKubernetes
from services.db_service_kubernetes import DBServiceKubernetes
from services.service_deployment_mode import ServiceDeploymentMode
from services.service_region import ServiceRegion
from services.service_storage_type import ServiceStorageType
from services.service_time import ServiceTime
from services.service_volume import ServiceDimVolume, ServiceFactVolume
from services.service_unit import ServiceUnit
from models.fact.fact_volume import FactVolume
from services.db_service import DBService

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

    def __init__(self, service_id: str, period_from: datetime, period_to: datetime):
        self.volumes: list[Volume] = []
        self.service_id = service_id
        self.period_from = period_from
        self.period_to = period_to

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
                fk_dep_mode: int = ServiceDeploymentMode(db).get_or_create(
                    volume.deployment_mode
                )
                fk_region: int = ServiceRegion(db).get_or_create(volume.region)
                fk_type: int = ServiceStorageType(db).get_or_create(volume.type)

                for details in volume.details:
                    dim_volume: DimVolume = DimVolume(
                        volume_uuid=details.volume_uuid,
                        fk_deployment_mode=fk_dep_mode,
                        fk_region=fk_region,
                        fk_type=fk_type,
                    )

                    print(details.resource_id)
                    node_id: str = details.resource_id
                    dim_kubernetes: Optional[DimKubernetes] = DBServiceKubernetes(
                        db
                    ).create_record(self.service_id, node_id)

                    if dim_kubernetes is None:
                        fk_resource = None
                    else:
                        fk_resource = DBServiceKubernetes(db).insert_one(dim_kubernetes)

                    record: FactVolume = FactVolume(
                        fk_volume=ServiceDimVolume(db).insert_one(dim_volume),
                        fk_period_from=ServiceTime(db).get_or_create(self.period_from),
                        fk_period_to=ServiceTime(db).get_or_create(self.period_to),
                        fk_created_at=ServiceTime(db).get_or_create(
                            datetime.now(timezone.utc)
                        ),
                        fk_resource=fk_resource,
                        fk_unit=ServiceUnit(db).get_or_create(details.quantity.unit),
                        # TODO: transformer le cumulé en non cumulé
                        value=69,
                        price=69,
                    )

                    DBService(db, FactVolume).insert_one(record)
                    db.commit()
