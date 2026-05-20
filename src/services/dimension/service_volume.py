from sqlalchemy.orm import Session

from models.dimension.dim_volume import DimVolume
from models.fact.fact_volume import FactVolume
from src.services.dimension.dim_db_service import DIMDBService


class ServiceDimVolume(DIMDBService[DimVolume]):
    def __init__(self, db: Session):
        super().__init__(db, DimVolume)


class ServiceFactVolume(DIMDBService[FactVolume]):
    def __init__(self, db: Session):
        super().__init__(db, FactVolume)
