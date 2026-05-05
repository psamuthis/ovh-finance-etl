from typing import ClassVar, Optional

from sqlalchemy.orm import Session

from src.models.dimension.dim_unit import DimUnit


class ServiceUnit:
    _cache: ClassVar[dict[str, int]] = {}
    _cache_loaded: ClassVar[bool] = False

    def __init__(self, db: Session):
        self.db: Session = db

    def get_all(self) -> list[DimUnit]:
        return self.db.query(DimUnit).all()

    def get_by_name(self, name: str) -> Optional[DimUnit]:
        return self.db.query(DimUnit).filter_by(name=name).first()

    def insert_one(self, name: str) -> int:
        unit: DimUnit = DimUnit(name=name)
        self.db.add(unit)
        self.db.flush()
        ServiceUnit._cache[name] = unit.id
        return unit.id

    def get_or_create(self, unit_str: str) -> int:
        self._load_cache()

        if unit_str in ServiceUnit._cache:
            return ServiceUnit._cache[unit_str]

        new_id: int = self.insert_one(unit_str)
        ServiceUnit._cache[unit_str] = new_id
        return new_id

    def _load_cache(self) -> None:
        if self._cache_loaded:
            return

        units: list[DimUnit] = self.get_all()
        DimUnit._cache = {unit.unit: unit.id for unit in units}
        DimUnit._cache_loaded = True

    def _refresh_cache(self) -> None:
        ServiceUnit._cache_loaded = False
        self._load_cache()
