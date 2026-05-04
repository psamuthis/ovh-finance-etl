from typing import ClassVar, Optional

from sqlalchemy import (
    BigInteger,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class DimRegion(DeclarativeBase):
    __tablename__ = "dim_region"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String)

    _cache: ClassVar[dict[str, int]] = {}
    _cache_loaded: ClassVar[bool] = False

    @staticmethod
    def get_all(db: Session) -> list["DimRegion"]:
        return db.query(DimRegion).all()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional["DimRegion"]:
        return db.query(DimRegion).filter_by(name=name).first()

    @staticmethod
    def insert_one(db: Session, name: str) -> int:
        region: DimRegion = DimRegion(name=name)
        db.add(region)
        db.flush()
        DimRegion._cache[name] = region.id
        return region.id

    @staticmethod
    def get_or_create(db: Session, region_name: str) -> int:
        DimRegion._load_cache(db)

        if region_name in DimRegion._cache:
            return DimRegion._cache[region_name]

        new_id: int = DimRegion.insert_one(db, region_name)
        DimRegion._cache[region_name] = new_id
        return new_id

    @staticmethod
    def _load_cache(db: Session) -> None:
        if DimRegion._cache_loaded:
            return

        regions: list[DimRegion] = DimRegion.get_all(db)
        DimRegion._cache = {region.name: region.id for region in regions}
        DimRegion._cache_loaded = True

    @staticmethod
    def _refresh_cache(db: Session) -> None:
        DimRegion._cache_loaded = False
        DimRegion._load_cache(db)
