from typing import Any

from etl.etl_volume import ETLVolume
from models.raw.current_usage_raw import CurrentUsageRaw


class ETL:

    def __init__(self, raw_record: CurrentUsageRaw):
        self.service_id: str = raw_record.service_id
        self.json: dict[str, Any] = raw_record.full_response_json
        self.volume: ETLVolume = ETLVolume(self.service_id)

    def run(self):
        self.volume.extract_data(self.json["hourlyUsage"]["volume"])
        self.volume.load_data()
