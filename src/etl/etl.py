from datetime import datetime
import json
from typing import Any

from etl.etl_fixed_instance import ETLFixedInstance
from etl.etl_volume import ETLVolume
from models.raw.current_usage_raw import CurrentUsageRaw
from etl.etl_dynamic_instance import ETLDynamicInstance


class ETL:

    def __init__(self, raw_record: CurrentUsageRaw):
        self.service_id: str = raw_record.service_id
        self.period_from: datetime = raw_record.period_from
        self.period_to: datetime = raw_record.period_to
        self.json: dict[str, Any] = raw_record.full_response_json

        self.volume: ETLVolume = ETLVolume(self.service_id, self.period_from, self.period_to)
        self.dynamic_instances: ETLDynamicInstance = ETLDynamicInstance(
            self.service_id, self.period_from, self.period_to
        )
        self.fixed_instances: ETLFixedInstance = ETLFixedInstance(
            self.service_id, self.period_from, self.period_to
        )

    def run(self):
        print(f"Starting ETL process...")
        print(f"\t{self.service_id}")
        print(f"\t{self.period_from}")
        print(f"\t{self.period_to}")

        with open("run_raw_data.json", "w") as file:
            json.dump(self.json, file, indent=4)

        # print(f"Volumes...")
        # self.volume.extract_data(self.json["hourlyUsage"]["volume"])
        # self.volume.load_data()
        # print(f"Volumes processed.")

        print(f"Dynamic Instances...")
        self.dynamic_instances.extract_data(
            self.json["hourlyUsage"]["instance"],
            self.json["hourlyUsage"]["instanceOption"],
        )
        self.dynamic_instances.load_data()
        print(f"Dynamic Instances processed.")

        print(f"Fixed Instances...")
        self.fixed_instances.extract_data(self.json["monthlyUsage"]["instance"], self.json["monthlyUsage"]["instanceOption"])
        self.fixed_instances.load_data()
        print(f"Fixed Instances processed.")

        print(f"ETL process done.")
