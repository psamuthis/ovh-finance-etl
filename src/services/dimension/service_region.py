from typing import ClassVar, Optional
from typing_extensions import override

from sqlalchemy.orm import Session


from connector.postgres_connection import WarehouseSessionLocal
from models.dimension.dim_region import DimRegion
from services.db_service import DBService


class ServiceRegion(DBService[DimRegion]):
    _cache: ClassVar[dict[str, int]] = {}
    _cache_loaded: ClassVar[bool] = False

    def __init__(self, db: Session):
        super().__init__(db, DimRegion)

        if not ServiceRegion._cache_loaded:
            self._load_cache()

    def get_by_name(self, name: str) -> Optional["DimRegion"]:
        return self.db.query(DimRegion).filter_by(name=name).first()

    @override
    def insert_one(self, record: DimRegion) -> int:
        self.db.add(record)
        self.db.flush()
        ServiceRegion._cache[record.name] = record.id
        return record.id

    def get_or_create(self, region_name: str) -> int:
        self._load_cache()

        if region_name in ServiceRegion._cache:
            return self._cache[region_name]

        return self.insert_one(DimRegion(name=region_name))

    def _load_cache(self) -> None:
        if ServiceRegion._cache_loaded:
            return

        regions: list[DimRegion] = self.get_all()
        ServiceRegion._cache = {region.name: region.id for region in regions}
        ServiceRegion._cache_loaded = True

    def _refresh_cache(self) -> None:
        ServiceRegion._cache_loaded = False
        self._load_cache()
