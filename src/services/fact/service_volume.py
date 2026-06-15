from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased

from models.dimension.dim_time import DimTime
from models.fact.fact_volume import FactVolume
from models.dimension.dim_volume import DimVolume


class ServiceFactVolume:
    def __init__(self, db: Session):
        self.db: Session = db

    def get_non_cumulative_cost(self, volume_uuid: str, current_price: Decimal) -> Decimal:
        month_start: datetime = datetime.now(timezone.utc).replace(day=1, minute=0, second=0, microsecond=0)

        previous_cumulated_price: Decimal = self.db.query(func.sum(FactVolume.price))\
            .join(DimVolume, DimVolume.id == FactVolume.fk_volume)\
            .filter(DimVolume.volume_uuid == volume_uuid)\
            .join(DimTime, DimTime.id == FactVolume.fk_created_at)\
            .filter(DimTime.timestamptz >= month_start)\
            .filter(DimTime.timestamptz < datetime.now(timezone.utc))\
            .scalar() or Decimal(0)

        return current_price - previous_cumulated_price

    def get_non_cumulative_value(self, volume_uuid: str, current_value: Decimal) -> Decimal:
        month_start: datetime = datetime.now(timezone.utc).replace(day=1, minute=0, second=0, microsecond=0)

        previous_cumulated_value: Decimal = self.db.query(func.sum(FactVolume.value))\
            .join(DimVolume, DimVolume.id == FactVolume.fk_volume)\
            .filter(DimVolume.volume_uuid == volume_uuid)\
            .join(DimTime, DimTime.id == FactVolume.fk_created_at)\
            .filter(DimTime.timestamptz >= month_start)\
            .filter(DimTime.timestamptz < datetime.now(timezone.utc))\
            .scalar() or Decimal(0)

        return current_value - previous_cumulated_value
