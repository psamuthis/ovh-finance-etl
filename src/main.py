from etl.etl import ETL
from models.raw.current_usage_raw import CurrentUsageRaw
from connector.postgres_connection import RawSessionLocal, WarehouseSessionLocal
from services.raw.service_current_usage_raw import ServiceUsageRaw

with RawSessionLocal() as db:
    latest_records: list[CurrentUsageRaw] = ServiceUsageRaw(db).retrieve_latest_data()

if latest_records is None:
    raise ValueError("Latest raw record wasn't retrieved...")

for record in latest_records:
    ETL(record).run()
