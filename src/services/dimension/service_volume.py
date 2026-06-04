from sqlalchemy.orm import Session

from models.dimension.dim_volume import DimVolume
from models.fact.fact_volume import FactVolume
from services.db_service import DBService


class ServiceDimVolume(DBService[DimVolume]):
    def __init__(self, db: Session):
        super().__init__(db, DimVolume)
