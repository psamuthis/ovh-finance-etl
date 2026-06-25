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
        
    # TODO changer le filtre: chercher un plan existant dans la période from-to au lieu de month_start-month_end
    def get_or_create(self, record: DimSavingsPlan, plan_start: datetime, plan_end: datetime) -> int:
        DimTimeFrom = aliased(DimTime)
        DimTimeTo = aliased(DimTime)

        existing_plan: Optional[DimSavingsPlan] = self.db.query(DimSavingsPlan)\
            .filter(DimSavingsPlan.plan_id==record.plan_id)\
            .join(DimTimeFrom, DimTimeFrom.id==DimSavingsPlan.fk_period_from)\
            .join(DimTimeTo, DimTimeTo.id==DimSavingsPlan.fk_period_to)\
            .filter(DimTimeFrom.timestamptz >= plan_start)\
            .filter(DimTimeTo.timestamptz < plan_end)\
            .first()

        if existing_plan is not None:
            return existing_plan.id

        return self.insert_one(record)
