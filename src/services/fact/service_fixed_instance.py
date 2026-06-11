from datetime import datetime, timezone

from models.dimension.dim_time import DimTime
from models.fact.fact_current_fixed_compute import FactCurrentFixedCompute
from services.db_service import DBService
from sqlalchemy.orm import Session


class ServiceFixedInstance(DBService):
    def __init__(self, db: Session):
        self.db: Session = db

    def get_or_create(self, record: FactCurrentFixedCompute) -> int:
        month_start: datetime = datetime.now(timezone.utc).replace(day=1, minute=0, second=0, microsecond=0)
        month_end: datetime = month_start.replace(month=month_start.month+1)

        existing_record: FactCurrentFixedCompute  = self.db.query(FactCurrentFixedCompute)\
            .filter(FactCurrentFixedCompute.instance_id==record.instance_id)\
            .join(DimTime, DimTime.id==FactCurrentFixedCompute.fk_created_at)\
            .filter(DimTime.timestamptz >= month_start)\
            .filter(DimTime.timestamptz < month_end)\
            .first()

        if existing_record is not None:
            return existing_record.id
        
        return self.insert_one(record)