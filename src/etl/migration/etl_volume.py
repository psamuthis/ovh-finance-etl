from datetime import datetime

from connector.db_connection import FinopsSessionLocal, WarehouseSessionLocal
from models.dimension.dim_volume import DimVolume
from models.fact.fact_volume import FactVolume
from models.finops.consomption_history import ConsomptionHistory
from services.db_service import DBService
from services.dimension.service_deployment_mode import ServiceDeploymentMode
from services.dimension.service_region import ServiceRegion
from services.dimension.service_storage_type import ServiceStorageType
from services.dimension.service_tenant import ServiceTenant
from services.dimension.service_time import ServiceTime
from services.dimension.service_unit import ServiceUnit


class ETLVolume:
    def __init__(self, project_id: str, period_from: datetime, period_to: datetime):
        self.project_id = project_id
        self.period_from = period_from
        self.period_to = period_to

    def load_data(self, volumes: list[ConsomptionHistory]) -> None:
        with WarehouseSessionLocal() as db:

            fk_period_from: int = ServiceTime(db).get_or_create(self.period_from)
            fk_period_to: int = ServiceTime(db).get_or_create(self.period_to)
            fk_tenant: int = ServiceTenant(db).get_or_create(self.project_id)

            for volume in volumes:
                fk_created_at: int = ServiceTime(db).get_or_create(volume._from)

                fk_volume: int = DBService(db, DimVolume).insert_one(DimVolume(
                    volume_uuid=volume.ressource_id,
                    fk_deployment_mode=None,
                    fk_region=ServiceRegion(db).get_or_create(volume.region),
                    fk_type=ServiceStorageType(db).get_or_create(volume.reference),
                    fk_tenant=fk_tenant
                ))

                DBService(db, FactVolume).insert_one(FactVolume(
                    fk_period_from=fk_period_from,
                    fk_period_to=fk_period_to,
                    fk_created_at=fk_created_at,
                    fk_volume=fk_volume,
                    fk_unit=ServiceUnit(db).get_or_create(volume.stored_unit),
                    value=volume.stored_value,
                    price=volume.totalPrice
                ))

            db.commit()