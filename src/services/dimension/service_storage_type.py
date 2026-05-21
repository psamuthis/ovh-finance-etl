from typing import ClassVar
from typing_extensions import override

from sqlalchemy.orm import Session

from models.dimension.dim_storage_type import DimStorageType
from services.dim_db_service import DimDBService


class ServiceStorageType(DimDBService[DimStorageType]):
    _cache: ClassVar[dict[str, int]] = {}
    _cache_loaded: ClassVar[bool] = False

    def __init__(self, db: Session):
        super().__init__(db, DimStorageType)

        if not ServiceStorageType._cache_loaded:
            self._load_cache()

    @override
    def insert_one(self, record: DimStorageType) -> int:
        self.db.add(record)
        self.db.flush()
        ServiceStorageType._cache[record.type] = record.id
        return record.id

    def get_or_create(self, type: str) -> int:
        self._load_cache()

        if type in ServiceStorageType._cache:
            return ServiceStorageType._cache[type]

        return self.insert_one(DimStorageType(type=type))

    def _load_cache(self) -> None:
        if ServiceStorageType._cache_loaded:
            return

        storage_types: list[DimStorageType] = self.get_all()
        ServiceStorageType._cache = {type.type: type.id for type in storage_types}
        ServiceStorageType._cache_loaded = True

    def _refresh_cache(self) -> None:
        ServiceStorageType._cache_loaded = False
        self._load_cache()
