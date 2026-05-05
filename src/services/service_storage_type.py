from typing import ClassVar

from sqlalchemy.orm import Session

from models.dimension.dim_storage_type import DimStorageType


class ServiceStorageType:
    _cache: ClassVar[dict[str, int]] = {}
    _cache_loaded: ClassVar[bool] = False

    def __init__(self, db: Session):
        self.db = db

        if not ServiceStorageType._cache_loaded:
            self._load_cache()

    def get_all(self) -> list[DimStorageType]:
        return self.db.query(DimStorageType).all()

    def insert_one(self, type: str) -> int:
        storage_type: DimStorageType = DimStorageType(type=type)
        self.db.add(storage_type)
        self.db.flush()
        ServiceStorageType._cache[type] = storage_type.id
        return storage_type.id

    def get_or_create(self, type: str) -> int:
        self._load_cache()

        if type in ServiceStorageType._cache:
            return ServiceStorageType._cache[type]

        new_id: int = self.insert_one(type)
        ServiceStorageType._cache[type] = new_id
        return new_id

    def _load_cache(self) -> None:
        if ServiceStorageType._cache_loaded:
            return

        storage_types: list[DimStorageType] = self.get_all()
        ServiceStorageType._cache = {type.type: type.id for type in storage_types}
        ServiceStorageType._cache_loaded = True

    def _refresh_cache(self) -> None:
        ServiceStorageType._cache_loaded = False
        self._load_cache()
