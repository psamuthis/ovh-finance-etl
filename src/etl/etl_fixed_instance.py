from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from connector.db_connection import WarehouseSessionLocal
from etl.dataclass.instance import FixedInstance, FixedInstanceOption
from models.bridge.bridge_fixed_instance_options import BridgeFixedInstanceOption
from models.dimension.dim_kubernetes import DimKubernetes
from models.fact.fact_current_fixed_compute import FactCurrentFixedCompute
from models.fact.fact_fixed_instance_option import FactFixedInstanceOption
from services.db_service import DBService
from services.dimension.api_service_kubernetes import APIServiceKubernetes
from services.dimension.db_service_kubernetes import DBServiceKubernetes
from services.dimension.service_deployment_mode import ServiceDeploymentMode
from services.dimension.service_region import ServiceRegion
from services.dimension.service_tenant import ServiceTenant
from services.dimension.service_time import ServiceTime
from services.fact.service_fixed_instance import ServiceFixedInstance
from config import DECIMAL_PRECISION


class ETLFixedInstance:
    def __init__(self, service_id: str, period_from: datetime, period_to: datetime, archived_at: datetime):
        self.service_id: str = service_id
        self.period_from: datetime = period_from
        self.period_to: datetime = period_to
        self.archived_at: datetime = archived_at
        self.fixed_instances: list[FixedInstance] = []
        self.instance_option: dict[str, FixedInstanceOption] = {}

    def extract_data(self, instance_data: list[dict[str, Any]], instance_option_data: list[dict[str, Any]]) -> None:
        for instance_group in instance_data:
            deployment_mode: str = instance_group["deploymentMode"]
            reference: str = instance_group["reference"]
            region: str = instance_group["region"]

            for detail in instance_group["details"]:
                fixed_instance: FixedInstance = FixedInstance(
                    deployment_mode,
                    ServiceTime.parse_iso_date(detail["activation"]),
                    detail["instanceId"],
                    detail["resourceId"],
                    reference,
                    region,
                    round(Decimal(detail["totalPrice"]), DECIMAL_PRECISION),
                )
                self.fixed_instances.append(fixed_instance)

            for option_group in instance_option_data:
                deployment_mode: str = option_group["deploymentMode"]
                region: str = option_group["region"]
                flavor: str = option_group["reference"]

                for detail in option_group["details"]:
                    self.instance_option[detail["instanceId"]] = FixedInstanceOption(
                        deployment_mode=deployment_mode,
                        region=region,
                        instance_id=detail["instanceId"],
                        total_price=round(Decimal(detail["totalPrice"]), DECIMAL_PRECISION),
                        flavor=flavor,
                    )

    def load_data(self) -> None:
        with WarehouseSessionLocal() as db:
            fk_tenant: int = ServiceTenant(db).get_or_create(self.service_id)
            kube_instances: dict[str, dict[str, Any]] = APIServiceKubernetes(self.service_id).find_latest_kube_match(
                [instance.instance_id for instance in self.fixed_instances]
            )

            for fixed_instance in self.fixed_instances:
                fk_deployment_mode: int = ServiceDeploymentMode(db).get_or_create(fixed_instance.deployment_mode)
                fk_region: int = ServiceRegion(db).get_or_create(fixed_instance.region)
                fk_activation: int = ServiceTime(db).get_or_create(fixed_instance.activation_date)
                fk_resource: Optional[int] = None

                if fixed_instance.instance_id in kube_instances:
                    fk_resource = DBService(db, DimKubernetes).insert_one(
                        DBServiceKubernetes(db).create_record(fk_tenant, kube_instances[fixed_instance.instance_id])
                    )

                fk_instance: int = ServiceFixedInstance(db).get_or_create(
                    FactCurrentFixedCompute(
                        fk_deployment_mode=fk_deployment_mode,
                        fk_region=fk_region,
                        fk_activation=fk_activation,
                        fk_resource=fk_resource,
                        fk_created_at=ServiceTime(db).get_or_create(self.archived_at),
                        instance_id=fixed_instance.instance_id,
                        price=fixed_instance.total_price,
                    ),
                    self.archived_at,
                )

                if fixed_instance.instance_id in self.instance_option:
                    fk_option = DBService(db, FactFixedInstanceOption).insert_one(
                        FactFixedInstanceOption(
                            fk_deployment_mode=fk_deployment_mode,
                            fk_region=fk_region,
                            price=fixed_instance.total_price,
                            flavor=self.instance_option[fixed_instance.instance_id].flavor,
                        )
                    )

                    DBService(db, BridgeFixedInstanceOption).insert_one(BridgeFixedInstanceOption(fk_instance=fk_instance, fk_option=fk_option))

            db.commit()
