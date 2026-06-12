from datetime import datetime, timezone
from decimal import Decimal

from models.dimension.dim_time import DimTime
from models.fact.fact_current_dynamic_compute import FactCurrentDynamicCompute
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased



class ServiceDynamicInstance:
    def __init__(self, db: Session):
        self.db: Session = db

    def get_non_cumulative_cost(self, instance_id: str, current_price: Decimal) -> Decimal:
        month_start: datetime = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        DimTimeFrom = aliased(DimTime)
        DimTimeTo = aliased(DimTime)

        previous_sum = self.db.query(func.sum(FactCurrentDynamicCompute.usage_price))\
            .filter(FactCurrentDynamicCompute.instance_id==instance_id)\
            .join(DimTimeFrom, FactCurrentDynamicCompute.fk_period_from == DimTimeFrom.id)\
            .join(DimTimeTo, FactCurrentDynamicCompute.fk_period_to == DimTimeTo.id)\
            .filter(DimTimeTo.timestamptz >= month_start)\
            .filter(DimTimeFrom.timestamptz <= datetime.now(timezone.utc))\
            .scalar() or Decimal(0)

        return round(current_price - previous_sum, 5)

    def get_non_cumulative_value(self, instance_id: str, current_value: Decimal) -> Decimal:
        month_start: datetime = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        DimTimeFrom = aliased(DimTime)
        DimTimeTo = aliased(DimTime)

        previous_sum: Decimal = self.db.query(func.sum(FactCurrentDynamicCompute.usage_value))\
            .filter(FactCurrentDynamicCompute.instance_id==instance_id)\
            .join(DimTimeFrom, FactCurrentDynamicCompute.fk_period_from == DimTimeFrom.id)\
            .join(DimTimeTo, FactCurrentDynamicCompute.fk_period_to == DimTimeTo.id)\
            .filter(DimTimeTo.timestamptz >= month_start)\
            .filter(DimTimeFrom.timestamptz <= datetime.now(timezone.utc))\
            .scalar() or Decimal(0)

        return current_value - previous_sum
            