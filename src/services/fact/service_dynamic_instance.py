from datetime import datetime, timezone
from decimal import Decimal
from tkinter import W

from models.dimension.dim_time import DimTime
from models.fact.fact_current_dynamic_compute import FactCurrentDynamicCompute
from sqlalchemy import between, func
from sqlalchemy.orm import Session, aliased



class ServiceDynamicInstance:
    def __init__(self, db: Session):
        self.db: Session = db

    def get_non_cumulative_cost(self, instance_id: str, current_price: Decimal) -> Decimal:
        current_month: datetime = datetime.now(timezone.utc)
        DimTimeFrom = aliased(DimTime)
        DimTimeTo = aliased(DimTime)

        previous_sum: Decimal = Decimal(0)
        previous_sum = self.db.query(func.sum(FactCurrentDynamicCompute.usage_price))\
            .filter(FactCurrentDynamicCompute.instance_id==instance_id)\
            .join(DimTimeFrom, FactCurrentDynamicCompute.fk_period_from == DimTimeFrom.id)\
            .join(DimTimeTo, FactCurrentDynamicCompute.fk_period_to == DimTimeTo.id)\
            .filter(DimTimeFrom.timestamptz <= current_month)\
            .filter(DimTimeTo.timestamptz >= current_month)\
            .scalar()

        if previous_sum is None:
            return round(current_price, 5)

        return round(current_price - previous_sum, 5)

    def get_non_cumulative_value(self, instance_id: str, current_value: int) -> int:
        current_month: datetime = datetime.now(timezone.utc)
        DimTimeFrom = aliased(DimTime)
        DimTimeTo = aliased(DimTime)

        previous_sum: int = self.db.query(func.sum(FactCurrentDynamicCompute.usage_value))\
            .filter(FactCurrentDynamicCompute.instance_id==instance_id)\
            .join(DimTimeFrom, FactCurrentDynamicCompute.fk_period_from == DimTimeFrom.id)\
            .join(DimTimeTo, FactCurrentDynamicCompute.fk_period_to == DimTimeTo.id)\
            .filter(DimTimeFrom.timestamptz <= current_month)\
            .filter(DimTimeTo.timestamptz >= current_month)\
            .scalar()

        if previous_sum is None:
            return current_value

        return current_value - previous_sum
            
