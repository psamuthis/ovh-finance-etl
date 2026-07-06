from datetime import datetime

from connector.db_connection import WarehouseSessionLocal
from models.dimension.dim_kubernetes import DimKubernetes
from models.fact.fact_current_dynamic_compute import FactCurrentDynamicCompute
from models.finops.consomption_history import ConsomptionHistory
from services.db_service import DBService
from services.dimension.service_region import ServiceRegion
from services.dimension.service_tenant import ServiceTenant
from services.dimension.service_time import ServiceTime
from services.dimension.service_unit import ServiceUnit


class ETLDynamicInstance:
    def __init__(self, project_id: str, period_from: datetime, period_to: datetime):
        self.project_id: str = project_id
        self.period_from: datetime = period_from
        self.period_to: datetime = period_to

    def load_data(self, instances: list[ConsomptionHistory]):
        with WarehouseSessionLocal() as db:
            fk_tenant: int = ServiceTenant(db).get_or_create(self.project_id)

            for instance in instances:
                fk_resource: int = DBService(db, DimKubernetes).insert_one(DimKubernetes(
                    fk_tenant=fk_tenant,
                    instance_id=instance.ressource_id,
                    flavor=instance.reference
                ))

                DBService(db, FactCurrentDynamicCompute).insert_one(FactCurrentDynamicCompute(
                    instance_id=instance.ressource_id,
                    fk_period_from=ServiceTime(db).get_or_create(instance._from),
                    fk_period_to=ServiceTime(db).get_or_create(instance._to),
                    fk_created_at=ServiceTime(db).get_or_create(instance.last_update),
                    fk_region=ServiceRegion(db).get_or_create(instance.region),
                    fk_deployment_mode=None,
                    fk_resource=fk_resource,
                    fk_usage_unit=ServiceUnit(db).get_or_create(instance.unit),
                    usage_value=instance.value,
                    usage_price=instance.totalPrice
                ))

            db.commit()
