from typing import ClassVar, Optional

from sqlalchemy import (
    BigInteger,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class DimUnit(DeclarativeBase):
    __tablename__ = "dim_unit"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    unit: Mapped[str] = mapped_column(String)
    measure_type: Mapped[str] = mapped_column(String)
    standard_unit: Mapped[str] = mapped_column(String)

    _cache: ClassVar[dict[str, int]] = {}
    _cache_loaded: ClassVar[bool] = False

    @staticmethod
    def get_all(db: Session) -> list["DimUnit"]:
        return db.query(DimUnit).all()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional["DimUnit"]:
        return db.query(DimUnit).filter_by(name=name).first()

    @staticmethod
    def insert_one(db: Session, name: str) -> int:
        unit: DimUnit = DimUnit(name=name)
        db.add(unit)
        db.flush()
        DimUnit._cache[name] = unit.id
        return unit.id

    @staticmethod
    def get_or_create(db: Session, unit_str: str) -> int:
        DimUnit._load_cache(db)

        if unit_str in DimUnit._cache:
            return DimUnit._cache[unit_str]

        new_id: int = DimUnit.insert_one(db, unit_str)
        DimUnit._cache[unit_str] = new_id
        return new_id

    @staticmethod
    def _load_cache(db: Session) -> None:
        if DimUnit._cache_loaded:
            return

        units: list[DimUnit] = DimUnit.get_all(db)
        DimUnit._cache = {unit.unit: unit.id for unit in units}
        DimUnit._cache_loaded = True

    @staticmethod
    def _refresh_cache(db: Session) -> None:
        DimUnit._cache_loaded = False
        DimUnit._load_cache(db)
