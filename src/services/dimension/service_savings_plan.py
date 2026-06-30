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
        
    def get_or_create(self, record: DimSavingsPlan) -> int:

        existing_plan: Optional[DimSavingsPlan] = self.db.query(DimSavingsPlan)\
            .filter(DimSavingsPlan.plan_id==record.plan_id)\
            .first()

        if existing_plan is not None:
            return existing_plan.id

        return self.insert_one(record)
