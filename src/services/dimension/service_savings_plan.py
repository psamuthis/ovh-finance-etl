from datetime import datetime, timezone
from typing import Optional

from models.dimension.dim_time import DimTime
from models.dimension.dim_savings_plan import DimSavingsPlan
from services.db_service import DBService
from sqlalchemy.orm import Session, aliased
from dateutil.relativedelta import relativedelta


class ServiceSavingsPlan(DBService):
    def __init__(self, db: Session):
        self.db: Session = db
        
    def get_or_create(self, record: DimSavingsPlan, archived_at: datetime) -> int:
        month_start: datetime = archived_at.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end: datetime = month_start + relativedelta(months=1)

        DimTimeFrom = aliased(DimTime)
        DimTimeTo = aliased(DimTime)

        existing_plan: Optional[DimSavingsPlan] = self.db.query(DimSavingsPlan)\
            .filter(DimSavingsPlan.plan_id==record.plan_id)\
            .join(DimTimeFrom, DimTimeFrom.id==DimSavingsPlan.fk_period_from)\
            .join(DimTimeTo, DimTimeTo.id==DimSavingsPlan.fk_period_to)\
            .filter(DimTimeFrom.timestamptz >= month_start)\
            .filter(DimTimeTo.timestamptz < month_end)\
            .first()

        if existing_plan is not None:
            return existing_plan.id

        return self.insert_one(record)
