import argparse
from datetime import datetime
from enum import Enum

from etl.etl import ETL
from models.raw.current_usage_raw import CurrentUsageRaw
from connector.db_connection import RawSessionLocal, WarehouseSessionLocal
from services.raw.service_current_usage_raw import ServiceUsageRaw

from config import EXCLUDED_TENANTS

EXCLUDED_TENANT_IDS: set[str] = set(EXCLUDED_TENANTS.values())

parser = argparse.ArgumentParser()
parser.add_argument("start_date", nargs="?", default=None, help="start date format YYYY-MM-DD format")
parser.add_argument("end_date", nargs="?", default=None, help="start date format YYYY-MM-DD format")
args = parser.parse_args()

if args.start_date:
    start_period: datetime = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_period: datetime = datetime.now()

    if args.end_date:
        end_period = datetime.strptime(args.end_date, "%Y-%m-%d")

    with RawSessionLocal() as db:
        records: list[CurrentUsageRaw] = ServiceUsageRaw(db).retrieve_data_between(start_period, end_period)

    if records is None:
        raise ValueError("No records found in interval.")

    print(f"Extracting data from {start_period} to {end_period}.")
    for record in records:
        if record.service_id in EXCLUDED_TENANT_IDS:
            continue

        ETL(record).run()

else:
    with RawSessionLocal() as db:
        latest_records: list[CurrentUsageRaw] = ServiceUsageRaw(db).retrieve_latest_data()

    if latest_records is None:
        raise ValueError("Latest raw record wasn't retrieved...")

    print(f"Pulling latest records.")
    for record in latest_records:
        if record.service_id in EXCLUDED_TENANT_IDS:
            continue

        ETL(record).run()
