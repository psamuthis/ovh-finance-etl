from sqlalchemy.orm import Session

from models.dimension.dim_volume import DimVolume
from models.fact.fact_volume import FactVolume
from services.dim_db_service import DimDBService


class ServiceDimVolume(DimDBService[DimVolume]):
    def __init__(self, db: Session):
        super().__init__(db, DimVolume)
