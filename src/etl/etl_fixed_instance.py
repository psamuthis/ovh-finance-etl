from datetime import datetime, timezone
from typing import Any

from connector.postgres_connection import WarehouseSessionLocal
from etl.etl_interface import ETLInterface
from etl.instance_datatypes import FixedInstance, FixedInstanceOption
from etl.shared import Quantity
from models.bridge.bridge_dynamic_instance_options import BridgeInstanceOption
from models.dimension.dim_deployment_mode import DimDeploymentMode
from models.fact.fact_current_fixed_compute import FactCurrentFixedCompute
from models.fact.fact_fixed_instance_option import FactFixedInstanceOption
from services.db_service import DBService
from services.dimension.service_deployment_mode import ServiceDeploymentMode
from services.dimension.service_region import ServiceRegion
from services.dimension.service_time import ServiceTime
from services.fact.service_fixed_instance import ServiceFixedInstance
from sqlalchemy.orm import Session

class ETLFixedInstance:
    def __init__(self, service_id: str, period_from: datetime, period_to: datetime):
        self.service_id: str = service_id
        self.period_from: datetime = period_from
        self.period_to: datetime = period_to
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
                    detail["totalPrice"],
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
                        total_price=detail["totalPrice"],
                        flavor=flavor
                    )

    def load_data(self) -> None:
        with WarehouseSessionLocal() as db:

            for fixed_instance in self.fixed_instances:
                fk_deployment_mode: int = ServiceDeploymentMode(db).get_or_create(
                    fixed_instance.deployment_mode
                )
                fk_region: int = ServiceRegion(db).get_or_create(fixed_instance.region)
                fk_activation: int = ServiceTime(db).get_or_create(fixed_instance.activation_date)


                fk_instance: int = ServiceFixedInstance(db).get_or_create(
                    FactCurrentFixedCompute(
                        fk_deployment_mode=fk_deployment_mode,
                        fk_region=fk_region,
                        fk_activation=fk_activation,
                        fk_resource=None,
                        fk_created_at=ServiceTime(db).get_or_create(datetime.now(timezone.utc)),
                        instance_id=fixed_instance.instance_id,
                        price=fixed_instance.total_price,
                    )

                )

                if fixed_instance.instance_id in self.instance_option:
                    fk_option = DBService(db, FactFixedInstanceOption).insert_one(
                        FactFixedInstanceOption(
                            fk_deployment_mode=fk_deployment_mode,
                            fk_region=fk_region,
                            price=fixed_instance.total_price,
                            flavor=self.instance_option[fixed_instance.instance_id].flavor
                        )
                    )

                    DBService(db, BridgeInstanceOption).insert_one(
                        BridgeInstanceOption(fk_instance=fk_instance, fk_option=fk_option)
                    )

            db.commit()
