from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from connector.postgres_connection import WarehouseSessionLocal
from models.dimension.dim_deployment_mode import DimDeploymentMode
from models.dimension.dim_kubernetes import DimKubernetes
from models.dimension.dim_region import DimRegion
from models.dimension.dim_storage_type import DimStorageType
from models.dimension.dim_volume import DimVolume
from services.dimension.api_service_kubernetes import APIServiceKubernetes
from services.dimension.db_service_kubernetes import DBServiceKubernetes
from services.dimension.service_deployment_mode import ServiceDeploymentMode
from services.dimension.service_region import ServiceRegion
from services.dimension.service_storage_type import ServiceStorageType
from services.dimension.service_time import ServiceTime
from services.dimension.service_volume import ServiceDimVolume
from services.dimension.service_unit import ServiceUnit
from models.fact.fact_volume import FactVolume
from services.db_service import DBService
from services.fact.service_volume import ServiceFactVolume
from services.dimension.service_tenant import ServiceTenant

from .dataclass.shared import Quantity
from .etl_interface import ETLInterface


@dataclass
class VolumeDetails:
    quantity: Quantity
    resource_id: str
    total_price: Decimal
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
                    total_price=round(Decimal(volume_details["totalPrice"]), 5),
                    volume_uuid=volume_details["volumeId"],
                )

                volume.details.append(details)
            self.volumes.append(volume)

    def load_data(self) -> None:

        for volume in self.volumes:
            with WarehouseSessionLocal() as db:
                fk_dep_mode: int = ServiceDeploymentMode(db).get_or_create(volume.deployment_mode)
                fk_region: int = ServiceRegion(db).get_or_create(volume.region)
                fk_type: int = ServiceStorageType(db).get_or_create(volume.type)
                fk_tenant: int = ServiceTenant(db).get_or_create(self.service_id)

                for details in volume.details:
                    dim_volume: DimVolume = DimVolume(
                        volume_uuid=details.volume_uuid,
                        fk_deployment_mode=fk_dep_mode,
                        fk_region=fk_region,
                        fk_type=fk_type,
                        fk_tenant=fk_tenant,
                    )

                    created_at: datetime = datetime.now(timezone.utc)
                    fk_created_at: int = ServiceTime(db).get_or_create(created_at)
                    fk_volume: int = ServiceDimVolume(db).insert_one(dim_volume)
                    non_cumulative_price: Decimal = ServiceFactVolume(db).get_non_cumulative_cost(
                        details.volume_uuid,
                        details.total_price,
                    )

                    record: FactVolume = FactVolume(
                        fk_volume=fk_volume,
                        fk_period_from=ServiceTime(db).get_or_create(self.period_from),
                        fk_period_to=ServiceTime(db).get_or_create(self.period_to),
                        fk_created_at=fk_created_at,
                        fk_unit=ServiceUnit(db).get_or_create(details.quantity.unit),
                        value=details.quantity.value,
                        price=non_cumulative_price,
                    )

                    DBService(db, FactVolume).insert_one(record)

                db.commit()
