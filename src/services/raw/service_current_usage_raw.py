from typing import Optional

from models.raw.current_usage_raw import CurrentUsageRaw
from services.db_service import DBService
from sqlalchemy.orm import Session


class ServiceUsageRaw(DBService):
    def __init__(self, db: Session):
        super().__init__(db, ServiceUsageRaw)

    def retrieve_latest_data(self) -> list[CurrentUsageRaw]:
        return (
            self.db.query(CurrentUsageRaw)
            .distinct(CurrentUsageRaw.service_id)
            .order_by(CurrentUsageRaw.service_id, CurrentUsageRaw.created_at.desc())
            .all()
        )
    