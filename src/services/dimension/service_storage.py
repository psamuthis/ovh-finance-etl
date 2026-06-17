from datetime import datetime, timezone

from etl.etl_storage import StorageCost
from models.dimension.dim_storage import DimStorage
from models.dimension.dim_time import DimTime
from models.fact.fact_storage import FactCurrentStorage
from services.db_service import DBService
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased


class ServiceStorage(DBService):
    def __init__(self, db: Session):
        super().__init__(db, ServiceStorage)

    def get_non_cumulative_cost(self, storage_name: str, current_cost: StorageCost) -> StorageCost:
        current_month: datetime = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        DimTimeFrom = aliased(DimTime)
        DimTimeTo = aliased(DimTime)

        result = self.db.query(
            func.sum(FactCurrentStorage.in_bandwidth_price).label("in_cost"),
            func.sum(FactCurrentStorage.in_bandwidth_value).label("in_value"),
            func.sum(FactCurrentStorage.out_bandwdith_price).label("out_cost"),
            func.sum(FactCurrentStorage.out_bandwdith_value).label("out_value"),
            func.sum(FactCurrentStorage.in_internal_bandwidth_price).label("in_internal_cost"),
            func.sum(FactCurrentStorage.in_internal_bandwidth_value).label("in_internal_value"),
            func.sum(FactCurrentStorage.out_internal_bandwidth_price).label("out_internal_cost"),
            func.sum(FactCurrentStorage.out_internal_bandwidth_value).label("out_internal_value"),
            func.sum(FactCurrentStorage.retrieval_fees_price).label("retrieval_fees_cost"),
            func.sum(FactCurrentStorage.retrieval_fees_value).label("retrieval_fees_value"),
            )\
            .join(DimStorage, DimStorage.id==FactCurrentStorage.fk_storage)\
            .filter(DimStorage.name==storage_name)\
            .join(DimTimeFrom, DimTimeFrom.id==FactCurrentStorage.fk_period_from)\
            .join(DimTimeTo, DimTimeTo.id==FactCurrentStorage.fk_created_at)\
            .filter(DimTimeFrom.timestamptz >= current_month)\
            .filter(DimTimeTo.timestamptz < datetime.now(timezone.utc))\
            .first()

        if result is None:
            previous_cumulated: StorageCost = StorageCost()
        else:
            previous_cumulated: StorageCost = StorageCost(*result)

        return current_cost - previous_cumulated