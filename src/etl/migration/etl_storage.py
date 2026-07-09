from datetime import datetime

from connector.db_connection import WarehouseSessionLocal
from models.dimension.dim_storage import DimStorage
from models.fact.fact_storage import FactCurrentStorage
from models.finops.consomption_history import ConsomptionHistory
from services.db_service import DBService
from services.dimension.service_region import ServiceRegion
from services.dimension.service_storage_type import ServiceStorageType
from services.dimension.service_tenant import ServiceTenant
from services.dimension.service_time import ServiceTime
from services.dimension.service_unit import ServiceUnit


class ETLStorage:

    def __init__(self, project_id: str,  period_from: datetime, period_to: datetime):
        self.project_id = project_id
        self.period_from = period_from
        self.period_to = period_to

    def load_data(self, storage_entries: list[ConsomptionHistory]):
        if len(storage_entries) == 0:
            return

        with WarehouseSessionLocal() as db:
            fk_period_from: int = ServiceTime(db).get_or_create(self.period_from)
            fk_period_to: int = ServiceTime(db).get_or_create(self.period_to)
            fk_tenant: int = ServiceTenant(db).get_or_create(self.project_id)

            for entry in storage_entries:

                fk_storage: int = DBService(db, DimStorage).insert_one(DimStorage(
                    fk_deployment_mode=None,
                    fk_region=ServiceRegion(db).get_or_create(entry.region),
                    fk_type=ServiceStorageType(db).get_or_create(entry.reference),
                    name=""
                ))

                DBService(db, FactCurrentStorage).insert_one(FactCurrentStorage(
                    fk_storage=fk_storage,
                    fk_period_from=fk_period_from,
                    fk_period_to=fk_period_to,
                    fk_created_at=ServiceTime(db).get_or_create(entry._from),
                    fk_tenant=fk_tenant,
                    fk_in_bandwidth_unit=ServiceUnit(db).get_or_create(entry.incomingBandwidth_unit),
                    in_bandwidth_value=entry.incomingBandwidth_value,
                    fk_out_bandwidth_unit=ServiceUnit(db).get_or_create(entry.outgoingBandwidth_unit),
                    out_bandwidth_value=entry.outgoingBandwidth_value,
                    fk_stored_unit=ServiceUnit(db).get_or_create(entry.stored_unit),
                    stored_price=entry.totalPrice
                ))

            db.commit()
