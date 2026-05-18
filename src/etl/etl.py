from datetime import datetime
from typing import Any

from etl.etl_volume import ETLVolume
from models.raw.current_usage_raw import CurrentUsageRaw


class ETL:

    def __init__(self, raw_record: CurrentUsageRaw):
        self.service_id: str = raw_record.service_id
        self.period_from: datetime = raw_record.period_from
        self.period_to: datetime = raw_record.period_to
        self.json: dict[str, Any] = raw_record.full_response_json
        self.volume: ETLVolume = ETLVolume(
            self.service_id, self.period_from, self.period_to
        )

    def run(self):
        print(f"Starting ETL process...")
        print(f"\t{self.service_id}")
        print(f"\t{self.period_from}")
        print(f"\t{self.period_to}")
        # print(f"\t{self.json}")
        # print(f'\t{self.json["hourlyUsage"]["volume"]}')

        self.volume.extract_data(self.json["hourlyUsage"]["volume"])
        self.volume.load_data()
        print(f"ETL process done.")
