from typing import ClassVar, Optional
from typing_extensions import override

from sqlalchemy.orm import Session

from models.dimension.dim_unit import DimUnit
from services.db_service import DBService


class ServiceUnit(DBService[DimUnit]):
    _cache: ClassVar[dict[str, int]] = {}
    _cache_loaded: ClassVar[bool] = False

    def __init__(self, db: Session):
        super().__init__(db, DimUnit)

        if not ServiceUnit._cache_loaded:
            self._load_cache()

    def get_by_unit(self, unit: str) -> Optional[DimUnit]:
        return self.db.query(DimUnit).filter_by(unit=unit).first()

    @override
    def insert_one(self, record: DimUnit) -> int:
        self.db.add(record)
        self.db.flush()
        ServiceUnit._cache[record.unit] = record.id
        return record.id

    def get_or_create(self, unit_str: str) -> int:
        self._load_cache()

        if unit_str in ServiceUnit._cache:
            return ServiceUnit._cache[unit_str]

        return self.insert_one(DimUnit(unit=unit_str))

    def _load_cache(self) -> None:
        if ServiceUnit._cache_loaded:
            return

        units: list[DimUnit] = self.get_all()
        ServiceUnit._cache = {unit.unit: unit.id for unit in units}
        ServiceUnit._cache_loaded = True

    def _refresh_cache(self) -> None:
        ServiceUnit._cache_loaded = False
        self._load_cache()
