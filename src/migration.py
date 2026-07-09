from datetime import datetime

from config import EXCLUDED_TENANTS
from connector.db_connection import FinopsSessionLocal
from etl.migration.etl_dynamic_instance import ETLDynamicInstance
from etl.migration.etl_fixed_instance import ETLFixedInstance
from etl.migration.etl_storage import ETLStorage
from etl.migration.etl_volume import ETLVolume
from models.finops.consomption_history import ConsomptionHistory
from services.dimension.api_service_kubernetes import APIServiceKubernetes

FROM: int = 0
TO: int = 1
MIGRATE_FROM: datetime = datetime(year=2025, month=7, day=1)
MIGRATE_TO: datetime = datetime(year=2026, month=6, day=1)
PROJECT_IDS: list[str] = APIServiceKubernetes.list_services()
EXCLUDED_TENANT_IDS: set[str] = set(EXCLUDED_TENANTS.values())

with FinopsSessionLocal() as db:
    ALL_PERIODS = db.query(ConsomptionHistory._from, ConsomptionHistory._to).distinct()\
        .where(ConsomptionHistory._from >= MIGRATE_FROM)\
        .where(ConsomptionHistory._from < MIGRATE_TO)\
        .all()

    for period in ALL_PERIODS:
        print(f"from:{period[FROM]} - to:{period[TO]}")

        for project_id in PROJECT_IDS:
            
            if project_id in EXCLUDED_TENANT_IDS:
                continue

            print(f"\t tenant:{project_id}")

            dynamic_instances: list[ConsomptionHistory] = db.query(ConsomptionHistory)\
                .where(ConsomptionHistory._from == period[FROM])\
                .where(ConsomptionHistory.service_name == project_id)\
                .where(ConsomptionHistory.type == 'instance')\
                .where(ConsomptionHistory.cost_type == 'hourlyUsage')\
                .all()
            ETLDynamicInstance(project_id, period[FROM], period[TO]).load_data(dynamic_instances)

            fixed_instances: list[ConsomptionHistory] = db.query(ConsomptionHistory)\
                .where(ConsomptionHistory._from == period[FROM])\
                .where(ConsomptionHistory.service_name == project_id)\
                .where(ConsomptionHistory.type == 'instance')\
                .where(ConsomptionHistory.cost_type == 'monthlyUsage')\
                .all()
            ETLFixedInstance(project_id, period[FROM], period[TO]).load_data(fixed_instances)
            
            storage: list[ConsomptionHistory] = db.query(ConsomptionHistory)\
                .where(ConsomptionHistory._from == period[FROM])\
                .where(ConsomptionHistory.service_name == project_id)\
                .where(ConsomptionHistory.type == 'storage')\
                .all()
            ETLStorage(project_id, period[FROM], period[TO]).load_data(storage)

            volumes: list[ConsomptionHistory] = db.query(ConsomptionHistory)\
                .where(ConsomptionHistory._from == period[FROM])\
                .where(ConsomptionHistory.service_name == project_id)\
                .where(ConsomptionHistory.type == 'volume')\
                .all()
            ETLVolume(project_id, period[FROM], period[TO]).load_data(volumes)