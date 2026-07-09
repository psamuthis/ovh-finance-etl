from datetime import datetime
from typing import Any
from itertools import chain

from connector.db_connection import FinopsSessionLocal, WarehouseSessionLocal
from models.dimension.dim_kubernetes import DimKubernetes
from models.fact.fact_current_dynamic_compute import FactCurrentDynamicCompute
from models.finops.configuration_kub import ConfigurationKub
from models.finops.configuration_kub_history import ConfigurationKubHistory
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
        if len(instances) == 0:
            return

        kube_data: dict[str, Any] = {}
        kube_history_data: dict[str, Any] = {}

        with FinopsSessionLocal() as db:
            kube_entries: list[ConfigurationKub] = db.query(ConfigurationKub).all()
            kube_history_entries: list[ConfigurationKubHistory] = db.query(ConfigurationKubHistory).all()

            for entry in kube_entries:
                kube_data[entry.instance_id] = entry

            for entry in kube_history_entries:
                kube_history_data[entry.instance_id] = entry

        with WarehouseSessionLocal() as db:
            fk_tenant: int = ServiceTenant(db).get_or_create(self.project_id)

            for instance in instances:

                if instance.ressource_id in kube_data:
                    fk_resource: int = DBService(db, DimKubernetes).insert_one(DimKubernetes(
                        fk_tenant=fk_tenant,
                        cluster_name=kube_data[instance.ressource_id].cluster_name,
                        nodepool_id=kube_data[instance.ressource_id].nodepool_id,
                        instance_id=instance.ressource_id,
                        flavor=instance.reference
                    ))
                elif instance.ressource_id in kube_history_data:
                    fk_resource: int = DBService(db, DimKubernetes).insert_one(DimKubernetes(
                        fk_tenant=fk_tenant,
                        cluster_name=kube_history_data[instance.ressource_id].node_name,
                        nodepool_id=kube_history_data[instance.ressource_id].nodepool_id,
                        instance_id=instance.ressource_id,
                        flavor=instance.reference
                    ))
                else:
                    fk_resource: int = DBService(db, DimKubernetes).insert_one(DimKubernetes(
                        fk_tenant=fk_tenant,
                        instance_id=instance.ressource_id,
                        flavor=instance.reference
                    ))

                DBService(db, FactCurrentDynamicCompute).insert_one(FactCurrentDynamicCompute(
                    instance_id=instance.ressource_id,
                    fk_period_from=ServiceTime(db).get_or_create(instance._from),
                    fk_period_to=ServiceTime(db).get_or_create(instance._to),
                    fk_created_at=ServiceTime(db).get_or_create(instance._from),
                    fk_region=ServiceRegion(db).get_or_create(instance.region),
                    fk_deployment_mode=None,
                    fk_resource=fk_resource,
                    fk_usage_unit=ServiceUnit(db).get_or_create(instance.unit),
                    usage_value=instance.value,
                    usage_price=instance.totalPrice
                ))

            db.commit()
