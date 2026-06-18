from enum import Enum

from etl.etl import ETL
from models.raw.current_usage_raw import CurrentUsageRaw
from connector.postgres_connection import RawSessionLocal, WarehouseSessionLocal
from services.raw.service_current_usage_raw import ServiceUsageRaw

from config import EXCLUDED_TENANTS

EXCLUDED_TENANT_IDS: set[str] = set(EXCLUDED_TENANTS.values())

with RawSessionLocal() as db:
    latest_records: list[CurrentUsageRaw] = ServiceUsageRaw(db).retrieve_latest_data()

if latest_records is None:
    raise ValueError("Latest raw record wasn't retrieved...")

for record in latest_records:
    if record.service_id in EXCLUDED_TENANT_IDS:
        continue

    ETL(record).run()
