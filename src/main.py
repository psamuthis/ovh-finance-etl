from typing import Any

from models.dimension.dim_deployment_mode import DimDeploymentMode
from models.raw.current_usage_raw import CurrentUsageRaw
from connector.postgres_connection import RawSessionLocal, WarehouseSessionLocal
from etl.etl import ETL
from etl.etl_volume import ETLVolume

with RawSessionLocal() as db:
    latest_record: CurrentUsageRaw | None = CurrentUsageRaw.retrieve_latest_record(db)

if latest_record is None:
    raise ValueError("Latest raw record wasn't retrieved...")

"""
For each tenant handle:
    - instance (network + options)
    - storage
    - volume
    - rancher
    - mks
    - savings_plan
"""

ETL(latest_record).run()
