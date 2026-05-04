from typing import Any

from models.dimension.dim_deployment_mode import DimDeploymentMode
from models.raw.current_usage_raw import CurrentUsageRaw
from connector.postgres_connection import RawSessionLocal, WarehouseSessionLocal
from src.etl.etl_volume import ETLVolume

with RawSessionLocal() as db:
    latest_record = CurrentUsageRaw.retrieve_latest_record(db)

if latest_record is None:
    exit(0)

raw_json: dict[str, Any] = latest_record.full_response_json

"""
For each tenant handle:
    - instance (network + options)
    - storage
    - volume
    - rancher
    - mks
    - savings_plan
"""

structured_volumes: ETLVolume = ETLVolume(latest_record.service_id)
structured_volumes.extract_data(raw_json["hourlyUsage"]["volume"])
print(structured_volumes.volumes[0])
