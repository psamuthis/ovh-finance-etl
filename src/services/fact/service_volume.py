from datetime import datetime
import decimal
from typing import Optional, Type, TypeVar, Generic
from sqlalchemy.orm import Mapped, Session, mapped_column

from models.base import Base
from models.dimension.dim_time import DimTime
from services.has_id_model import HasIdModel
from models.fact.fact_volume import FactVolume
from services.db_service import DBService
from models.dimension.dim_volume import DimVolume


class ServiceFactVolume:
    def __init__(self, db: Session):
        self.db: Session = db

    def cumulative_to_daily_cost(
        self, created_at: datetime, volume_uuid: str, current_price: decimal.Decimal
    ) -> decimal.Decimal:
        month_start: datetime = created_at.replace(day=1, minute=0, second=0, microsecond=0)

        resource_entries = (
            self.db.query(FactVolume)
            .join(DimTime, DimTime.id == FactVolume.fk_created_at)
            .join(DimVolume, DimVolume.id == FactVolume.fk_volume)
            .filter(DimVolume.volume_uuid == volume_uuid)
            .filter(DimTime.timestamptz < created_at)
            .filter(DimTime.timestamptz >= month_start)
        )

        cumulated_price: decimal.Decimal = decimal.Decimal(0.0)
        for entry in resource_entries:
            cumulated_price = cumulated_price + entry.price

        return current_price - cumulated_price

    def cumulative_to_daily_value(
        self, created_at: datetime, volume_uuid: str, current_value: int
    ) -> int:
        month_start: datetime = created_at.replace(day=1, minute=0, second=0, microsecond=0)

        resource_entries = (
            self.db.query(FactVolume)
            .join(DimTime, DimTime.id == FactVolume.fk_created_at)
            .join(DimVolume, DimVolume.id == FactVolume.fk_volume)
            .filter(DimVolume.volume_uuid == volume_uuid)
            .filter(DimTime.timestamptz < created_at)
            .filter(DimTime.timestamptz >= month_start)
        )

        cumulated_value: int = 0
        for entry in resource_entries:
            cumulated_value = cumulated_value + entry.value

        return current_value - cumulated_value
