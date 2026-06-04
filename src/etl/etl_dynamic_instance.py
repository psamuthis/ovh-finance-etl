from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from etl.etl_interface import ETLInterface
from etl.shared import Quantity
from etl.instance_datatypes import (
    DynamicInstance,
    DynamicInstanceDetails,
    FixedInstance,
    InstanceOptionDetails,
)
from connector.postgres_connection import WarehouseSessionLocal
from services.dimension.service_deployment_mode import ServiceDeploymentMode
from services.dimension.service_region import ServiceRegion
from services.dimension.service_tenant import ServiceTenant
from services.dimension.service_time import ServiceTime
from services.dimension.service_unit import ServiceUnit
from models.dimension.dim_kubernetes import DimKubernetes
from services.dimension.db_service_kubernetes import DBServiceKubernetes
from models.dimension.dim_time import DimTime
from models.fact.fact_current_dynamic_compute import FactCurrentDynamicCompute
from models.fact.fact_current_instance_option import FactCurrentInstanceOption
from services.db_service import DBService
from services.fact.service_instance import ServiceInstance
from models.bridge.bridge_dynamic_instance_options import BridgeDynamicInstanceOption


class ETLDynamicInstance:
    def __init__(self, service_id: str, period_from: datetime, period_to: datetime):
        self.service_id = service_id
        self.period_from = period_from
        self.period_to = period_to
        self.dynamic_instances: list[DynamicInstance] = []
        self.instance_options: dict[str, InstanceOptionDetails] = {}

    def extract_data(
        self,
        instance_data: list[dict[str, Any]],
        instance_option_data: list[dict[str, Any]],
    ) -> None:
        self.transform_instance(instance_data)

        for option_group in instance_option_data:
            for details in option_group["details"]:
                self.instance_options[details["instanceId"]] = self.transform_option_details(
                    details
                )

    def load_data(self) -> None:
        with WarehouseSessionLocal() as db:
            self.load_dynamic_instances(db)

    def transform_instance(self, instance_data) -> None:
        for instance_group in instance_data:

            if "savingsPlanIds" in instance_group:
                continue

            dynamic_instance = DynamicInstance(
                deployment_mode=instance_group["deploymentMode"],
                flavor=instance_group["reference"],
                region=instance_group["region"],
            )

            for details_entry in instance_group["details"]:
                dynamic_instance.details.append(
                    self.transform_dynamic_instance_details(details_entry)
                )

            self.dynamic_instances.append(dynamic_instance)

    def transform_dynamic_instance_details(self, details: dict[str, Any]) -> DynamicInstanceDetails:
        quantity: Quantity = Quantity(details["quantity"]["unit"], details["quantity"]["value"])
        return DynamicInstanceDetails(
            instance_id=details["instanceId"],
            quantity=quantity,
            resource_id=details["resourceId"],
            total_price=details["totalPrice"],
        )

    def transform_option_details(self, details: dict[str, Any]) -> InstanceOptionDetails:
        quantity: Quantity = Quantity(
            unit=details["quantity"]["unit"], value=details["quantity"]["value"]
        )

        return InstanceOptionDetails(
            instance_id=details["instanceId"],
            quantity=quantity,
            total_price=details["totalPrice"],
        )

    def load_dynamic_instances(self, db: Session) -> None:
        fk_tenant: int = ServiceTenant(db).get_or_create(self.service_id)
        fk_period_from: int = ServiceTime(db).get_or_create(self.period_from)
        fk_period_to: int = ServiceTime(db).get_or_create(self.period_to)

        for flavor in self.dynamic_instances:
            fk_dep_mode: int = ServiceDeploymentMode(db).get_or_create(flavor.deployment_mode)
            fk_region: int = ServiceRegion(db).get_or_create(flavor.region)

            for instance in flavor.details:
                fk_usage_unit: int = ServiceUnit(db).get_or_create(instance.quantity.unit)

                instance_record: FactCurrentDynamicCompute = FactCurrentDynamicCompute(
                    instance_id=instance.instance_id,
                    fk_period_from=fk_period_from,
                    fk_period_to=fk_period_to,
                    fk_created_at=ServiceTime(db).get_or_create(datetime.now(timezone.utc)),
                    fk_tenant=fk_tenant,
                    fk_region=fk_region,
                    fk_deployment_mode=fk_dep_mode,
                    fk_resource=None,
                    fk_usage_unit=fk_usage_unit,
                    usage_value=instance.quantity.value,
                    usage_price=instance.total_price,
                )

                fk_instance: int = DBService(db, FactCurrentDynamicCompute).insert_one(
                    instance_record
                )
                fk_option: Optional[int] = None
                if instance.instance_id in self.instance_options:
                    fk_option = DBService(db, FactCurrentInstanceOption).insert_one(
                        FactCurrentInstanceOption(
                            fk_unit=self.instance_options[instance.instance_id].quantity.unit,
                            value=self.instance_options[instance.instance_id].quantity.value,
                            price=self.instance_options[instance.instance_id].total_price,
                        )
                    )
                    DBService(db, BridgeDynamicInstanceOption).insert_one(
                        BridgeDynamicInstanceOption(fk_instance=fk_instance, fk_option=fk_option)
                    )

            db.commit()
