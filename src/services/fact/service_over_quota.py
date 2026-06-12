from datetime import datetime, timezone
from decimal import Decimal

from models.dimension.dim_time import DimTime
from models.fact.fact_savings_plan_over_quota import FactSavingsPlanOverQuota
from services.db_service import DBService
from sqlalchemy import func
from sqlalchemy.orm import Session

OVER_QUOTA_TOK: str = r".over-quota"

class ServiceOverQuota(DBService):
    def __init__(self, db: Session):
        self.db: Session = db

    def get_non_cumulative_cost(self, flavor: str, current_price: Decimal) -> Decimal:
        month_start: datetime = datetime.now(timezone.utc)

        previous_cumulated_cost: Decimal = self.db.query(func.sum(FactSavingsPlanOverQuota.price))\
            .filter(FactSavingsPlanOverQuota.flavor==flavor)\
            .join(DimTime, DimTime.id==FactSavingsPlanOverQuota.fk_created_at)\
            .filter(DimTime.timestamptz >= month_start)\
            .filter(DimTime.timestamptz < datetime.now(timezone.utc))\
            .scalar() or Decimal(0)

        return current_price - previous_cumulated_cost

    def get_non_cumulative_value(self, flavor: str, current_value: Decimal) -> Decimal:
        month_start: datetime = datetime.now(timezone.utc)

        previous_cumulated_value: Decimal = self.db.query(func.sum(FactSavingsPlanOverQuota.value))\
            .filter(FactSavingsPlanOverQuota.flavor == flavor)\
            .join(DimTime, DimTime.id == FactSavingsPlanOverQuota.fk_created_at)\
            .filter(DimTime.timestamptz >= month_start)\
            .filter(DimTime.timestamptz < datetime.now(timezone.utc))\
            .scalar() or Decimal(0)

        return current_value - previous_cumulated_value
