from typing import ClassVar, Optional

from sqlalchemy.orm import Session


from connector.postgres_connection import WarehouseSessionLocal
from models.dimension.dim_region import DimRegion


class ServiceRegion:
    _cache: ClassVar[dict[str, int]] = {}
    _cache_loaded: ClassVar[bool] = False

    def __init__(self, db: Session):
        self.db: Session = db

        if not ServiceRegion._cache_loaded:
            self._load_cache()

    def get_all(self) -> list[DimRegion]:
        return self.db.query(DimRegion).all()

    def get_by_name(self, name: str) -> Optional["DimRegion"]:
        return self.db.query(DimRegion).filter_by(name=name).first()

    def insert_one(self, name: str) -> int:
        region: DimRegion = DimRegion(name=name)
        self.db.add(region)
        self.db.flush()
        ServiceRegion._cache[name] = region.id
        return region.id

    def get_or_create(self, region_name: str) -> int:
        self._load_cache()

        if region_name in ServiceRegion._cache:
            return self._cache[region_name]

        new_id: int = self.insert_one(region_name)
        ServiceRegion._cache[region_name] = new_id
        return new_id

    def _load_cache(self) -> None:
        if ServiceRegion._cache_loaded:
            return

        regions: list[DimRegion] = self.get_all()
        ServiceRegion._cache = {region.name: region.id for region in regions}
        ServiceRegion._cache_loaded = True

    def _refresh_cache(self) -> None:
        ServiceRegion._cache_loaded = False
        self._load_cache()
