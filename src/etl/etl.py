from datetime import datetime
from time import sleep
from typing import Any

from connector.db_connection import WarehouseSessionLocal
from etl.etl_fixed_instance import ETLFixedInstance
from etl.etl_savings_plan import ETLSavingsPlan
from etl.etl_storage import ETLStorage
from etl.etl_volume import ETLVolume
from models.raw.current_usage_raw import CurrentUsageRaw
from etl.etl_dynamic_instance import ETLDynamicInstance
from services.dimension.service_tenant import ServiceTenant


class ETL:

    def __init__(self, raw_record: CurrentUsageRaw):
        self.service_id: str = raw_record.service_id
        self.period_from: datetime = raw_record.period_from
        self.period_to: datetime = raw_record.period_to
        self.archived_at: datetime = raw_record.call_timestamp
        self.json: dict[str, Any] = raw_record.full_response_json

        self.volume: ETLVolume = ETLVolume(self.service_id, self.period_from, self.period_to, self.archived_at)
        self.dynamic_instances: ETLDynamicInstance = ETLDynamicInstance(self.service_id, self.period_from, self.period_to, self.archived_at)
        self.fixed_instances: ETLFixedInstance = ETLFixedInstance(self.service_id, self.period_from, self.period_to, self.archived_at)
        self.savings_plans: ETLSavingsPlan = ETLSavingsPlan(self.service_id, self.archived_at)
        self.storage: ETLStorage = ETLStorage(self.service_id, self.period_from, self.period_to, self.archived_at)

    def run(self):
        print(f"Starting ETL process...")
        print(f"\t{self.service_id}")
        print(f"\t{self.period_from}")
        print(f"\t{self.period_to}")
        print(f"\t{self.archived_at}")

        with WarehouseSessionLocal() as db:
            ServiceTenant(db).get_or_create(self.service_id)

        print(f"Volumes...")
        self.volume.extract_data(self.json["hourlyUsage"]["volume"])
        self.volume.load_data()
        print(f"Volumes processed.")

        print(f"Dynamic Instances...")
        self.dynamic_instances.extract_data(self.json["hourlyUsage"]["instance"], self.json["hourlyUsage"]["instanceOption"])
        self.dynamic_instances.load_data()
        print(f"Dynamic Instances processed.")

        print(f"Fixed Instances...")
        self.fixed_instances.extract_data(self.json["monthlyUsage"]["instance"], self.json["monthlyUsage"]["instanceOption"])
        self.fixed_instances.load_data()
        print(f"Fixed Instances processed.")

        print(f"Savings Plans...")
        self.savings_plans.extract_data(self.json["monthlyUsage"]["savingsPlan"], self.json["hourlyUsage"]["instance"])
        self.savings_plans.load_data()
        print(f"Savings Plans processed.")

        # print(f"Managed Kubernetes Service...")
        # TODO (whenever ovh fixes their api)
        # print(f"Managed Kubernetes Service processed.")

        print(f"Storage...")
        self.storage.extract_data(self.json["hourlyUsage"]["storage"])
        self.storage.load_data()
        print(f"Storage processed.")

        print(f"ETL process done.")
