from datetime import datetime
from typing import Any

from connector.db_connection import WarehouseSessionLocal
from models.dimension.dim_kubernetes import DimKubernetes
from models.fact.fact_current_fixed_compute import FactCurrentFixedCompute
from models.finops.consomption_history import ConsomptionHistory
from services.db_service import DBService
from services.dimension.api_service_kubernetes import APIServiceKubernetes
from services.dimension.db_service_kubernetes import DBServiceKubernetes
from services.dimension.service_region import ServiceRegion
from services.dimension.service_tenant import ServiceTenant
from services.dimension.service_time import ServiceTime


class ETLFixedInstance:

    def __init__(self, project_id: str,  period_from: datetime, period_to: datetime):
        self.project_id = project_id
        self.period_from = period_from
        self.period_to = period_to

    def load_data(self, instances: list[ConsomptionHistory]):
        with WarehouseSessionLocal() as db:
            fk_tenant: int = ServiceTenant(db).get_or_create(self.project_id)

            for instance in instances:

                fk_resource: int = DBService(db, DimKubernetes).insert_one(DimKubernetes(
                    fk_tenant=fk_tenant,
                    instance_id=instance.ressource_id,
                    flavor=instance.reference
                ))

                DBService(db, FactCurrentFixedCompute).insert_one(FactCurrentFixedCompute(
                    fk_region=ServiceRegion(db).get_or_create(instance.region),
                    fk_resource=fk_resource,
                    fk_created_at=ServiceTime(db).get_or_create(instance._from),
                    instance_id=instance.ressource_id,
                    price=instance.totalPrice
                ))

            db.commit()